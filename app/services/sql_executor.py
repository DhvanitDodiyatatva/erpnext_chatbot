from sqlalchemy import text
from app.core.database import SessionLocal

ALLOWED_KEYWORDS = ("select",)

def is_safe_sql(sql: str) -> bool:
    sql_lower = sql.lower().strip()
    return sql_lower.startswith(ALLOWED_KEYWORDS)

def execute_sql(sql: str):
    if not is_safe_sql(sql):
        raise ValueError("Unsafe SQL detected")

    db = SessionLocal()
    result = db.execute(text(sql))
    rows = result.fetchall()
    columns = result.keys()

    return [dict(zip(columns, row)) for row in rows]
