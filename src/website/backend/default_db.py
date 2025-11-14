# DO NOT RUN THIS AS PRIMARY DEV ONCE THE DATABASE IS IN USE, AS IT WILL DELETE ALL DATA!
# THIS FILE IS ONLY FOR INITIAL SETUP OF THE DATABASE SCHEMA.
import getpass
import oracledb

try:
    # Enter Oracle username
    username = input("Enter Oracle username: ")

    # Connect to Oracle Database
    pw = getpass.getpass("Enter password: ")

    # Enter wallet password if applicable (otherwise leave as empty string)
    wall_pass = getpass.getpass("Enter wallet password (if applicable, else leave blank): ")

    connection = oracledb.connect(
        user=username,
        password=pw,
        dsn="watchtowerdev_low", # change if your DSN differs (check tnsnames.ora) or use connection string directly
        config_dir="./Wallet_WatchTowerDev", # change if your wallet location differs (should be unnecessary if file is in same dir)
        wallet_location="./Wallet_WatchTowerDev",
        wallet_password=wall_pass
    )
except oracledb.DatabaseError as e:
    error, = e.args
    print("There was a problem connecting to the database:")
    print("Code:", error.code)
    print("Message:", error.message)
    exit(1)
except Exception as ex:
    print("An unexpected error occurred:", ex)
    exit(1)

print("Successfully connected to Oracle Database\n")
if username.lower() == "admin": # actually should be main dev user
    # Create Tables
    with connection.cursor() as cursor:
        # Drop existing tables (in reverse dependency order)
        for table in ["Blacklist", "History", "Devices", "Users"]:
            cursor.execute(f"""
                BEGIN
                    EXECUTE IMMEDIATE 'DROP TABLE {table} CASCADE CONSTRAINTS';
                EXCEPTION
                    WHEN OTHERS THEN
                        IF SQLCODE != -942 THEN
                            RAISE;
                        END IF;
                END;
            """)
        print("Old tables dropped (if they existed)")

        # Users table
        cursor.execute("""
            CREATE TABLE Users (
                id              NUMBER GENERATED ALWAYS AS IDENTITY,
                username        VARCHAR2(255) NOT NULL,
                password        VARCHAR2(255) NOT NULL,
                CONSTRAINT pk_users PRIMARY KEY (id),
                CONSTRAINT uq_users_username UNIQUE (username)
            )
        """)
        print("Users table created")

        # Devices table
        cursor.execute("""
            CREATE TABLE Devices (
                id              NUMBER GENERATED ALWAYS AS IDENTITY,
                name            VARCHAR2(255) NOT NULL,
                os              VARCHAR2(255),
                manufacturer    VARCHAR2(255),
                mac_address     VARCHAR2(255) NOT NULL,
                port            NUMBER,
                user_id         NUMBER NOT NULL,
                CONSTRAINT pk_devices PRIMARY KEY (id),
                CONSTRAINT uq_devices_mac UNIQUE (mac_address),
                CONSTRAINT fk_devices_users FOREIGN KEY (user_id)
                    REFERENCES Users(id)
                    ON DELETE CASCADE
            )
        """)
        print("Devices table created")

        # History table
        cursor.execute("""
            CREATE TABLE History (
                device_id           NUMBER,
                datetime            TIMESTAMP,
                outgoing_ip         VARCHAR2(255),
                incoming_ip         VARCHAR2(255),
                network_protocol    VARCHAR2(255),
                connection_status   VARCHAR2(255),
                CONSTRAINT pk_history PRIMARY KEY (device_id, datetime),
                CONSTRAINT fk_history_devices FOREIGN KEY (device_id)
                    REFERENCES Devices(id)
                    ON DELETE CASCADE,
                CONSTRAINT chk_history_status CHECK (connection_status IN ('Connected', 'Disconnected'))
            )
        """)
        print("History table created")

        # Blacklist table
        cursor.execute("""
            CREATE TABLE Blacklist (
                device_id   NUMBER,
                blocked     NUMBER(1,0) DEFAULT 0 NOT NULL,
                CONSTRAINT pk_blacklist PRIMARY KEY (device_id),
                CONSTRAINT fk_blacklist_devices FOREIGN KEY (device_id)
                    REFERENCES Devices(id)
                    ON DELETE CASCADE
            )
        """)
        print("Blacklist table created")

    connection.commit()
    connection.close()

    print("All tables created successfully with cascade deletes and connection closed.")

else:
    print("You must connect as 'admin' to set up the database schema.")
    print("You are connected as:", username)
    print("Exiting without making any changes.\n")

connection.close()
print("Connection closed.")