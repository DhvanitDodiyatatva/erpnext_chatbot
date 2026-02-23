from app.services.llm import llm_call
import json

def format_answer(question: str, rows: list[dict]) -> str:
    if not rows:
        return "No data found."

    rows_json = json.dumps(rows, indent=2)

    prompt = f"""
You are an ERP assistant.

User Question:
{question}

Database Result (JSON):
{rows_json}

Instructions:
- List ALL items from the database result.
- Consider the Database Result (JSON) as a final answeres to the user question.
- Do NOT omit any item.
- Do NOT add recommendations.
- Present the answer clearly and directly.

Generate the final answer.
"""

    return llm_call(
        "You are a precise ERP data assistant.",
        prompt,
        temperature=0
    )
