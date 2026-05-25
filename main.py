# Code for ETL operations on Country-GDP data

# Importing the required libraries
from pathlib import Path
from datetime import datetime
import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup


def extract(url, table_attribs):
    """
    Extract GDP table from the website and return it as a DataFrame.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    tables = soup.find_all("table")
    target_table = tables[0]
    rows = target_table.find_all("tr")

    records = []

    for row in rows:
        cols = row.find_all("td")

        if len(cols) < 3:
            continue

        record = {
            "Rank": cols[0].get_text(" ", strip=True),
            "Bank name": cols[1].get_text(" ", strip=True),
            "MC_USD_Billion": cols[2].get_text(" ", strip=True),
        }

        records.append(record)

    df = pd.DataFrame(records, columns=table_attribs)

    return df
def read_exchange_rate(csv_path):
    """
    Read exchange rate data from a CSV file and return it as a DataFrame.
    """

    df_exchange = pd.read_csv(csv_path)
    print(df_exchange)
    return df_exchange

def transform(df, df_exchange):
    """
    Convert market cap from USD billion to GBP, EUR, and INR billion.
    """

    df["MC_USD_Billion"] = (
        df["MC_USD_Billion"]
        .str.replace(",", "", regex=False)
        .astype(float)
    )

    rates = dict(zip(df_exchange["Currency"], df_exchange["Rate"]))

    df["MC_GBP_Billion"] = (df["MC_USD_Billion"] * rates["GBP"]).round(2)
    df["MC_EUR_Billion"] = (df["MC_USD_Billion"] * rates["EUR"]).round(2)
    df["MC_INR_Billion"] = (df["MC_USD_Billion"] * rates["INR"]).round(2)

    return df


def load_to_csv(df, csv_path):
    """
    Save the final DataFrame as a CSV file.
    """

    df.to_csv(csv_path, index=False)


def load_to_db(df, sql_connection, table_name):
    """
    Save the final DataFrame as a SQLite database table.
    """

    df.to_sql(table_name, sql_connection, if_exists="replace", index=False)


def run_query(query_statement, sql_connection):
    """
    Run a SQL query on the database and print the output.
    """

    query_output = pd.read_sql_query(query_statement, sql_connection)
    print(query_output)


def log_progress(message):
    """
    Log progress message with timestamp into a log file.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("code_log.txt", "a") as log_file:
        log_file.write(f"{timestamp} : {message}\n")


# Main ETL execution

url = "https://web.archive.org/web/20230908091635/https://en.wikipedia.org/wiki/List_of_largest_banks"

table_attribs = ["Rank", "Bank name", "MC_USD_Billion"]

csv_path = Path(".") / "./Largest_banks_data.csv"
db_name = "Banks.db"
table_name = "Largest_banks"


log_progress("Preliminaries complete. Initiating ETL process")

log_progress("Data extraction started")
df = extract(url, table_attribs)
log_progress("Data extraction complete. Initiating Transformation process")

df_exchange = read_exchange_rate("exchange_rate.csv")
df = transform(df, df_exchange)
log_progress("Data transformation complete. Initiating Loading process")

load_to_csv(df, csv_path)
log_progress("Data saved to CSV file")

log_progress("SQL Connection initiated")
with sqlite3.connect(db_name) as conn:
    load_to_db(df, conn, table_name)
    log_progress("Data loaded to Database as a table, Executing queries")

    query_statement = f"""
    SELECT *
    FROM {table_name};
    """
    run_query(query_statement, conn)
    log_progress("Process Complete")

log_progress("Server Connection closed")