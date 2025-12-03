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
            dsn="watchtowerdev_low",
            config_dir="./Wallet_WatchTowerDev",
            wallet_location="./Wallet_WatchTowerDev",
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


# SCHEMA CREATION

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
            mac_address     VARCHAR2(255) NOT NULL,
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
            connection_status   VARCHAR2(255),
            CONSTRAINT pk_history PRIMARY KEY (device_id, datetime),
            CONSTRAINT chk_history_status CHECK (connection_status IN ('Connected', 'Disconnected')),
            CONSTRAINT fk_history_devices FOREIGN KEY (device_id)
                REFERENCES Devices(id)
                ON DELETE CASCADE
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


# INSERT LOGIC FOR TELEMETRY

def ensure_user_exists(cursor, username="default_user"):
    """Ensures the default user exists (since simulator doesn’t track real user accounts)."""
    cursor.execute("SELECT id FROM Users WHERE username = :u", [username])
    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute("""
        INSERT INTO Users (username, password)
        VALUES (:u, 'password')
        RETURNING id INTO :id
    """, {"u": username, "id": cursor.var(oracledb.NUMBER)})

    return cursor.getimplicitresults()[0][0]


def ensure_device_exists(cursor, device_name, mac, device_type):
    """Return device_id, creating entry if needed."""
    cursor.execute("SELECT id FROM Devices WHERE mac_address = :m", [mac])
    row = cursor.fetchone()
    if row:
        return row[0]

    user_id = ensure_user_exists(cursor)  # assign to default user

    cursor.execute("""
        INSERT INTO Devices (name, os, mac_address, user_id)
        VALUES (:n, :o, :m, :u)
        RETURNING id INTO :id
    """, {
        "n": device_name,
        "o": device_type,
        "m": mac,
        "u": user_id,
        "id": cursor.var(oracledb.NUMBER)
    })

    return cursor.getimplicitresults()[0][0]


def insert_history(cursor, device_id, source_ip, status, timestamp):
    connection_state = "Connected" if status == "active" else "Disconnected"

    cursor.execute("""
        INSERT INTO History (device_id, datetime, outgoing_ip, connection_status)
        VALUES (:d, TO_TIMESTAMP(:t, 'YYYY-MM-DD HH24:MI:SS'), :ip, :s)
    """, {
        "d": device_id,
        "t": timestamp,
        "ip": source_ip,
        "s": connection_state
    })


def update_blacklist(cursor, device_id, status):
    """Mark device as blocked if compromised or suspicious."""
    blocked_flag = 1 if status != "active" else 0

    cursor.execute("SELECT device_id FROM Blacklist WHERE device_id = :d", [device_id])
    row = cursor.fetchone()

    if row:
        cursor.execute("UPDATE Blacklist SET blocked = :b WHERE device_id = :d",
                       {"b": blocked_flag, "d": device_id})
    else:
        cursor.execute("INSERT INTO Blacklist (device_id, blocked) VALUES (:d, :b)",
                       {"d": device_id, "b": blocked_flag})


def insert_telemetry(connection, payload):
    """
    Main function to be called from the simulator.
    Example payload keys:
      device_id, source_ip, mac, device_type, current_load, status, timestamp
    """
    with connection.cursor() as cursor:
        device_id = ensure_device_exists(
            cursor,
            device_name=payload["device_id"],
            mac=payload["mac"],
            device_type=payload["device_type"]
        )

        insert_history(
            cursor,
            device_id=device_id,
            source_ip=payload["source_ip"],
            status=payload["status"],
            timestamp=payload["timestamp"]
        )

        update_blacklist(
            cursor,
            device_id=device_id,
            status=payload["status"]
        )

    connection.commit()
