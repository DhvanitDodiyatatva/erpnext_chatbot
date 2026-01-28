from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def format_answer(question: str, data: list[dict]) -> str:
    if not data:
        return "No data found for this query."

    prompt = f"""
User question:
{question}

Database result:
{data}

Explain the result clearly in natural language.
"""  

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0.3,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
