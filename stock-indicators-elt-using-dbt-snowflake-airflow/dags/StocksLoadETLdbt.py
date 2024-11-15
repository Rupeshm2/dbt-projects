
from airflow import DAG
from airflow.models import Variable
from airflow.decorators import task
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.utils.task_group import TaskGroup
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from datetime import timedelta
from datetime import datetime
import snowflake.connector
import requests


def return_snowflake_conn():

    # Initialize the SnowflakeHook
    hook = SnowflakeHook(snowflake_conn_id='snowflake_conn')
    
    # Execute the query and fetch results
    conn = hook.get_conn()
    return conn.cursor()


@task
def extract_get_data(symbol):
  vantage_api_key = Variable.get("vantage_api_key")
  url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={vantage_api_key}'
  r = requests.get(url)
  data = r.json()
  results = []
  for d in data["Time Series (Daily)"]:
    temp_dict = data["Time Series (Daily)"][d]
    temp_dict["date"] = d   # added the date to the dict
    temp_dict["symbol"] = symbol #Added sybols to dictionary
    results.append(temp_dict)

  return results

@task
def transform_90_days(records):
  date_90_days_ago = datetime.now() - timedelta(days=90)
  date_90_days_ago_str = date_90_days_ago.strftime("%Y-%m-%d")
  results_90_days = [r for r in records if r["date"] >= date_90_days_ago_str]
  return results_90_days

@task
def create_table(con, table):

    con.execute(f"""
  CREATE TABLE IF NOT EXISTS {table} (
  symbol varchar,
  price_date date,
  open float,
  high float,
  low float,
  close float,
  volume integer,
  load_timestamp TIMESTAMP_NTZ(9),
  primary key (price_date, symbol)
  );""")

@task
def load_records(con, table, results, symbol):
  try:

    con.execute("BEGIN;")
    count = 0
    for r in results:
      symbol = r["symbol"]
      open = r["1. open"]
      high = r["2. high"]
      low = r["3. low"]
      close = r["4. close"]
      volume = r["5. volume"]
      date = r["date"]
      delete_sql = f"DELETE FROM {table} A WHERE A.price_date = '{date}' AND A.symbol = '{symbol}';"
      # print(delete_sql)
      con.execute(delete_sql)
      insert_sql = f"INSERT INTO {table} (symbol, open, high, low, close, volume, price_date, load_timestamp) VALUES ('{symbol}', {open}, {high}, {low}, {close}, {volume}, '{date}', current_timestamp);"
      # print(insert_sql)
      con.execute(insert_sql)
      count += 1
    con.execute("COMMIT;")
  except Exception as e:
        con.execute("ROLLBACK;")
        print(e)
        raise e


with DAG(dag_id = 'StockdLoadETL_for_dbt', schedule_interval='@daily',
         start_date = datetime(2024,10,9),catchup=False,
         tags=['Stocks', 'ETL'],) as dag:
    
    symbol1 = Variable.get("Amazon_symbl")
    symbol2 = Variable.get("Walmart_symbl")
    target_table = Variable.get("target_table")
    cur = return_snowflake_conn() 

    with TaskGroup(symbol1) as stock1:
        extract_get_data_1 = extract_get_data(symbol1)
        create_table(cur, target_table)
        transform_90_days_1 = transform_90_days(extract_get_data_1)
        load_records(cur, target_table, transform_90_days_1, symbol1)

    with TaskGroup(symbol2) as stock2:
        extract_get_data_2 = extract_get_data(symbol2)
        transform_90_days_2 = transform_90_days(extract_get_data_2)
        load_records(cur, target_table, transform_90_days_2, symbol2)

#GIve trigger to dbt execution dag
dbt_trigger = TriggerDagRunOperator(
  task_id="dbt_trigger",
  trigger_dag_id="BuildELT_dbt",
  execution_date = '{{ ds }}',
  reset_dag_run = True
)
        
stock1 >> stock2 >> dbt_trigger
