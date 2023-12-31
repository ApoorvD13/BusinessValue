

import os
from google.oauth2 import service_account
import google.auth
from google.auth.transport.requests import Request

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


import vertexai
from vertexai.preview.language_models import TextGenerationModel
def predict_large_language_model_sample(
    project_id: str,
    model_name: str,
    temperature: float,
    max_decode_steps: int,
    top_p: float,
    top_k: int,
    content: str,
    location: str = "us-central1",
    tuned_model_name: str = "",
    ) :
    """Predict using a Large Language Model."""
    vertexai.init(project="annular-cogency-397714", location=location)
    model = TextGenerationModel.from_pretrained(model_name)
    if tuned_model_name:
      model = model.get_tuned_model(tuned_model_name)
    response = model.predict(
        content,
        temperature=temperature,
        max_output_tokens=max_decode_steps,
        top_k=top_k,
        top_p=top_p,)
    print(f"Response from Model: {response.text}")
predict_large_language_model_sample("${annular-cogency-397714}", "text-bison@001", 0.2, 256, 0.8, 40, '''Give me ten frequently asked interview questions for the role of machine learning engineer''', "us-central1")