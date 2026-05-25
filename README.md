# Largest Banks ETL Pipeline

## Overview

This project implements a modular ETL (Extract, Transform, Load) pipeline in Python to collect and process data on the world's largest banks by market capitalization.

The pipeline:
- Extracts bank market capitalization data from an archived Wikipedia page
- Cleans and transforms the extracted data
- Converts USD market capitalization values into GBP, EUR, and INR
- Saves processed data into CSV and SQLite database formats
- Executes SQL queries against the generated database
- Logs ETL progress throughout execution

---

## Technologies Used

- Python
- pandas
- requests
- BeautifulSoup4
- SQLite3
- SQL
- pathlib
- datetime

---

## Project Structure

```text
largest-banks-etl-pipeline/
│
├── main.py
├── exchange_rate.csv
├── Largest_banks_data.csv
├── Banks.db
├── code_log.txt
├── requirements.txt
└── README.md
