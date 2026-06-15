import json
from web3 import Web3

# Connect to Ganache blockchain
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

# Contract address from deployment
contract_address = ''

# Load ABI from JSON file
with open('CertificateManager_abi.json', 'r') as f:
    abi = json.load(f)

# Create contract instance
contract = w3.eth.contract(address=contract_address, abi=abi)

# Your issuer account and private key (replace with your actual private key)
private_key = "0x49ec64ff745b2014a949dd28a2fef0efe15a4631622f115eb94612a5a128be43"
private_key = private_key.strip().replace('\n', '').replace('\r', '').replace(' ', '')
issuer_address = w3.eth.accounts[0]

# List of multiple certificates data
certificates = [
    ["CERT20251234", "Ankit Sharma", "190107002", "Bachelor of Technology", "Computer Science and Engineering", "2025", "ABC Engineering College", "XYZ Technical University", "8.96", "2025-07-15"],
    ["CERT20251235", "Rohit Singh", "190107003", "Bachelor of Engineering", "Mechanical Engineering", "2025", "DEF Engineering College", "XYZ Technical University", "8.75", "2025-07-15"],
    ["CERT20251236", "Priya Verma", "190107004", "Bachelor of Technology", "Electrical Engineering", "2025", "GHI Engineering College", "XYZ Technical University", "8.80", "2025-07-15"],
    ["CERT20251237", "Sneha Patel", "190107005", "Bachelor of Technology", "Civil Engineering", "2025", "JKL Engineering College", "XYZ Technical University", "8.60", "2025-07-15"],
    ["CERT20251238", "Aditya Kumar", "190107006", "Bachelor of Engineering", "Chemical Engineering", "2025", "MNO Engineering College", "XYZ Technical University", "8.85", "2025-07-15"]
]

# Loop to issue certificates one by one
for certificate_data in certificates:
    nonce = w3.eth.get_transaction_count(issuer_address)
    tx = contract.functions.issueCertificate(*certificate_data).build_transaction({
        'chainId': 1337,
        'gas': 3000000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': nonce,
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Certificate {certificate_data[0]} issued successfully! Tx hash: {tx_receipt.transactionHash.hex()}")
