"""
Script to execute all SQL queries from customer_behavior_sql_queries.sql
against customer_behavior.db and display results in the terminal.
"""

import os
import re
import sqlite3
import pandas as pd

# Set pandas display options for clean terminal output
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)


def load_queries(sql_file_path: str):
    with open(sql_file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Matches any question divider: e.g. --Q11, -- Q11, --q11, -- Question 11, with optional indentation
    chunks = re.split(r"\n(?=\s*--\s*(?:q(?:uestion)?\s*\d+))", text.strip(), flags=re.IGNORECASE)
    queries = []
    for chunk in chunks:
        lines = chunk.strip().split("\n")
        comments = []
        sql_lines = []
        parsing_title = True

        for line in lines:
            stripped = line.strip()
            # Only top-level comment lines before SQL code become part of the title
            if parsing_title and stripped.startswith("--"):
                clean_comment = stripped.lstrip("-").strip()
                if clean_comment:
                    comments.append(clean_comment)
            elif stripped:
                parsing_title = False
                sql_lines.append(line)

        title = " ".join(comments) if comments else "SQL Query"
        sql = "\n".join(sql_lines).strip()
        if sql:
            queries.append((title, sql))
    return queries


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "database_customer.db") if os.path.exists(os.path.join(base_dir, "database_customer.db")) else os.path.join(base_dir, "customer_behavior.db")
    sql_path = os.path.join(base_dir, "sql_queries.sql") if os.path.exists(os.path.join(base_dir, "sql_queries.sql")) else os.path.join(base_dir, "customer_behavior_sql_queries.sql")

    conn = sqlite3.connect(db_path)
    queries = load_queries(sql_path)

    print("=" * 80)
    print(f"  RUNNING ALL {len(queries)} QUERIES ON {os.path.basename(db_path)}")
    print("=" * 80 + "\n")

    for idx, (title, sql) in enumerate(queries, 1):
        print(f"[{idx}/{len(queries)}] {title}")
        print("-" * 80)
        try:
            df = pd.read_sql_query(sql, conn)
            total_rows = len(df)
            if total_rows > 10:
                print(df.head(10).to_string(index=False))
                print(f"\n... (showing top 10 of {total_rows} rows)")
            else:
                print(df.to_string(index=False))
        except Exception as e:
            print(f"Error: {e}")

        print("\n" + "=" * 80 + "\n")

    conn.close()


if __name__ == "__main__":
    main()
