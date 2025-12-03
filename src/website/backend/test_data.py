from src.website.backend.coded_simulator.db_utils import get_credentials, connect_to_db

def main():
    username, password, wallet_pw = get_credentials()
    conn = connect_to_db(username, password, wallet_pw)
    cur = conn.cursor()

    print("Connected!\n")

    # Example: check the DEV1.BLACKLIST table
    table = "DEV1.BLACKLIST"
    print(f"Fetching up to 5 rows from {table}:")

    try:
        cur.execute(f"SELECT * FROM {table} WHERE ROWNUM <= 5")
        rows = cur.fetchall()
        if rows:
            for row in rows:
                print(row)
        else:
            print("No data found in this table.")
    except Exception as e:
        print(f"Error querying {table}: {e}")

    conn.close()
    print("\nConnection closed.")

if __name__ == "__main__":
    main()
