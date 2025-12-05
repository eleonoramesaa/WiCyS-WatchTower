from os import environ as env
import oracledb
from db_utils import connect_to_db

from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
    
app = Flask(__name__)
CORS(app)

## This is gettign arguments such as: /api/get_data?sql_query=
@app.route("/api/get_data")
def get_data():
    
    username = env.get("DB_USERNAME")
    password = env.get("DB_PASSWORD")
    wallet_pw = ""

    # Checking coonection
    try:
        connection = connect_to_db(username, password, wallet_pw)
                
    except oracledb.DatabaseError as e:
        error, = e.args

        return jsonify({
        "error": "Database connection failed",
        "code": error.code,
        "message": error.message
        }), 500

    sql_query = request.args.get("sql_query")
    
    if not sql_query:
        return jsonify({
            "error": "Missing required parameters",
            "required": ["sql_query"]
        }), 400

    # running sql statement
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            result = cursor.fetchall()

    except oracledb.DatabaseError as e:
        error = e.args[0]
        return jsonify({
            "error": "Query failed",
            "code": error.code if hasattr(error, "code") else None,
            "message": error.message if hasattr(error, "message") else str(e),
            "sql": sql_query
        }), 500


    finally:
        try:
            connection.close()
        except:
            pass

    return jsonify(result)


@app.route("/")
def home():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Website</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #f5f5f5;
            }
            h1 {
                color: #333;
            }
        </style>
    </head>
    <body>
        <h1>API Website</h1>
    </body>
    </html>
    """
    return make_response(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 5000))