from src.website.backend.coded_simulator.db_utils import get_credentials, connect_to_db

# -----------------------------
# MAIN SCRIPT
# -----------------------------
def main():
    username, password, wallet_pw = get_credentials()
    conn = connect_to_db(username, password, wallet_pw)
    cur = conn.cursor()
    print("✅ Connected successfully")
    conn.close()


if __name__ == "__main__":
    main()
