# DO NOT RUN FILE AS "PRIMARY DEV" ONCE THE DATABASE IS IN USE, AS IT WILL DELETE ALL DATA!
# THIS FILE IS ONLY FOR INITIAL SETUP/CREATION OF THE DATABASE SCHEMA.

from db_utils import (
    get_credentials,
    connect_to_db,
    setup_schema,
    grant_privileges_to_role,
    create_public_synonyms
)
import oracledb


def main():
    username, password, wallet_pw = get_credentials()
    connection = None

    try:
        connection = connect_to_db(username, password, wallet_pw)
        uname = username.lower()

        admin_users = {"admin", "sys", "system"}

        # --------------------------------------------------------------
        # CASE 1: Not admin and not dev1 → do nothing
        # --------------------------------------------------------------
        if uname not in admin_users and uname != "dev1":
            print("You must connect as 'dev1' or an admin user to run setup.")
            print("Connected as:", username)
            print("Exiting without changes.\n")
            return

        # --------------------------------------------------------------
        # STEP 1: Schema Creation (dev1 or admin)
        # --------------------------------------------------------------
        print("Setting up database schema...\n")
        setup_schema(connection)

        try:
            connection.commit()
            print("\nTables created successfully.\n")
        except oracledb.DatabaseError as e:
            error, = e.args
            print("Commit failed after schema creation")
            print("Code:", error.code)
            print("Message:", error.message)
            raise

        # --------------------------------------------------------------
        # STEP 2: Admin-only actions (privileges + synonyms)
        # --------------------------------------------------------------
        if uname in admin_users:
            print(f"Connected as admin account '{username}'. Running admin tasks...\n")

            # Grant privileges
            try:
                grant_privileges_to_role(connection)
                print("Privileges granted successfully.\n")
            except Exception as e:
                print("ERROR granting privileges:", e)
                raise

            # Create public synonyms
            try:
                create_public_synonyms(connection, schema_name="DEV1")
                print("Public synonyms created successfully.\n")
            except Exception as e:
                print("ERROR creating public synonyms:", e)
                raise

            # Final commit
            try:
                connection.commit()
                print("Admin tasks completed and committed.\n")
            except oracledb.DatabaseError as e:
                error, = e.args
                print("Commit failed during admin tasks")
                print("Code:", error.code)
                print("Message:", error.message)
                raise

        else:
            print("Connected as dev1 — schema created. No admin tasks executed.\n")

    finally:
        if connection:
            try:
                connection.close()
                print("Connection closed.")
            except Exception as ex:
                print("Error closing connection:", ex)


if __name__ == "__main__":
    main()
