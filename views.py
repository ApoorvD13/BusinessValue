from django.http import HttpResponse
from django.shortcuts import render
import os
from google.oauth2 import service_account
import google.auth
from google.auth.transport.requests import Request
from google.cloud import storage
from io import BytesIO
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import vertexai
from vertexai.preview.language_models import TextGenerationModel

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
    for text_pdf in text_pdfs:
        output_pdf.insert_pdf(text_pdf)
    output_pdf.insert_pdf(resume_pdf)
    return output_pdf

# Define the PDF file path
resume_pdf_path = "C:/Users/dell 3593/Downloads/ilovepdf_merged.pdf"  # Replace with your PDF file path

# Function to extract text from a PDF file using PyMuPDF
def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text += page.get_text()
    return text

# Function to predict keywords from extracted resume text using Vertex AI
def predict_keywords_from_resume(
    project_id: str,
    model_name: str,
    temperature: float,
    max_decode_steps: int,
    top_p: float,
    top_k: int,
    resume_text: str,
    location: str = "us-central1",
    tuned_model_name: str = "",
):
    # Generate a prompt for keyword extraction
    prompt = f"Extract keywords that provide insights into a person's values, technical skills, and soft skills from this document and resume. Look for words or phrases that indicate their core values, such as integrity and teamwork, as well as technical proficiencies like programming languages or data analysis. Additionally, identify soft skills such as communication, leadership, and problem-solving abilities. Provide a comprehensive list of keywords that reflect the individual's qualifications and attributes..\n\nResume Content:\n{resume_text}"

    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location)

    # Load the TextGenerationModel
    model = TextGenerationModel.from_pretrained(model_name)

    if tuned_model_name:
        model = model.get_tuned_model(tuned_model_name)

    # Make a prediction using the generated prompt
    response = model.predict(
        prompt,
        temperature=temperature,
        max_output_tokens=max_decode_steps,
        top_k=top_k,
        top_p=top_p,
    )

    # Extract keywords from the response
    extracted_keywords = response.text.split(', ')  # Assuming keywords are separated by a comma and space

    # Print the extracted keywords
    print("Extracted Keywords:")
    for keyword in extracted_keywords:
        print(keyword)

    return extracted_keywords

# Function to generate a self-introduction script using Vertex AI
def generate_introduction_script(
    project_id: str,
    model_name: str,
    temperature: float,
    max_decode_steps: int,
    top_p: float,
    top_k: int,
    resume_text: str,
    keywords: list,
    location: str = "us-central1",
    tuned_model_name: str = "",
):
    # Generate a prompt for script generation
    keyword_string = ', '.join(keywords)
    prompt = f"Generate a self-introduction script for an individual with the following keywords: {keyword_string}. Use these keywords to highlight the individual's strengths and skills based on their resume content:\n\n{resume_text}"

    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location)

    # Load the TextGenerationModel
    model = TextGenerationModel.from_pretrained(model_name)

    if tuned_model_name:
        model = model.get_tuned_model(tuned_model_name)

    # Make a prediction using the generated prompt
    response = model.predict(
        prompt,
        temperature=temperature,
        max_output_tokens=max_decode_steps,
        top_k=top_k,
        top_p=top_p,
    )

    # Extract the generated script from the response
    generated_script = response.text

    # Print the generated script
    print("Generated Introduction Script:")
    print(generated_script)

def index(request):
    return render(request, 'index.html')

def analyze(request):
    question1_text = request.GET.get('text1', 'default')
    question2_text = request.GET.get('text2', 'default')
    question3_text = request.GET.get('text3', 'default')
    question4_text = request.GET.get('text4', 'default')
    question5_text = request.GET.get('text5', 'default')

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

    # Extract text from the merged resume PDF
    merged_pdf_text = extract_text_from_pdf(merged_pdf_path)

    # Predict keywords from the merged resume PDF using Vertex AI
    keywords = predict_keywords_from_resume(
        project_id="annular-cogency-397714",
        model_name="text-bison@001",
        temperature=0.2,
        max_decode_steps=256,
        top_p=0.8,
        top_k=40,
        resume_text=merged_pdf_text,
        location="us-central1",
    )

    # Generate the self-introduction script using extracted keywords
    generate_introduction_script(
        project_id="annular-cogency-397714",
        model_name="text-bison@001",
        temperature=0.2,
        max_decode_steps=256,
        top_p=0.8,
        top_k=40,
        resume_text=merged_pdf_text,
        keywords=keywords,
    )

    params = {
        'Success': "Merging, Keyword Extraction, and Script Generation Successful"
    }

    return render(request, 'analyze.html', params)

