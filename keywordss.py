import os
from google.oauth2 import service_account
import google.auth
from google.auth.transport.requests import Request

#changes made for verificatiom
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
# Specify the path to your JSON key file
key_path = "D:/FYProject/annular-cogency-397714-32d3bfc578fc.json"

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
import vertexai
from vertexai.preview.language_models import TextGenerationModel

# Apoorv
resume_pdf_path = "D:\FYProject\Apoorv_Dandavate_CV.pdf"  # Replace with your PDF file path

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
    prompt = f"Extract keywords that provide insights into a person's values, technical skills, and soft skills from this document or resume. Look for words or phrases that indicate their core values, such as integrity and teamwork, as well as technical proficiencies like programming languages or data analysis. Additionally, identify soft skills such as communication, leadership, and problem-solving abilities. Provide a comprehensive list of keywords that reflect the individual's qualifications and attributes..\n\nResume Content:\n{resume_text}"

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

    # Print the response
    print(f"Response from Model: {response.text}")

# Example usage:
if __name__ == "__main__":
    pdf_text = extract_text_from_pdf(resume_pdf_path)
    predict_keywords_from_resume(
        project_id="annular-cogency-397714",
        model_name="text-bison@001",
        temperature=0.2,
        max_decode_steps=256,
        top_p=0.8,
        top_k=40,
        resume_text=pdf_text,
        location="us-central1",
    )
