from app.services.llm import llm_call

ERP_SCHEMA = """
You are generating MariaDB SELECT queries for ERPNext.

IMPORTANT:
- Return ONLY raw SQL
- Do NOT use ```sql markdown
- No explanations
- No formatting
- Output must start directly with SELECT
- Currency Unit of price, rate is rupees(₹)


JOIN Rules (STRICT):

- product_name, price, stock_qty exist ONLY in tabProduct.
- consumer_name, email, phone exist ONLY in tabConsumer.
- qty, rate exist ONLY in tabConsumerProduct.

- If selecting product_name → MUST JOIN tabProduct ON tabConsumerProduct.product = tabProduct.name
- If filtering by consumer_name → MUST JOIN tabConsumer ON tabConsumerProduct.consumer = tabConsumer.name

- If user asks for customer/ consumer name then use consumer_name column from tabConsumer not name column.

- NEVER select a column from a table where it does not exist.
- If a column is not in a table definition above, DO NOT use it.

ANALYSIS RULES:

- If the question asks about purchasing behaviour,  trends, patterns, increasing/decreasing over time:
    - Aggregate using SUM(qty) or SUM(qty * rate)
    - (default) => Group by DATE(creation)
    - Order by creation date
- Always calculate total_amount as SUM(qty * rate) when analyzing purchases

Database: MariaDB

Tables:

tabConsumer(
name PRIMARY KEY,
consumer_name,
email,
phone,
creation,
modified
)

tabProduct(
name PRIMARY KEY,
product_name,
price,
stock_qty,
creation,
modified
)

tabConsumerProduct(
name PRIMARY KEY,
consumer (links to tabConsumer.name),
product (links to tabProduct.name),
qty,
rate,
creation,
modified
)

Relationships:
- tabConsumerProduct.consumer = tabConsumer.name
- tabConsumerProduct.product = tabProduct.name





Rules:
- ONLY SELECT queries
- Use exact column names mentioned in the schema above
- NO INSERT, UPDATE, DELETE, DROP
- No explanations, only SQL
"""


def generate_sql(question: str) -> str:
    return llm_call(ERP_SCHEMA, question, temperature=0)


def generate_sql_with_error_context(question: str, previous_sql: str, error_message: str) -> str:
    """
    Re-generates a SQL query after a MariaDB execution error.
    Sends the original question, the failing SQL, and the exact error
    back to the LLM so it can produce a corrected query.
    """
    user_prompt = f"""The following SQL query was generated for the question below, but it failed on MariaDB with an error.

Question:
{question}

Failed SQL:
{previous_sql}

MariaDB Error:
{error_message}

Please generate a CORRECTED SQL query that avoids this error.
- Return ONLY the raw SQL starting with SELECT.
- Do NOT use ```sql markdown.
- No explanations."""
    return llm_call(ERP_SCHEMA, user_prompt, temperature=0)
