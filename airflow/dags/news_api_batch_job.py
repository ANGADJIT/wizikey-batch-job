'''
The following DAG Performs fetching the news articles from News Org API and than Uplaod to Local S3 Storage 
Named as Minio. Please Go Through the README.MD thoroughly Do Follow all the instruction in that so you can test
the dag.  
'''

from airflow.decorators import dag, task
from datetime import datetime, timedelta
from airflow.models import Variable
from typing import Generator
import requests
from requests import Response
import json
from minio import Minio
from itertools import islice
from datetime import datetime
from os import listdir


# Default AIRFLOW Args
default_agrs: dict = {
    'owner': 'angadjit-singh',
    'retries': 5,
    'retry_delay': timedelta(seconds=5)
}

# The following method send's email if task fails
def on_failure_task_callback(context):
    print(f"Task {context['task_instance'].task_id} failed. check logs")


# This Dag starts from 17 Jan,2024 Runs Every day
@dag(
    dag_id='news-api-batch-job',
    start_date=datetime(year=2024,day=17,month=1),
    description='This Batch Job Gets data every 30 minutes and store news data in AWS S3',
    schedule_interval='@daily',
    default_args=default_agrs,
    catchup=False,
    on_failure_callback=on_failure_task_callback
)
def news_api_batch_job():

    # The following task gets data from API and put into file instead in memory
    @task()
    def fetch_articles() -> None:
        # Get all variables for News API
        API_KEY: str = Variable.get('API_KEY')
        TOPIC: str = Variable.get('TOPIC')
        BASE_URL: str = Variable.get('BASE_URL')

        # Make Url for GET Request 
        #! (Note) This all variables you have to set manually in airflow ADMIN Ui
        url: str = f'{BASE_URL}?q={TOPIC}&apiKey={API_KEY}'

        # Get Data and put in Generator
        response: Response = requests.get(url)

        if response.status_code != 200:
            raise Exception('Failed to fetch data from API')
        
        # Put Data In Generator
        articles: Generator = (article for article in response.json()['articles'])
        
        # Global list
        chunk_articles: list[dict] = None
        ptr: int = 1

        # Divide into chunks
        chunk_size = int(Variable.get('CHUNK_SIZE'))

        for chunk in iter(lambda: list(islice(articles, chunk_size)), []):
            chunk_articles = list(chunk)

            # Save to Tmp
            path: str = f'/tmp/articles-ptr-{ptr}.json'
            with open(path,'w') as file:
                json.dump(chunk_articles,file)
            
            # Remove previous articles 
            chunk_articles.clear()
            ptr += 1

    # This task will get data from Temp and upload this to S3 
    @task()
    def upload_articles():
        # Get all S3 Variables
        minio_bucket: str = Variable.get('BUCKET')
        minio_access_key: str = Variable.get('ACCESS_KEY')
        minio_secret_key: str = Variable.get('SECRET_KEY')
        minio_endpoint: str = Variable.get('S3_ENDPOINT')

        # Get client
        client = Minio(minio_endpoint, access_key=minio_access_key, secret_key=minio_secret_key, secure=False)

        # Get files name from local
        files: list[str] = listdir(path='/tmp/')
        date: str = str(datetime.now()).split(' ')[0]

        # Upload artciles according to date
        for file in files:
            if file.startswith('articles-ptr') and file.endswith('.json'):
                file_path: str = f'/tmp/{file}'
                key: str = f'{date}/{file}'
                client.fput_object(bucket_name=minio_bucket,object_name=key,file_path=file_path)
        
    # Execute task here
    fetch_articles()
    upload_articles()

news_api_batch_job = news_api_batch_job()