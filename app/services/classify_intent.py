from app.services.llm import llm_call


INTENT_PROMPT = """
You are an intent classifier.

Classify the user query into EXACTLY ONE of the following labels:

ERP_QUERY
GENERAL_CHAT

Rules:
- If the question/command is about consumers, customers, products, stock, sales, quantity, or price → ERP_QUERY
- Otherwise → GENERAL_CHAT

Return ONLY the label.
Do NOT explain.
Do NOT write sentences.
Do NOT add extra text.
"""



def classify_intent(question: str) -> str:
    result = llm_call(INTENT_PROMPT, question)
    result = result.strip().upper()

    if "ERP_QUERY" in result:
        return "ERP_QUERY"

    if "GENERAL_CHAT" in result:
        return "GENERAL_CHAT"

    return "GENERAL_CHAT"  
