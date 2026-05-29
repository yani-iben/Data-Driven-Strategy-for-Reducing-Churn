import psycopg2
try:
    # Test connection to the default 'postgres' database
    # Leave password as empty string '' if you didn't set one
    conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="", port="5124")
    print("🚀 SUCCESS! Your local PostgreSQL server is reachable and passwordless.")
    conn.close()
except Exception as e:
    print("❌ CONNECTION FAILED. Here is the exact system error:")
    print(e)