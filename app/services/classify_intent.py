from app.services.llm import llm_call

# Align with sql_generator: only these tables/columns exist in ERP DB.
ERP_SCHEMA_SUMMARY = """
ERP database has ONLY these tables and columns:
- tabConsumer: name, consumer_name, email, phone, creation, modified
- tabProduct: name, product_name, price, stock_qty, creation, modified
- tabConsumerProduct: name, consumer, product, qty, rate, creation, modified
(No invoice_no, page_no, or document/page-based, holidays list, leave, product specification/ description/details, fields.)
"""

INTENT_PROMPT = f"""
You are an intent classifier.

Classify the user query into EXACTLY ONE of these two labels:

ERP_QUERY
DOCUMENT_QUERY

{ERP_SCHEMA_SUMMARY}

Rules:
- ERP_QUERY: ONLY if the question can be answered using the ERP schema above.
  Examples: list consumers, product prices, stock, quantities and rates from tabConsumerProduct,
  sales by date, totals (SUM qty * rate), etc. No mention of "invoice number", "page", or PDF/document.
- DO not use ERP_QUERY when quesiton is about billing details of a specific order/Invoice(order No. = Invoice No) instead use DOCUMENT_QUERY.
- DOCUMENT_QUERY: Everything else. Use this when:
  - The question asks about a specific invoice by number and/or page, billing details of a specific order/Invoice(order No. = Invoice No)
  - The question refers to ingested documents, PDFs, manuals, policies, leave documents, or unstructured text, OR
  - The question is general, small talk, or not answerable from the ERP tables above.

Return ONLY the label.
Do NOT explain. Do NOT add extra text.
"""


def classify_intent(question: str) -> str:
    result = llm_call(INTENT_PROMPT, question)
    result = result.strip().upper()

    if "ERP_QUERY" in result:
        return "ERP_QUERY"
    return "DOCUMENT_QUERY"
