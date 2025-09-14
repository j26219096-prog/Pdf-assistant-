import re
from flask import Flask, request, jsonify, render_template
from groq import Groq

app = Flask(__name__)
client = Groq(api_key="YOUR_GROQ_API_KEY")

# ✅ Chunking function
def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i+chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_question = data.get("question", "")
    pdf_text = data.get("pdf_text", "")

    if not pdf_text or not user_question:
        return jsonify({"answer": "Please upload a PDF and ask a question."})

    # 🔹 Split PDF into chunks
    chunks = chunk_text(pdf_text, chunk_size=500, overlap=50)

    # 🔹 Pick the most relevant chunk based on keyword overlap
    best_chunk = max(chunks, key=lambda c: len(re.findall(user_question.lower(), c.lower())))

    # 🔹 Call Groq API with only best chunk
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",   # can also try "llama-3.1-70b-versatile"
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on the given PDF text."},
            {"role": "user", "content": f"PDF Content:\n{best_chunk}\n\nQuestion: {user_question}"}
        ]
    )

    return jsonify({"answer": response.choices[0].message.content})
