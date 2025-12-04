# CREATE_SYNONYMS.PY
# Run this ONLY as an admin user.
# Creates public synonyms for DEV1 schema tables.

from db_utils import (
    get_credentials,
    connect_to_db,
    create_public_synonyms
)
import oracledb

def main():
    username, password, wallet_pw = get_credentials()
    connection = None

    try:
        connection = connect_to_db(username, password, wallet_pw)
        user = username.lower()

        if user not in ("admin", "sys", "system"):
            print("ERROR: Only admin users may create public synonyms.")
            print("Connected as:", username)
            return

        print(f"\nRunning public synonym creation as admin user '{username}' for DEV1 schema...\n")

        create_public_synonyms(connection)

        try:
            connection.commit()
            print("\nPublic synonyms created successfully.\n")
        except oracledb.DatabaseError as e:
            error, = e.args
            print("Commit failed")
            print("Code:", error.code)
            print("Message:", error.message)
            raise

    finally:
        if connection:
            try:
                connection.close()
                print("Connection closed.")
            except Exception as ex:
                print("Error closing connection:", ex)


if __name__ == "__main__":
    main()
