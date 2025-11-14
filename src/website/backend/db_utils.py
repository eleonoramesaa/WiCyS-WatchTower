import getpass
import oracledb

# CONNECTION HANDLING
def get_credentials():
    username = input("Enter Oracle username: ")
    password = getpass.getpass("Enter password: ")
    wallet_password = getpass.getpass("Enter wallet password (if applicable, else leave blank): ")
    return username, password, wallet_password


def connect_to_db(username, password, wallet_password):
    try:
        conn = oracledb.connect(
            user=username,
            password=password,
            dsn="watchtowerdev_low", # change if your DSN differs (check tnsnames.ora) or use connection string 
            config_dir="./Wallet_WatchTowerDev", # change if your wallet location differs (should be unnecessary if file is in same dir/project folder)
            wallet_location="./Wallet_WatchTowerDev", # follow the above dir comment
            wallet_password=wallet_password
        )
        print("Successfully connected to Oracle Database\n")
        return conn

    except oracledb.DatabaseError as e:
        error, = e.args
        print("There was a problem connecting:\n")
        print("Code:", error.code)
        print("Message:", error.message)
        exit(1)

    except Exception as ex:
        print("Unexpected error:", ex)
        exit(1)

# SCHEMA OPERATIONS
def drop_existing_tables(cursor):
    """Drops tables safely in the correct dependency order."""
    tables = ["Blacklist", "History", "Devices", "Users"]

    for table in tables:
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


def create_users_table(cursor):
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


def create_devices_table(cursor):
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


def create_history_table(cursor):
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


def create_blacklist_table(cursor):
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


def setup_schema(connection):
    # Main schema setup routine.
    with connection.cursor() as cursor:
        drop_existing_tables(cursor)
        create_users_table(cursor)
        create_devices_table(cursor)
        create_history_table(cursor)
        create_blacklist_table(cursor)

