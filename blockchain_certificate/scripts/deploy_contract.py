from web3 import Web3
from solcx import compile_standard, install_solc, set_solc_version
import json

# Connect to Ganache blockchain
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
print("Connected to Ganache:", w3.is_connected())

# Use your Ganache account address and private key
my_address = w3.eth.accounts[0]
private_key = ""  # Replace with your private key

# Read the updated Solidity contract code from the correct path
with open('CertificateManager.sol', 'r') as file:

    contract_source_code = file.read()

# Install and set Solidity compiler version
install_solc('0.8.0')
set_solc_version('0.8.0')

# Compile the contract
compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {"CertificateManager.sol": {"content": contract_source_code}},
    "settings": {
        "outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}
    }
})

# Extract bytecode and ABI
bytecode = compiled_sol['contracts']['CertificateManager.sol']['CertificateManager']['evm']['bytecode']['object']
abi = compiled_sol['contracts']['CertificateManager.sol']['CertificateManager']['abi']

# Save ABI to JSON file for future use in interacting with the contract
with open('CertificateManager_abi.json', 'w') as abi_file:
    json.dump(abi, abi_file)

# Create contract instance
CertificateManager = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get transaction nonce for the sender address
nonce = w3.eth.get_transaction_count(my_address)

# Build the deployment transaction (no constructor parameters)
transaction = CertificateManager.constructor().build_transaction({
    'chainId': 1337,
    'gas': 3000000,
    'gasPrice': w3.to_wei('20', 'gwei'),
    'nonce': nonce
})

# Sign the transaction with private key
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# Send the signed transaction
print("Deploying CertificateManager contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

# Wait for transaction receipt
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print(f"Contract deployed at address: {tx_receipt.contractAddress}")
