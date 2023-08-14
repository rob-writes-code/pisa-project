from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import Variable
import logging
import pandas as pd

# List of country codes to process
country_codes = [
    'alb','arg','aus','aut','bel','bgr','bih','blr','bra','brn',
    'can','che','chl','col','cri','cze','deu','dnk','dom','esp'
    ]

# Task to get the offset for each country in analytical db
# This acts as a bookmark, to extract only new submissions of data
def get_offset():
    src_db = PostgresHook(postgres_conn_id="analytical_db_rds")
    src_conn = src_db.get_conn()

    for country_code in country_codes:
        try:
            df = pd.read_sql(
                f''' 
                SELECT COUNT(*)
                FROM pisa
                WHERE cnt = '{country_code.upper()}';
                ''',
                src_conn
            )
            count = int(df['count'])
        except Exception as e:
            count = 0
            logging.info(f"Reason for failure: {e}")

        # Set the offset as a Variable to be used in a later Task
        Variable.set(f'{country_code}_count', count)
    src_conn.close()

# Task to extract from source databases and push data to Xcom
def extract(**kwargs):
    for country_code in country_codes:
        src_db = PostgresHook(postgres_conn_id=f"seta-{country_code}")
        src_conn = src_db.get_conn()
        count = Variable.get(f'{country_code}_count')

        # Fetch data using the offset to only get new submissions
        df = pd.read_sql(
            f'''
            SELECT id, cnt, escs, tmins, belong, durecec
            FROM responses
            OFFSET {count};
            ''',
            src_conn
        )

        # Push extracted data to Xcom for use in next Task
        kwargs['ti'].xcom_push(key=country_code, value=df.to_json())
        logging.info(f"Extract function: pushing dataset to Xcom")
    src_conn.close()


# Task to load data into analytical db
def load(**kwargs):
    target_db = PostgresHook(postgres_conn_id="analytical_db_rds")

    # Create table in analytical db with composite primary key to prevent duplication of data
    create_posts_table = '''
    CREATE TABLE IF NOT EXISTS pisa (
    id INT,
    cnt TEXT,
    escs NUMERIC(15, 4),
    tmins INT,
    belong NUMERIC(15, 4),
    durecec INT,
    time_submitted TIMESTAMP,
    PRIMARY KEY (id, cnt)
    );
    '''

    # Insert data into table, update existing entry with new values if conflict
    load_post_data = '''
    INSERT INTO pisa (id, cnt, escs, tmins, belong, durecec, time_submitted)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id, cnt) DO UPDATE SET
    escs=EXCLUDED.escs,
    tmins=EXCLUDED.tmins,
    belong=EXCLUDED.belong,
    durecec=EXCLUDED.durecec,
    time_submitted=EXCLUDED.time_submitted;
    '''
    
    # Pull data from Xcom and load into DataFrame
    for country_code in country_codes:
        df = pd.read_json(kwargs['ti'].xcom_pull(key=country_code))
        logging.info(f"Load function: pulled dataset from Xcom. DataFrame shape is {df.shape}")

        columns = ['id', 'cnt', 'escs', 'tmins', 'belong', 'durecec']

        df = df[columns]
        df['time_submitted'] = datetime.now()

        # change 'NA' values to None
        for column in columns:
            df[column] = df[column].replace('NA', None)

        # Load data into analytical db
        with target_db.get_conn() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(create_posts_table)
                    for row in df.itertuples():
                        data = row[1:]
                        logging.info(f'Loading data: {data}')
                        cursor.execute(load_post_data, data)
                    conn.commit()
    conn.close()

# Define the DAG
dag = DAG(
    "pisa_dag",
    description="Extracts data from seta databases and moves to analytical db",
    schedule_interval=timedelta(seconds=30),
    start_date=datetime(2023, 8, 2),
    catchup=False,
    max_active_runs=1,
    tags=["PISA"]
)

# Define tasks
get_offset_task = PythonOperator(
    task_id="get_offset_task",
    python_callable=get_offset,
    provide_context=True,
    dag=dag
)

extract_task = PythonOperator(
    task_id="extract_task",
    python_callable=extract,
    provide_context=True,
    dag=dag
)

loading_task = PythonOperator(
    task_id="load_to_analytical_db",
    python_callable=load,
    provide_context=True,
    dag=dag
)

# Set order/flow of tasks
get_offset_task >> extract_task >> loading_task