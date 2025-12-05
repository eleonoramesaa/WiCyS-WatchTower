import getpass
import oracledb
import os

# -------------------------------------------------------------------
#  CREDENTIAL COLLECTION
# -------------------------------------------------------------------

def get_credentials():
    print("Getting credentials")
    username = input("Enter Oracle username: ")
    password = getpass.getpass("Enter password: ")
    wallet_password = getpass.getpass("Enter wallet password (if applicable, else leave blank): ")
    return username, password, wallet_password


def connect_to_db(username, password, wallet_password):
    try:
        # Correct: go up 3 levels (backend → website → src → WiCyS-WatchTower)
        PROJECT_ROOT = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../..")
        )

        wallet_path = os.path.join(PROJECT_ROOT, "Wallet_WatchTowerDev")

        if not os.path.exists(wallet_path):
            print("\nERROR: Oracle wallet directory not found:")
            print(wallet_path)
            raise FileNotFoundError(wallet_path)
        
        conn = oracledb.connect(
            user=username,
            password=password,
            dsn="watchtowerdev_low",
            config_dir=wallet_path,
            wallet_location=wallet_path,
            wallet_password=wallet_password
        )

        print("Successfully connected to Oracle Database\n")
        return conn

    except oracledb.DatabaseError as e:
        error, = e.args
        print("\nThere was a problem connecting:")
        print("Code:", error.code)
        print("Message:", error.message)
        exit(1)


# -------------------------------------------------------------------
#  SCHEMA CREATION UTILITIES
# -------------------------------------------------------------------

def drop_existing_tables(cursor):
    """Drops tables safely in correct dependency order."""
    # Child tables first, then parents
    tables = ["History", "Blacklist", "Devices", "Users"]
    for table in tables:
        cursor.execute(f"""
            BEGIN
                EXECUTE IMMEDIATE 'DROP TABLE {table} CASCADE CONSTRAINTS';
            EXCEPTION WHEN OTHERS THEN
                IF SQLCODE != -942 THEN RAISE; END IF;
            END;
        """)
    print("Old tables dropped (if existed).")


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
    print("Users table created.")


def create_devices_table(cursor):
    cursor.execute("""
        CREATE TABLE Devices (
            id                  NUMBER GENERATED ALWAYS AS IDENTITY,
            name                VARCHAR2(255) NOT NULL,
            os                  VARCHAR2(255),
            type                VARCHAR2(255),
            mac_address         VARCHAR2(255) NOT NULL,
            user_id             NUMBER NOT NULL,
            suspicious_device   NUMBER(1,0) DEFAULT 0 NOT NULL,
            CONSTRAINT pk_devices PRIMARY KEY (id),
            CONSTRAINT uq_devices_mac UNIQUE (mac_address),
            CONSTRAINT fk_devices_users FOREIGN KEY (user_id)
                REFERENCES Users(id) ON DELETE CASCADE
        )
    """)
    print("Devices table created.")


def create_history_table(cursor):
    cursor.execute("""
        CREATE TABLE History (
            device_id           NUMBER NOT NULL,
            datetime            TIMESTAMP NOT NULL,
            outgoing_ip         VARCHAR2(255),
            packet_size         NUMBER,
            connection_status   VARCHAR2(255),
            threat              NUMBER(1,0) DEFAULT 0 NOT NULL,
            payload_size        NUMBER,
            device_type         VARCHAR2(255),
            CONSTRAINT pk_history PRIMARY KEY (device_id, datetime),
            CONSTRAINT fk_history_devices FOREIGN KEY (device_id)
                REFERENCES Devices(id) ON DELETE CASCADE
        )
    """)
    print("History table created.")


def create_blacklist_table(cursor):
    cursor.execute("""
        CREATE TABLE Blacklist (
            device_id   NUMBER,
            blocked     NUMBER(1,0) DEFAULT 0 NOT NULL,
            CONSTRAINT pk_blacklist PRIMARY KEY (device_id),
            CONSTRAINT fk_blacklist_devices FOREIGN KEY (device_id)
                REFERENCES Devices(id) ON DELETE CASCADE
        )
    """)
    print("Blacklist table created.")


def setup_schema(connection):
    with connection.cursor() as cursor:
        drop_existing_tables(cursor)
        create_users_table(cursor)
        create_devices_table(cursor)
        create_history_table(cursor)
        create_blacklist_table(cursor)

    # ---- Grant table privileges to dev_team_role ----
    grant_table_privileges(connection)


