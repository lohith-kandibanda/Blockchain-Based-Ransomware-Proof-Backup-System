from flask import Flask, request, jsonify, send_file
from encryption import encrypt_file, decrypt_file
from ipfs_client import upload_to_ipfs, download_from_ipfs
from contract_interaction import store_backup_on_chain, get_backup_from_chain
from web3 import Web3
import os
import hashlib
from flask_cors import CORS
import uuid

# -------------------------
# 🚀 Setup Flask App
# -------------------------
app = Flask(__name__)
CORS(app)

# -------------------------
# 📂 Create Folders
# -------------------------
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# -------------------------
# 📤 Upload and Backup API
# -------------------------
@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files or 'password' not in request.form:
            return jsonify({'error': 'File and password are required'}), 400

        file = request.files['file']
        password = request.form['password']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        encrypted_path = encrypt_file(file_path, password)
        ipfs_hash = upload_to_ipfs(encrypted_path)

        file_id = hashlib.sha256((file.filename + str(uuid.uuid4())).encode()).hexdigest()
        original_filename = file.filename  # ✅ Capture original filename

        # ✅ Compute hash from original file BEFORE encryption
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        file_hash = Web3.keccak(file_bytes)

        # 🔄 Now call store_backup_on_chain with the correct hash
        tx_hash = store_backup_on_chain(file_id, ipfs_hash, file_bytes=file_hash)

        if not tx_hash:
            return jsonify({'error': 'Blockchain transaction failed'}), 500

        return jsonify({
            "message": "File uploaded and backed up successfully!",
            "file_id": file_id,
            "ipfs_hash": ipfs_hash,
            "tx_hash": tx_hash,
            "filename": original_filename  # ✅ Return filename to frontend
        }), 200

    except Exception as e:
        print(f"❌ Upload Error: {e}")
        return jsonify({'error': str(e)}), 500

# -------------------------
# 📥 Restore/Download API (with integrity check)
# -------------------------
@app.route('/restore', methods=['POST'])
def restore_backup():
    try:
        file_id = request.form.get('file_id')
        version = int(request.form.get('version', 0))
        password = request.form.get('password')
        verify = request.form.get('verify', 'false').lower() == 'true'
        original_filename = request.form.get('filename', f"{file_id}_v{version}_restored.bin")

        if not file_id or not password:
            return jsonify({'error': 'file_id and password are required'}), 400

        ipfs_hash, version_onchain, owner, hash_onchain = get_backup_from_chain(file_id, version)

        if not ipfs_hash:
            return jsonify({'error': 'No backup found on blockchain'}), 404

        download_from_ipfs(ipfs_hash, output_folder=DOWNLOAD_FOLDER)

        encrypted_path = os.path.join(DOWNLOAD_FOLDER, ipfs_hash)
        decrypted_path = os.path.join(DOWNLOAD_FOLDER, original_filename)

        decrypt_file(encrypted_path, decrypted_path, password)

        if verify:
            with open(decrypted_path, 'rb') as f:
                file_bytes = f.read()
            local_hash = Web3.keccak(file_bytes).hex()
            expected_hash = hash_onchain.hex() if isinstance(hash_onchain, bytes) else str(hash_onchain)

            print("🔍 Expected hash:", expected_hash)
            print("🔍 Computed hash:", local_hash)

            if local_hash != expected_hash:
                return jsonify({
                    "error": "Integrity check failed!",
                    "expected_hash": expected_hash,
                    "actual_hash": local_hash
                }), 400

        # ✅ Send file with original filename
        return send_file(decrypted_path, as_attachment=True, download_name=original_filename)

    except Exception as e:
        print(f"❌ Restore Error: {e}")
        return jsonify({'error': str(e)}), 500

# -------------------------
# 🏃 Run the Flask App
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)
