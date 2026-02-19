from app.services.llm import llm_call

def format_answer(question: str, rows: list[dict]) -> str:
    if not rows:
        return "No data found."

    prompt = f"""
Question:
{question}

Database Result:
{rows}

Explain this clearly in business-friendly language.
"""
    return llm_call(
        "You are a helpful ERP assistant.",
        prompt,
        temperature=0.3
    )
