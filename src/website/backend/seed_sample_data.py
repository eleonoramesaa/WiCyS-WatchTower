from datetime import datetime
from db_utils import get_credentials, connect_to_db

# -----------------------------
# USERS
# -----------------------------
def get_or_create_user(cursor, username):
    cursor.execute(
        "SELECT id FROM dev1.Users WHERE username = :u",
        {"u": username}
    )
    row = cursor.fetchone()
    if row:
        return row[0]

    cursor.execute(
        """
        INSERT INTO dev1.Users (username, password)
        VALUES (:u, :p)
        """,
        {"u": username, "p": "demo-password"}
    )

    cursor.execute(
        "SELECT id FROM dev1.Users WHERE username = :u",
        {"u": username}
    )
    return cursor.fetchone()[0]


# -----------------------------
# DEVICES
# -----------------------------
def insert_device(cursor, name, os, manufacturer, mac, port, user_id):
    cursor.execute(
        """
        INSERT INTO dev1.Devices (name, os, manufacturer, mac_address, port, user_id)
        VALUES (:name, :os, :man, :mac, :port, :uid)
        """,
        {
            "name": name,
            "os": os,
            "man": manufacturer,
            "mac": mac,
            "port": port,
            "uid": user_id,
        },
    )


# -----------------------------
# HISTORY
# -----------------------------
def insert_history_sample(cursor, device_id, status):
    now = datetime.now()
    cursor.execute(
        """
        INSERT INTO dev1.History (
            device_id, datetime, outgoing_ip, incoming_ip,
            network_protocol, connection_status
        )
        VALUES (
            :did, :dt, :out_ip, :in_ip,
            :proto, :status
        )
        """,
        {
            "did": device_id,
            "dt": now,
            "out_ip": "1.2.3.4",
            "in_ip": "10.0.0.5",
            "proto": "TCP",
            "status": status,
        },
    )


# -----------------------------
# MAIN SCRIPT
# -----------------------------
def main():
    username, password, wallet_pw = get_credentials()
    conn = connect_to_db(username, password, wallet_pw)

    try:
        cur = conn.cursor()

        # 1 test user inside dev1 schema
        user_id = get_or_create_user(cur, "demo_user")

        # Four example devices
        devices = [
            ("Personal PC", "Windows", "Dell", "00:11:22:33:44:55", 5001),
            ("Smart TV", "Tizen", "Samsung", "00:11:22:33:44:66", 5002),
            ("Security Camera", "Linux", "Reolink", "00:11:22:33:44:77", 5003),
            ("Network Printer", "Embedded", "HP", "00:11:22:33:44:88", 5004),
        ]

        device_ids = []
        for name, os, man, mac, port in devices:
            insert_device(cur, name, os, man, mac, port, user_id)

            cur.execute(
                "SELECT id FROM dev1.Devices WHERE mac_address = :mac",
                {"mac": mac}
            )

            device_ids.append(cur.fetchone()[0])

        # Add a history row for each device
        for did in device_ids:
            insert_history_sample(cur, did, "Connected")

        conn.commit()
        print("Sample user, devices, and history inserted")

    finally:
        conn.close()
        print("Connection closed")


if __name__ == "__main__":
    main()
