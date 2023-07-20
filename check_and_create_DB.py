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

        print(f"Connected to the database '{database}'.")
        connection.close()
        
    except psycopg2.Error as i:
        error_message = f"{datetime.datetime.now()} - Error: {e}"   
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
            print(f"Database '{database}' created successfully.")
            cursor.close()
            connection.close()
            
            database_created = True
            
        except psycopg2.Error as e:
            error_message = f"{datetime.datetime.now()} - Error while creating database: {e}"
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
            connection.autocommit = True
            cursor = connection.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Credits (
                    credit_id INTEGER PRIMARY KEY,
                    client_id INTEGER,
                    percent NUMERIC,
                    sum NUMERIC,
                    term INTEGER,
                    periods INTEGER
                );
            """)
            print("Table 'Credits' created successfully.")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Deposits (
                    deposit_id INTEGER PRIMARY KEY,
                    client_id INTEGER,
                    amount NUMERIC,
                    duration INTEGER
                );
            """)
            print("Table 'Deposits' created successfully.")

            cursor.close()
            connection.close()          
    
     	                  
if __name__ == "__main__":
    check_and_create_database()
    

