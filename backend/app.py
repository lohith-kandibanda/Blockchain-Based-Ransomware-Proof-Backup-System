from flask import Flask, request, jsonify, send_file
from encryption import encrypt_file, decrypt_file
from ipfs_client import upload_to_ipfs, download_from_ipfs
from contract_interaction import store_backup_on_chain, get_backup_from_chain
import os
import hashlib
from flask_cors import CORS

# -------------------------
# 🚀 Setup Flask App
# -------------------------
app = Flask(__name__)
CORS(app)  # Allow frontend → backend API requests (important)

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

        # Save uploaded file
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Encrypt file
        encrypted_path = encrypt_file(file_path, password)

        # Upload encrypted file to IPFS
        ipfs_hash = upload_to_ipfs(encrypted_path)

        # Generate unique File ID
        file_id = hashlib.sha256(file.filename.encode()).hexdigest()

        # Store on Blockchain, get Transaction Hash
        tx_hash = store_backup_on_chain(file_id, ipfs_hash)

        if not tx_hash:
            return jsonify({'error': 'Blockchain transaction failed'}), 500

        # ✅ Success Response
        return jsonify({
            "message": "File uploaded and backed up successfully!",
            "file_id": file_id,
            "ipfs_hash": ipfs_hash,
            "tx_hash": tx_hash
        }), 200

    except Exception as e:
        print(f"❌ Upload Error: {e}")
        return jsonify({'error': str(e)}), 500

# -------------------------
# 📥 Restore/Download API
# -------------------------
@app.route('/restore', methods=['POST'])
def restore_backup():
    try:
        file_id = request.form.get('file_id')
        version = request.form.get('version', default=1, type=int)
        password = request.form.get('password')

        if not file_id or not password:
            return jsonify({'error': 'file_id and password are required'}), 400

        # Fetch IPFS hash from Blockchain
        ipfs_hash, version_onchain, owner = get_backup_from_chain(file_id, version)

        if not ipfs_hash:
            return jsonify({'error': 'No backup found on blockchain'}), 404

        # Download encrypted file
        download_from_ipfs(ipfs_hash, output_folder=DOWNLOAD_FOLDER)

        encrypted_download_path = os.path.join(DOWNLOAD_FOLDER, ipfs_hash)
        decrypted_file_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}_v{version}_decrypted")

        # Decrypt file
        decrypt_file(encrypted_download_path, decrypted_file_path, password)

        # Send decrypted file to user
        return send_file(decrypted_file_path, as_attachment=True)

    except Exception as e:
        print(f"❌ Restore Error: {e}")
        return jsonify({'error': str(e)}), 500

# -------------------------
# 🏃 Run the Flask App
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)
