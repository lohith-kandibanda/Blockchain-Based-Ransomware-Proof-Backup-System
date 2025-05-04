from web3 import Web3
import json
import os
from dotenv import load_dotenv

# 🔧 Load environment variables
load_dotenv()

INFURA_URL = os.getenv("INFURA_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ACCOUNT_ADDRESS = os.getenv("ACCOUNT_ADDRESS")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# 🔧 Load Contract ABI
with open('../contracts/BackupContractABI.json', 'r') as abi_file:
    ABI = json.load(abi_file)

# 🔧 Connect to Blockchain
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

# 📤 Store backup (file_id + ipfs_hash) on Blockchain
def store_backup_on_chain(file_id, ipfs_hash):
    try:
        nonce = w3.eth.get_transaction_count(ACCOUNT_ADDRESS, "pending")  # Use pending
        base_gas_price = w3.eth.gas_price

        tx = contract.functions.storeBackup(file_id, ipfs_hash).build_transaction({
            'from': ACCOUNT_ADDRESS,
            'gas': 2000000,
            'gasPrice': int(base_gas_price * 1.1),  # Slight gas boost
            'nonce': nonce
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        print(f"✅ Backup stored successfully! TxHash: {tx_hash.hex()}")
        return tx_hash.hex()  # IMPORTANT: return TxHash to show in frontend

    except Exception as e:
        print(f"❌ Error storing backup: {e}")
        return None

# 📥 Fetch backup details (ipfs_hash, version, owner) from Blockchain
def get_backup_from_chain(file_id, version):
    try:
        backup_data = contract.functions.getBackup(file_id, version).call()
        ipfs_hash = backup_data[0]
        version_number = backup_data[1]
        owner = backup_data[2]
        return ipfs_hash, version_number, owner
    except Exception as e:
        print(f"❌ Error fetching backup: {str(e)}")
        return None, None, None
