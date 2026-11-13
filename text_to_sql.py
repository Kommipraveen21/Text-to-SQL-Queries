
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# 1. Get the project folder path
BASE_DIR = Path(__file__).resolve().parent

# 2. Load environment variables
load_dotenv(BASE_DIR / ".env")

# 3. Get Gemini API key
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Gemini API key not found. Check your .env file.")

# 4. Connect to Gemini
client = genai.Client(api_key=API_KEY)
print("Gemini API connected successfully!")

# 5. Database file path
DB_PATH = BASE_DIR / "database" / "company.db"

if DB_PATH.exists():
    print("Database connected successfully!")
else:
    raise FileNotFoundError("Database file not found!")


# 6. Get database schema
def get_database_schema():

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name, sql
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
    """)

    tables = cursor.fetchall()
    connection.close()

    schema = ""

    for table_name, table_sql in tables:
        schema += table_sql + "\n"

    return schema


# 7. Generate SQL using Gemini
def generate_sql(question):

    schema = get_database_schema()

    prompt = f"""
    You are an expert SQLite SQL developer.

    Database schema:
    {schema}

    User question:
    {question}

    Instructions:
    1. Understand the user's question carefully.
    2. Generate only one valid SQLite SELECT query.
    3. Use only the tables and columns available in the schema.
    4. Handle common spelling mistakes when the intended meaning is clear.
    5. Use correct database values when filtering.
    6. Use JOIN when information is needed from multiple tables.
    7. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, or CREATE.
    8. Return only SQL without explanations or markdown.
    9. For case-insensitive text comparisons, use LOWER(column) = LOWER('value').
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    sql_query = response.text.strip()

    return sql_query


# 8. Execute SQL query
def execute_sql(sql_query):

    sql_query = sql_query.strip()

    if sql_query.startswith("```"):
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

    if not sql_query.upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed!")

    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("PRAGMA query_only = ON")

        cursor = connection.cursor()
        cursor.execute(sql_query)

        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        return columns, rows

    finally:
        connection.close()


# 9. Main program

# 9. Main program

# 9. Main program
from prettytable import PrettyTable
from colorama import init, Fore, Style

# Initialize colors
init(autoreset=True)


if __name__ == "__main__":

    print(Fore.GREEN + "\n===================================")
    print(Fore.GREEN + "   Welcome to Text-to-SQL Chatbot")
    print(Fore.GREEN + "===================================")

    print("\nAvailable Commands:")
    print("1. Type 'schema' to view database structure")
    print("2. Type 'quit' or 'exit' to stop")
    print("3. Enter any question to generate SQL")

    # Display database schema at startup
    print(Fore.CYAN + "\nDatabase Schema:")
    print(get_database_schema())

    # Continuous question loop
    while True:

        question = input(Fore.YELLOW + "\nEnter your question: ").strip()

        # Exit command
        if question.lower() in ["quit", "exit"]:
            print(Fore.GREEN + "\nChatbot closed. Goodbye!")
            break

        # Schema command
        if question.lower() == "schema":
            print(Fore.CYAN + "\nDatabase Schema:")
            print(get_database_schema())
            continue

        # Empty question
        if not question:
            print(Fore.RED + "Please enter a question.")
            continue

        try:
            # Generate SQL
            sql = generate_sql(question)

            print(Fore.GREEN + "\nGenerated SQL:")
            print(sql)

            # Execute SQL
            columns, rows = execute_sql(sql)

            # Display results in a table
            print(Fore.GREEN + "\nQuery executed successfully!")

            table = PrettyTable()
            table.field_names = columns

            for row in rows:
                table.add_row(row)

            print(table)

            if not rows:
                print(Fore.YELLOW + "No records found.")

        except Exception as error:
            print(Fore.RED + "\nError: " + str(error))
