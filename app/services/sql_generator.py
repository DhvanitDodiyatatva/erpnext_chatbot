from app.services.llm import llm_call

ERP_SCHEMA = """
You are generating MariaDB SELECT queries for ERPNext.

IMPORTANT:
- Return ONLY raw SQL
- Do NOT use ```sql markdown
- No explanations
- No formatting
- Output must start directly with SELECT


JOIN Rules (STRICT):

- product_name, price, stock_qty exist ONLY in tabProduct.
- consumer_name, email, phone exist ONLY in tabConsumer.
- qty, rate exist ONLY in tabConsumerProduct.

- If selecting product_name → MUST JOIN tabProduct ON tabConsumerProduct.product = tabProduct.name
- If filtering by consumer_name → MUST JOIN tabConsumer ON tabConsumerProduct.consumer = tabConsumer.name

- NEVER select a column from a table where it does not exist.
- If a column is not in a table definition above, DO NOT use it.

Database: MariaDB

Tables:

tabConsumer(
name PRIMARY KEY,
consumer_name,
email,
phone
)

tabProduct(
name PRIMARY KEY,
product_name,
price,
stock_qty
)

tabConsumerProduct(
name PRIMARY KEY,
consumer (links to tabConsumer.name),
product (links to tabProduct.name),
qty,
rate
)

Relationships:
- tabConsumerProduct.consumer = tabConsumer.name
- tabConsumerProduct.product = tabProduct.name





Rules:
- ONLY SELECT queries
- NO INSERT, UPDATE, DELETE, DROP
- Use exact column names
- No explanations, only SQL
"""


def generate_sql(question: str) -> str:
    return llm_call(ERP_SCHEMA, question)
