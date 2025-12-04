# DO NOT RUN FILE AS "PRIMARY DEV" ONCE THE DATABASE IS IN USE, AS IT WILL DELETE ALL DATA!
# THIS FILE IS ONLY FOR INITIAL SETUP/CREATION OF THE DATABASE SCHEMA.
from db_utils import get_credentials, connect_to_db, setup_schema
import oracledb

# MAIN PROGRAM
def main():
    username, password, wallet_pw = get_credentials()
    connection = None

    try:
        connection = connect_to_db(username, password, wallet_pw)

        if username.lower() != "dev1":
            print("You must connect as 'dev1' to set up the database.")
            print("Connected as:", username)
            print("Exiting without making changes.\n")
            return

        print("Setting up database schema...\n")
        setup_schema(connection)

        # Commit with safe handling
        
        try:
            connection.commit()
            print("\nAll tables created successfully.\n")
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


# Start script
if __name__ == "__main__":
    main()
