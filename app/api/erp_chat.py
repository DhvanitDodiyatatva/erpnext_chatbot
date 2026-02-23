from app.services.classify_intent import classify_intent
from app.services.llm import llm_call
from fastapi import APIRouter
import requests 
from app.services.sql_generator import generate_sql
from app.services.sql_validator import validate_sql
from app.services.answer_formatter import format_answer

router = APIRouter()

ERP_EXECUTOR_URL = "http://localhost:8000/api/method/chatbot.api.sql.execute_sql"


@router.post("/erp-chat")
def erp_chat(payload: dict):
    question = payload["question"]

    # 1️ Classify Intent First
    intent = classify_intent(question)
    print("Detected Intent:", intent)

    # 2️ Handle General Chat (No ERP Call)
    if intent == "GENERAL_CHAT":

        restricted_prompt = """
        You are an ERPNext assistant.

        Strict Rules:
        - You ONLY answer questions related to ERPNext system usage,
        modules, business processes, consumers, products, sales, stock, etc.
        - If the question is unrelated to ERPNext or business data,
        politely refuse.
        - Do NOT answer general knowledge questions.
        - Do NOT answer political, historical, or unrelated questions.

        If unrelated, respond with:
        "I can only assist with ERPNext-related queries."
        """

        answer = llm_call(restricted_prompt, question, temperature=0)

        return {"type": "chat", "question": question, "answer": answer}

    # 3️ Handle ERP Query
    if intent == "ERP_QUERY":
        sql = generate_sql(question)

        print("--------------------------------------------------------------")
        print("Generated SQL:", sql)
        print("--------------------------------------------------------------")

        validate_sql(sql)

        print("--------------------------------------------------------------")
        print("Generated after validate SQL:", sql)
        print("--------------------------------------------------------------")

        headers = {"Authorization": "token 3273cfe6dfbd2b7:c6dfe7d19969e92"}

        response = requests.post(
            ERP_EXECUTOR_URL, json={"sql": sql}, headers=headers, timeout=30
        )

        if response.status_code != 200:
            return {"type": "error", "error": "ERP server error"}

        try:
            erp_response = response.json()
        except ValueError:
            return {"type": "error", "error": "Invalid ERP response"}

        print("--------------------------------------------------------------")
        print("ERP RAW RESPONSE:", erp_response)
        print("--------------------------------------------------------------")

        #  Safe ERP handling
        if "exception" in erp_response:
            return {"type": "error", "question": question, "error": "ERP query failed"}

        rows = erp_response.get("message", [])

        answer = format_answer(question, rows)

        return {"type": "erp", "question": question, "sql": sql, "answer": answer}

    # 4️ Fallback Safety
    return {"type": "error", "question": question, "error": "Unable to classify query"}
