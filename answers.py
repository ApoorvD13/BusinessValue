import fitz  # PyMuPDF
import vertexai
from vertexai.preview.language_models import TextGenerationModel

# Define the PDF file path
resume_pdf_path = "Apoorv_Dandavate_CV.pdf"  # Replace with your PDF file path

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
    prompt = f"Extract keywords that provide insights into a person's values, technical skills, and soft skills from this document or resume. Look for words or phrases that indicate their core values, such as integrity and teamwork, as well as technical proficiencies like programming languages or data analysis. Additionally, identify soft skills such as communication, leadership, and problem-solving abilities. Provide a comprehensive list of keywords that reflect the individual's qualifications and attributes:\n\nResume Content:\n{resume_text}"

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

    # Extract and return the generated keywords
    keywords = response.text.strip().split(',')
    return keywords

# Function to generate interview question and answer based on keywords
def generate_interview_question_and_answer(
    model_name: str,
    temperature: float,
    max_decode_steps: int,
    top_p: float,
    top_k: int,
    keywords: str,
    location: str = "us-central1",
):
    # Initialize Vertex AI
    vertexai.init(location=location)

    # Load the TextGenerationModel
    model = TextGenerationModel.from_pretrained(model_name)

    # Generate an interview question based on provided keywords
    question_prompt = f"Generate  5 frequently asked HR interview question:\n\n"
    question_response = model.predict(
        question_prompt,
        temperature=temperature,
        max_output_tokens=max_decode_steps,
        top_k=top_k,
        top_p=top_p,
    )

    # Generate a personalized answer to the generated question
    generated_question = question_response.text.strip()
    answer_prompt = f"Generate personalized answers to all the questions one by one using generated keywords:\n\n{generated_question}{', '.join(keywords)}"
    answer_response = model.predict(
        answer_prompt,
        temperature=temperature,
        max_output_tokens=max_decode_steps,
        top_k=top_k,
        top_p=top_p,
    )

    # Print the generated question and answer
    print(f"Generated Interview Question: {generated_question}")
    print(f"Generated Personalized Answer: {answer_response.text}")

# Example usage:
if __name__ == "__main__":
    pdf_text = extract_text_from_pdf(resume_pdf_path)
    keywords = predict_keywords_from_resume(
        project_id="annular-cogency-397714",
        model_name="text-bison@001",
        temperature=0.2,
        max_decode_steps=256,
        top_p=0.8,
        top_k=40,
        resume_text=pdf_text,
        location="us-central1",
    )

    if keywords:
        generate_interview_question_and_answer(
            model_name="text-bison@001",  # Replace with the name of the pre-trained model
            temperature=0.2,
            max_decode_steps=256,
            top_p=0.8,
            top_k=40,
            keywords=keywords,
            location="us-central1",
        )
