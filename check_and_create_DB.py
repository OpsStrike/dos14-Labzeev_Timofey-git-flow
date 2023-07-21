import psycopg2
import datetime

with open("secrets_decrypted.yml", "r") as f:
    password = f.read()

host = "localhost"
port = 5432
database = "omegabank"
username = "postgres"

def check_and_create_database():
    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password
        )
        print(f"Подключено к базе данных '{database}'.")
        connection.close()
    except psycopg2.OperationalError as e:
        error_message = f"{datetime.datetime.now()} - Ошибка: {e}"
        with open("errors_DB.yml", "a") as error_file:
            error_file.write(error_message + "\n")
        try:
            connection = psycopg2.connect(
                host=host,
                port=port,
                user=username,
                password=password
            )
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE {database};")
            print(f"База данных '{database}' успешно создана.")
            cursor.close()
            connection.close()

            database_created = True

        except psycopg2.ProgrammingError as e:
            error_message = f"{datetime.datetime.now()} - Ошибка при создании базы данных: {e}"
            with open("errors_DB.yml", "a") as error_file:
                error_file.write(error_message + "\n")
    
    if database_created:
        try:
            connection = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password
            )
            cursor = connection.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Credits (
                    credit_id PRIMARY KEY,
                    client_id INTEGER,
                    percent NUMERIC,
                    sum NUMERIC,
                    term INTEGER,
                    periods INTEGER
                );
            """)
            print("Таблица 'Credits' успешно создана.")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Deposits (
                    deposit_id PRIMARY KEY,
                    client_id INTEGER,
                    amount NUMERIC,
                    duration INTEGER
                );
            """)
            print("Таблица 'Deposits' успешно создана.")

            cursor.close()
            connection.commit()
            connection.close()
        except psycopg2.ProgrammingError as e:
            error_message = f"{datetime.datetime.now()} - Ошибка при создании таблиц: {e}"
            with open("errors_DB.yml", "a") as error_file:
                error_file.write(error_message + "\n")

if __name__ == "__main__":
    check_and_create_database()

