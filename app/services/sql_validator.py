def validate_sql(sql: str):
    sql_lower = sql.lower()
    if not sql_lower.startswith("select"):
        raise ValueError("Only SELECT queries allowed")

    forbidden = ["insert", "update", "delete", "drop", "alter"]
    if any(word in sql_lower for word in forbidden):
        raise ValueError("Unsafe SQL detected")

    return sql
