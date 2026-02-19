from fastapi import APIRouter
import requests
from app.services.sql_generator import generate_sql
from app.services.sql_validator import validate_sql
from app.services.answer_formatter import format_answer

router = APIRouter()

ERP_EXECUTOR_URL = (
    "http://localhost:8000/api/method/chatbot.api.sql.execute_sql"
)


@router.post("/erp-chat")
def erp_chat(payload: dict):
    question = payload["question"]

    sql = generate_sql(question)
    print("--------------------------------------------------------------")
    print("Generated SQL:", sql)
    print("--------------------------------------------------------------")
    validate_sql(sql)
    print("--------------------------------------------------------------")
    print("Generated after validate SQL:", sql)
    print("--------------------------------------------------------------")

    headers = {"Authorization": "token 3273cfe6dfbd2b7:c6dfe7d19969e92"}

    erp_response = requests.post(
        ERP_EXECUTOR_URL, json={"sql": sql}, headers=headers, timeout=30
    ).json()

    print("--------------------------------------------------------------")
    print("ERP RAW RESPONSE:", erp_response)
    print("--------------------------------------------------------------")

    rows = erp_response["message"]

    answer = format_answer(question, rows)

    return {"question": question, "sql": sql, "answer": answer}
