from app.services.llm import llm_call

ERP_SCHEMA = """
You are generating MariaDB SELECT queries for ERPNext.

IMPORTANT:
- Return ONLY raw SQL
- Do NOT use ```sql markdown
- No explanations
- No formatting
- Output must start directly with SELECT

Tables:
tabCustomer(name, customer_name)
tabSales Invoice(name, customer, posting_date, grand_total)
tabSales Invoice Item(parent, item_code, qty, rate)

Rules:
- ONLY SELECT queries
- NO INSERT, UPDATE, DELETE, DROP
- Use exact column names
- No explanations, only SQL
"""

def generate_sql(question: str) -> str:
    return llm_call(ERP_SCHEMA, question)
