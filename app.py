from flask import Flask, render_template, request
import os
import PyPDF2
from groq import Groq

app = Flask(__name__)

# Groq client (set your API key in Render → Environment Variables → GROQ_API_KEY)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

pdf_text = ""  # Store PDF text in memory

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    global pdf_text
    file = request.files.get("pdf")

    if not file:
        return "No file uploaded"

    try:
        reader = PyPDF2.PdfReader(file)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text() + "\n"
        return "✅ PDF uploaded successfully. Now ask a question!"
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

@app.route("/ask", methods=["POST"])
def ask():
    global pdf_text
    user_question = request.form.get("question")

    if not pdf_text:
        return "⚠️ Please upload a PDF first."
    if not user_question:
        return "⚠️ Please enter a question."

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",   # free LLaMA-3 model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the given PDF text."},
                {"role": "user", "content": f"PDF Content:\n{pdf_text}\n\nQuestion: {user_question}"}
            ]
        )
        answer = response.choices[0].message.content
        return answer
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
