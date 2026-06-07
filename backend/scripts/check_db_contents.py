import psycopg2
import json

# Connection parameters (adjust if needed)
conn = psycopg2.connect(
    host="db",
    port=5432,
    user="postgres",
    password="password",
    database="postgres"
)

def print_table(cursor, table_name, limit=5):
    """Print first 'limit' rows from a table, plus total row count."""
    print(f"\n--- Table: {table_name} ---")
    
    # Get total count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"Total rows: {count}")
    
    if count == 0:
        return
    
    # Get column names
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 0")
    colnames = [desc[0] for desc in cursor.description]
    
    # Fetch a few rows
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
    rows = cursor.fetchall()
    
    # Print each row as formatted dict (or simple for JSONB columns)
    for i, row in enumerate(rows, 1):
        print(f"  Row {i}:")
        for idx, col in enumerate(colnames):
            value = row[idx]
            # If column is likely JSONB (content in submissions), pretty print it
            if col in ('content', 'files') and value is not None:
                try:
                    if isinstance(value, str):
                        value = json.loads(value)
                    value = json.dumps(value, indent=4)
                except:
                    pass
            print(f"    {col}: {value}")
    print("")

cursor = conn.cursor()

# Display tables
for table in ['tasks', 'task_files', 'users', 'submissions', 'submission_results']:
    try:
        print_table(cursor, table, limit=5)
    except psycopg2.Error as e:
        print(f"Error reading {table}: {e}")

cursor.close()
conn.close()