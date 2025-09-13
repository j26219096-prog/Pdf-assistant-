import os
from flask import Flask, render_template, request
import openai
import PyPDF2

app = Flask(__name__)

# OpenAI API key from Render secret
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    answer = ""
    error = ""
    try:
        if request.method == "POST":
            pdf_file = request.files.get("pdf")
            question = request.form.get("question")

            if not pdf_file:
                error = "No PDF uploaded!"
            elif not question:
                error = "Please enter a question!"
            else:
                reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text

                if not text.strip():
                    error = "PDF is empty or could not extract text."
                else:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role":"user", "content": f"Text: {text}\nQuestion: {question}"}]
                    )
                    answer = response.choices[0].message.content

    except Exception as e:
        error = f"An error occurred: {str(e)}"

    return render_template("index.html", answer=answer, error=error)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
