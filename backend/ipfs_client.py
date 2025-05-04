import requests
import os

IPFS_API_URL = 'http://127.0.0.1:5001/api/v0'


def upload_to_ipfs(file_path):
    """
    Upload a file to IPFS and return its CID (Hash).
    """
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(f'{IPFS_API_URL}/add', files=files)

    if response.status_code == 200:
        res_json = response.json()
        return res_json['Hash']
    else:
        raise Exception(f"Failed to upload file to IPFS: {response.text}")


def download_from_ipfs(ipfs_hash, output_folder='.'):
    """
    Download a file from IPFS using its CID (Hash) and save to output_folder.
    """
    params = {'arg': ipfs_hash}
    response = requests.post(f'{IPFS_API_URL}/cat', params=params, stream=True)

    if response.status_code == 200:
        os.makedirs(output_folder, exist_ok=True)
        file_path = os.path.join(output_folder, ipfs_hash)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return file_path
    else:
        raise Exception(f"Failed to download file from IPFS: {response.text}")
