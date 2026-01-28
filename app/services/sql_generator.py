from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SQL_SYSTEM_PROMPT = """
You are an expert PostgreSQL assistant.

Rules:
- Generate ONLY a SELECT query
- Do NOT use INSERT, UPDATE, DELETE, DROP, TRUNCATE
- Use only the tables and columns provided
- Do NOT add explanations, only SQL

Schema:
customers(id, name, email, created_at, updated_at)
products(id, name, category, price, created_at, updated_at)
customer_product(customer_id, product_id, created_at, updated_at)
"""

def generate_sql(question: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0,
        messages=[
            {"role": "system", "content": SQL_SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ]
    )

    return response.choices[0].message.content.strip()
