# News Articles Batch Job 📰🔄

## Overview

This batch job is designed to fetch news articles based on a dynamic topic from the NewsOrg API, partition the data into chunks of configurable size, and store it in Minio S3 (locally replicated AWS S3). The data is organized in folders with the structure `{YYYY-MM-DD}/article-ptr-{partition-number}`. The entire process runs daily and is orchestrated using Apache Airflow, with Python as the core language.

## Setup

1. **Create Virtual Environment:**
   - Ensure Python 3.10.12 is installed.
   - Create a Python virtual environment.
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies:**
   - Use the `requirements.txt` file to install all required dependencies.
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Airflow:**
   - Edit the `setup.sh` script with your path, username, and email.
   - Run the setup script to configure Airflow for local development.
   ```bash
   bash setup.sh
   ```

4. **Start Airflow:**
   - Use the `start.sh` script to initiate the Airflow services.
   ```bash
   bash start.sh
   ```

5. **Airflow Variables:**
   - Configure the following variables in Airflow:
     - "ACCESS_KEY"
     - "API_KEY"
     - "BASE_URL"
     - "BUCKET"
     - "CHUNK_SIZE"
     - "S3_ENDPOINT"
     - "SECRET_KEY"
     - "TOPIC"

## Optimization 🚀

To optimize data fetching and processing:

- **Generator Usage:**
  - Data fetching is optimized using generators instead of storing data in lists. This approach is crucial when dealing with potentially millions of records, ensuring efficiency and resource optimization.

## Daily Workflow

1. **Fetch News Articles:**
   - Retrieve news articles from the NewsOrg API based on the dynamic topic.

2. **Data Partitioning:**
   - Partition the fetched data into chunks of configurable size.

3. **S3 Storage:**
   - Store partitioned data in Minio S3 with a folder structure reflecting the date and partition number.

4. **Airflow Automation:**
   - The entire process is orchestrated and automated using Apache Airflow, providing a scalable and reliable solution.