# -------------------------------------------------------------------
#  USER + DEVICE MANAGEMENT
# -------------------------------------------------------------------

def ensure_user_exists(cursor, username="default_user"):
    """Ensures the default simulator user exists."""
    cursor.execute("SELECT id FROM Users WHERE username = :u", {"u": username})
    row = cursor.fetchone()
    if row:
        return row[0]

    id_var = cursor.var(oracledb.NUMBER)

    try:
        cursor.execute("""
            INSERT INTO Users (username, password)
            VALUES (:u, :p)
            RETURNING id INTO :id
        """, {
            "u": username,
            "p": "WatchTower123!",
            "id": id_var
        })
    except Exception as e:
        print("\nUSER INSERT ERROR:")
        print(" - username:", username)
        print(" - Oracle error:", e)
        raise

    new_id = id_var.getvalue()
    return int(new_id[0]) if new_id else None


def ensure_device_exists(cursor, device_name, mac, os_value, d_type, suspicious_flag):
    """
    Returns device_id, creating entry if needed.
    Also updates OS and suspicious_device for existing devices.
    """
    # Normalize suspicious_flag to 0 or 1
    suspicious_flag = 1 if suspicious_flag else 0

    cursor.execute("""
        SELECT id, os, suspicious_device
        FROM Devices
        WHERE LOWER(TRIM(mac_address)) = LOWER(TRIM(:m))
    """, {"m": mac})
    row = cursor.fetchone()

    if row:
        device_id, existing_os, existing_suspicious = row

        # If new telemetry says this device is suspicious, mark it
        if suspicious_flag == 1 and existing_suspicious == 0:
            cursor.execute("""
                UPDATE Devices
                SET suspicious_device = 1
                WHERE id = :id
            """, {"id": device_id})

        # If we have a better or new OS value, update it
        if os_value and (existing_os is None or existing_os != os_value):
            cursor.execute("""
                UPDATE Devices
                SET os = :o
                WHERE id = :id
            """, {"o": os_value, "id": device_id})

        return device_id

    # New device case
    user_id = ensure_user_exists(cursor)

    id_var = cursor.var(oracledb.NUMBER)

    try:
        cursor.execute("""
            INSERT INTO Devices (name, os, type, mac_address, user_id, suspicious_device)
            VALUES (:n, :o, :t, :m, :u, :s)
            RETURNING id INTO :id
        """, {
            "n": device_name,
            "o": os_value,
            "t": d_type,
            "m": mac,
            "u": user_id,
            "s": suspicious_flag,
            "id": id_var
        })
    except Exception as e:
        print("\nDEVICE INSERT ERROR:")
        print(" - device_name:", device_name)
        print(" - mac:", mac)
        print(" - os_value:", os_value)
        print(" - suspicious_flag:", suspicious_flag)
        print(" - user_id:", user_id)
        print(" - Oracle error:", e)
        raise

    new_id = id_var.getvalue()
    return int(new_id[0]) if new_id else None


# -------------------------------------------------------------------
#  HISTORY AND BLACKLIST UPDATES
# -------------------------------------------------------------------

def insert_history(cursor, device_id, source_ip, device_type, status, timestamp, threat=0, payload_size=None):
    """Writes a historical connection record."""

    # NEW LOGIC:
    # If 'threat' or suspicious flag indicates an issue → Warning
    if threat == 1 or status == "suspicious":
        connection_state = "Warning"
    else:
        connection_state = "Connected" if status == "active" else "Disconnected"

    cursor.execute("""
        INSERT INTO History (
            device_id, datetime, outgoing_ip, device_type, connection_status, threat, payload_size
        )
        VALUES (
            :d,
            TO_TIMESTAMP(:t, 'YYYY-MM-DD HH24:MI:SS'),
            :ip,
            :dt, 
            :s,
            :thr,
            :ps
        )
    """, {
        "d": device_id,
        "t": timestamp,
        "ip": source_ip,
        "dt": device_type,
        "s": connection_state,
        "thr": threat,
        "ps": payload_size,
    })



