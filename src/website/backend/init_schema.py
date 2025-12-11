# INIT_SCHEMA.PY
# Run this ONLY as DEV1 — it drops tables and recreates schema.
# DO NOT run after production begins.

from db_utils import (
    get_credentials,
    connect_to_db,
    setup_schema
)
import oracledb

def main():
    username, password, wallet_pw = get_credentials()
    connection = None

    try:
        connection = connect_to_db(username, password, wallet_pw)

        if username.lower() != "dev1":
            print("ERROR: Only DEV1 may run schema initialization.")
            print("Connected as:", username)
            return

        print("\nRunning schema setup as DEV1...\n")
        setup_schema(connection)

        try:
            connection.commit()
            print("\nSchema created and privileges granted successfully.\n")
        except oracledb.DatabaseError as e:
            error, = e.args
            print("\nCommit failed")
            print("Code:", error.code)
            print("Message:", error.message)
            raise

    except oracledb.DatabaseError as e:
        error, = e.args
        print("Error opening connection:")
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
