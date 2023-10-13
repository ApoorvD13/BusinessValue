import os
from google.oauth2 import service_account
import google.auth
from google.auth.transport.requests import Request

# Specify the path to your JSON key file
key_path = "C:/Users/dell 3593/Downloads/annular-cogency-397714-6e8aded04175.json"

# Load the credentials
credentials = service_account.Credentials.from_service_account_file(key_path)

# Use the credentials for authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path  # Set the environment variable

credentials, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

if credentials and credentials.valid:
    # You are authenticated
    pass
else:
    # Authenticate if not already authenticated
    credentials.refresh(Request())

import fitz  # PyMuPDF
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from google.cloud import storage
import os

# Function to create a PDF from text input
def create_text_pdf(text):
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.drawString(100, 750, text)  # Adjust the position and style as needed
    can.save()

    packet.seek(0)
    new_pdf = fitz.open("pdf", packet.read())
    return new_pdf

# Function to merge text PDFs and resume PDF into a single PDF
def merge_pdfs(text_pdfs, resume_pdf):
    output_pdf = fitz.open()

    # Insert each text PDF
    for text_pdf in text_pdfs:
        output_pdf.insert_pdf(text_pdf)

    # Insert the resume PDF
    output_pdf.insert_pdf(resume_pdf)

    return output_pdf

# Replace these with your user-entered text and resume file path
question1_text = "Answer to question 1."
question2_text = "Answer to question 2."
question3_text = "Answer to question 3."
question4_text = "Answer to question 4."
question5_text = "Answer to question 5."
resume_pdf_path = "C:/Users/dell 3593/Downloads/Vaishnavi Shastri Resume 1 page.pdf"

# Create PDFs from user-entered text
text_pdfs = [
    create_text_pdf(question1_text),
    create_text_pdf(question2_text),
    create_text_pdf(question3_text),
    create_text_pdf(question4_text),
    create_text_pdf(question5_text)
]

# Open the user's resume PDF
resume_pdf = fitz.open(resume_pdf_path)

# Merge the text PDFs and resume PDF
merged_pdf = merge_pdfs(text_pdfs, resume_pdf)

# Extract the filename from the resume file path
resume_filename = os.path.basename(resume_pdf_path)

# Create the destination object name based on the resume filename
destination_blob_name = f"merged_{os.path.splitext(resume_filename)[0]}.pdf"

# Save the merged PDF to a file
merged_pdf_path = "merged_resume.pdf"
merged_pdf.save(merged_pdf_path)

# Upload the merged PDF to Google Cloud Storage
bucket_name = 'bvi_mergedfiles'  # Replace with your GCS bucket name

storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(destination_blob_name)
blob.upload_from_filename(merged_pdf_path)

print(f'Merged PDF uploaded to {bucket_name}/{destination_blob_name}')