def update_blacklist(cursor, device_id, status, threat):
    """
    Block device if threat level exceeds threshold.
    Default threshold = 5.
    """
    THREAT_THRESHOLD = 5

    # threat-based override
    if threat >= THREAT_THRESHOLD:
        blocked = 1
    else:
        blocked = 0 if status == "active" else 1

    cursor.execute("SELECT device_id FROM Blacklist WHERE device_id = :d", {"d": device_id})
    row = cursor.fetchone()

    if row:
        cursor.execute("""
            UPDATE Blacklist
            SET blocked = :b
            WHERE device_id = :d
        """, {"b": blocked, "d": device_id})
    else:
        cursor.execute("""
            INSERT INTO Blacklist (device_id, blocked)
            VALUES (:d, :b)
        """, {"d": device_id, "b": blocked})



# -------------------------------------------------------------------
#  MASTER TELEMETRY INSERT
# -------------------------------------------------------------------

def insert_telemetry(connection, payload):
    """
    Inserts:
    - device existence check or creation
    - history row (with threat + payload size)
    - threat-based blacklist status update
    then commits.
    """
    with connection.cursor() as cursor:

        # Device lookup or creation
        device_id = ensure_device_exists(
            cursor,
            payload["device_id"],
            payload["mac"],
            payload.get("os"),
            payload.get("suspicious_device", 0)
        )

        # Insert History
        insert_history(
            cursor,
            device_id,
            payload["source_ip"],
            payload["device_type"],
            payload["status"],
            payload["timestamp"],
            payload["threat"],
            payload["payload_size"]
        )

        # Threat-based Blacklist update
        update_blacklist(
            cursor,
            device_id,
            payload["status"],
            payload["threat"]
        )

    connection.commit()


# -------------------------------------------------------------------
#  MAINTENANCE UTILITIES
# -------------------------------------------------------------------

def wipe_tables(connection):
    """
    Deletes all rows from all tables in the correct dependency order.
    Safe for tables with foreign keys.
    """
    with connection.cursor() as cursor:
        # Child tables first
        cursor.execute("DELETE FROM History")
        cursor.execute("DELETE FROM Blacklist")

        # Then parent tables
        cursor.execute("DELETE FROM Devices")
        cursor.execute("DELETE FROM Users")

    connection.commit()
    print("All table rows wiped successfully.")


def drop_public_synonym_if_exists(cursor, synonym_name):
    """
    Drops a public synonym only if it exists (Option 2 pattern).
    """
    cursor.execute(f"""
        DECLARE
            v_count INTEGER;
        BEGIN
            SELECT COUNT(*)
            INTO v_count
            FROM ALL_SYNONYMS
            WHERE OWNER = 'PUBLIC'
              AND SYNONYM_NAME = UPPER('{synonym_name}');

            IF v_count > 0 THEN
                EXECUTE IMMEDIATE 'DROP PUBLIC SYNONYM {synonym_name}';
            END IF;
        END;
    """)


def create_public_synonym(cursor, synonym_name, schema_name, table_name):
    """
    Creates a public synonym pointing to schema.table.
    """
    cursor.execute(f"""
        CREATE PUBLIC SYNONYM {synonym_name}
        FOR {schema_name}.{table_name}
    """)


def create_public_synonyms(connection, schema_name="DEV1"):
    """
    Creates public synonyms so users can query tables without schema prefixes.
    Example: SELECT * FROM devices;
    For each table, drop the synonym if it exists and create a fresh one.
    """
    tables = ["Users", "Devices", "History", "Blacklist"]

    with connection.cursor() as cursor:
        for table in tables:
            synonym_name = table.lower()

            # Drop only if exists (Option 2)
            drop_public_synonym_if_exists(cursor, synonym_name)

            # Create synonym
            create_public_synonym(cursor, synonym_name, schema_name, table)

            print(f"Synonym created: {synonym_name} -> {schema_name}.{table}")

    connection.commit()
    print("All public synonyms created successfully.")

def grant_table_privileges(connection, schema_name="DEV1", role_name="DEV_TEAM_ROLE"):
    """
    Grants SELECT, INSERT, UPDATE, DELETE on each table in this schema
    to the given role. Must be run as the schema owner (e.g., DEV1).
    """
    tables = ["Users", "Devices", "History", "Blacklist"]

    with connection.cursor() as cursor:
        for table in tables:
            fq_table = f"{schema_name}.{table}"

            cursor.execute(f"""
                GRANT SELECT, INSERT, UPDATE, DELETE
                ON {fq_table}
                TO {role_name}
            """)

            print(f"Granted DML privileges on {fq_table} to role {role_name}.")

    connection.commit()
    print("\nAll privileges granted successfully.\n")
