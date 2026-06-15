import json
import fitz  # PyMuPDF
import io
from PIL import Image
from pyzbar.pyzbar import decode
from web3 import Web3

# 1. Connect to Ganache blockchain
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

# 2. Update with your latest deployed contract address
contract_address = ''

# 3. Load ABI from JSON file
with open('CertificateManager_abi.json', 'r') as f:
    abi = json.load(f)

# 4. Create contract instance
contract = w3.eth.contract(address=contract_address, abi=abi)

def extract_id_from_pdf(pdf_path):
    """Converts PDF to image and scans for the Certificate ID in the QR code"""
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)  # Load the first page
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # Higher resolution for QR
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))
        
        # Scan QR code
        decoded_objects = decode(image)
        if decoded_objects:
            # Assuming the QR contains just the ID or the verification URL
            qr_data = decoded_objects[0].data.decode('utf-8')
            # If your QR is a URL, extract the ID from the end
            if "candidate=" in qr_data:
                return qr_data.split("candidate=")[-1]
            return qr_data
        return None
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None

def verify_certificate(certificate_number: str):
    """Queries the blockchain for all 10 certificate fields"""
    try:
        # result now returns 10 strings matching your updated smart contract
        result = contract.functions.getCertificate(certificate_number).call()
        
        if not result[0]: # Check if Certificate ID is empty
            print(f"\n❌ No record found on blockchain for ID: {certificate_number}")
            return

        (cert_no, student_name, roll_no, degree, branch,
         grad_year, college, university, cgpa, date_of_issue) = result
        
        print("\n✅ CERTIFICATE VERIFIED ON BLOCKCHAIN!")
        print("-" * 40)
        print(f"Certificate Number : {cert_no}")
        print(f"Student Name       : {student_name}")
        print(f"Roll Number        : {roll_no}")
        print(f"Degree/Course      : {degree}")
        print(f"Branch             : {branch}")
        print(f"Graduation Year    : {grad_year}")
        print(f"College Name       : {college}")
        print(f"University         : {university}")
        print(f"CGPA               : {cgpa}")
        print(f"Date of Issue      : {date_of_issue}")
        print("-" * 40)
        
    except Exception as e:
        print("\n❌ Error querying blockchain:", e)

# Main Execution
print("--- Blockchain PDF Verification System ---")
path = input("Enter the path to the Certificate PDF file: ").strip().replace('"', '')

# Automatically extract ID from the PDF you uploaded
cert_id = extract_id_from_pdf(path)

if cert_id:
    print(f"🔍 Detected Certificate ID: {cert_id}")
    verify_certificate(cert_id)
else:
    # Fallback to manual entry if QR scan fails
    print("⚠️ Could not detect QR code in PDF.")
    manual_id = input("Enter certificate number manually: ")
    verify_certificate(manual_id)