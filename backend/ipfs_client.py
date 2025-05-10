import os
import requests
from dotenv import load_dotenv

# 🔧 Load your Pinata JWT from .env
load_dotenv()
PINATA_JWT = os.getenv("PINATA_JWT")

PINATA_UPLOAD_URL = "https://api.pinata.cloud/pinning/pinFileToIPFS"
PINATA_GATEWAY_URL = "https://gateway.pinata.cloud/ipfs"

def upload_to_ipfs(file_path):
    """
    Upload a file to Pinata IPFS and return its CID.
    """
    try:
        with open(file_path, 'rb') as file:
            files = {'file': (os.path.basename(file_path), file)}
            headers = {'Authorization': PINATA_JWT}

            response = requests.post(PINATA_UPLOAD_URL, files=files, headers=headers)

            if response.status_code == 200:
                ipfs_hash = response.json()["IpfsHash"]
                print(f"✅ File pinned to Pinata: {ipfs_hash}")
                return ipfs_hash
            else:
                print(f"❌ Pinata Upload Failed: {response.text}")
                return None
    except Exception as e:
        print(f"❌ Error in upload_to_ipfs: {e}")
        return None


def download_from_ipfs(ipfs_hash, output_folder='.'):
    """
    Download a file from Pinata IPFS Gateway using its CID.
    """
    try:
        os.makedirs(output_folder, exist_ok=True)
        url = f"{PINATA_GATEWAY_URL}/{ipfs_hash}"
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            file_path = os.path.join(output_folder, ipfs_hash)
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ File downloaded from IPFS to: {file_path}")
            return file_path
        else:
            raise Exception(f"Failed to download file from IPFS: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Error in download_from_ipfs: {e}")
        return None
