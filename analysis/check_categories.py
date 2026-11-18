
import duckdb

queries = {
    "REPORT REASONS": """
        SELECT DISTINCT reason
        FROM read_csv_auto('../data/raw/reports.csv')
        ORDER BY reason
    """,

    "MODERATION ACTION TYPES": """
        SELECT DISTINCT action_type
        FROM read_csv_auto('../data/raw/moderation_actions.csv')
        ORDER BY action_type
    """,

    "APPEAL OUTCOMES": """
        SELECT DISTINCT outcome
        FROM read_csv_auto('../data/raw/appeals.csv')
        ORDER BY outcome
    """
}

for title, query in queries.items():
    print(f"\n========== {title} ==========")
    duckdb.sql(query).show()
