from db_utils import get_credentials, connect_to_db

def main():
    username, password, wallet_pw = get_credentials()
    conn = connect_to_db(username, password, wallet_pw)
    conn.close()
    print("Connection OK and closed")

if __name__ == "__main__":
    main()
