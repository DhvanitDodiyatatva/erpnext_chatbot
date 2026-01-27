import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL_NAME = "llama-3.1-8b-instant"

def generate_answer(context: str, question: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. "
                "Answer ONLY using the provided context. "
                "If the answer is not in the context, say "
                "'I don't have that information.'"
            )
        },
        {
            "role": "user",
            "content": f"""
Context:
{context}

Question:
{question}
"""
        }
    ]

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.2,
        max_tokens=300
    )

    return response.choices[0].message.content
