from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from web3 import Web3

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Connect to local Ganache (or update to your testnet/mainnet provider)
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

# Replace with your contract address from deployment
contract_address = ''

# Load ABI from file
with open('CertificateManager_abi.json', 'r') as f:
    abi = json.load(f)

contract = w3.eth.contract(address=contract_address, abi=abi)

# Replace with your Ganache private key
private_key = ''
issuer_account = w3.eth.account.from_key(private_key)
issuer_address = issuer_account.address

@app.route('/issue_certificate', methods=['POST'])
def issue_certificate():
    try:
        data = request.json
        required_fields = [
            'certificateNumber', 'studentName', 'rollNumber',
            'degree', 'branch', 'graduationYear',
            'college', 'university', 'cgpa', 'dateOfIssue'
        ]
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required certificate fields'}), 400

        cert_data = [data[field] for field in required_fields]
        nonce = w3.eth.get_transaction_count(issuer_address)
        tx = contract.functions.issueCertificate(*cert_data).build_transaction({
            'chainId': 1337,
            'gas': 3000000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': nonce
        })
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return jsonify({'txHash': tx_hash.hex()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/verify_certificate/<certificateNumber>', methods=['GET'])
def verify_certificate(certificateNumber):
    try:
        cert = contract.functions.getCertificate(certificateNumber).call()
        # If certificateNumber is empty, certificate not found
        if not cert[0]:
            return jsonify({'error': 'Certificate not found'}), 404
        return jsonify({
            'certificateNumber': cert[0],
            'studentName': cert[1],
            'rollNumber': cert[2],
            'degree': cert[3],
            'branch': cert[4],
            'graduationYear': cert[5],
            'college': cert[6],
            'university': cert[7],
            'cgpa': cert[8],
            'dateOfIssue': cert[9]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    app.run(debug=True)
