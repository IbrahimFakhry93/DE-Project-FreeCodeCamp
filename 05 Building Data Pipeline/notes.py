#
# & Building Your First Data Pipeline (Python + Docker + PostgreSQL)

# ? What is a data pipeline?
# * A data pipeline is a process that moves data from a source → through transformations → into a destination.
# * In this example: Source DB (Postgres) → Python ELT script → Destination DB (Postgres).
# * ELT = Extract, Load, Transform. We first extract data, load it into another DB, then transform later.

# & Project Setup

# ? Create project structure:
# * mkdir elt_project && cd elt_project
# * touch elt_script.py
# * touch docker-compose.yaml

# ? Why Docker Compose?
# * Docker Compose lets us run multiple containers together (source DB, destination DB, and our Python script).
# * Each service runs in isolation but communicates via a shared network.

# in order to
# have the two databases that we need one
# being our source where our data is
# coming from and the destination where we
# want to send data to so that way we can
# use the alt script to move data between
# those two now we're going to use
# postgress for this example because we
# can use it as an open source database


# & docker-compose.yaml (services definition)

# ? Define three services: source_postgres, destination_postgres, elt_script.

# ! version: "3"
# ! services:
# ^   source_postgres:
# ~     image: postgres:latest
# ~     ports: ["5433:5432"]          # expose source DB on localhost:5433
# ~     environment:
# *       POSTGRES_DB: sourcedb
# *       POSTGRES_USER: postgres
# *       POSTGRES_PASSWORD: secret
# ~     volumes:
# *       - ./source_db_init:/docker-entrypoint-initdb.d

# ? Explanation: The init SQL file in source_db_init will auto‑create tables and insert fake data.

# ^   destination_postgres:
# ~     image: postgres:latest
# ~     ports: ["5434:5432"]          # expose destination DB on localhost:5434
# ~     environment:
# *       POSTGRES_DB: destdb
# *       POSTGRES_USER: postgres
# *       POSTGRES_PASSWORD: secret
# ? Note: No volume here → data resets each run, so we can test the pipeline fresh.


#! why we place elt_script here in composer file
# * to tell Docker that we utilizing a script here (elt script)
# * to send data from the source to the destination databases
# * so we place it in the docker container which is runtime instance
# * so Docker will run this script instead of us having to manually do it

# ^   elt_script:
# ~     build:
# *       context: .
# *       dockerfile: Dockerfile
# ~     command: ["python","elt_script.py"]
# ~     depends_on:
# *       - source_postgres
# *       - destination_postgres

# ? Explanation: The script container waits until both DBs are ready before running.

# & Dockerfile (for elt_script)

# ? Defines Python environment with PostgreSQL client tools.
# * FROM python:3.8-slim
# * RUN apt-get update && apt-get install -y postgresql-client
# * COPY elt_script.py .
# * CMD ["python","elt_script.py"]

# & Source Database Initialization

# ? Create folder + SQL file:
# * mkdir source_db_init && touch source_db_init/init.sql
# ? Example init.sql:
# * CREATE TABLE actors (id SERIAL PRIMARY KEY, name TEXT);
# * INSERT INTO actors (name) VALUES ('Leonardo DiCaprio'), ('Tom Hanks');

# & Python ELT Script (elt_script.py)

# ? Import libraries:
# * import subprocess, time, sys

# ? Step 1: Wait for Postgres to be ready
# * def wait_for_postgres(host, retries=5, delay=5):
# *     for i in range(retries):
# *         try:
# *             subprocess.run(["pg_isready","-h",host], check=True)
# *             print(f"Connected to {host}")
# *             return True
# *         except subprocess.CalledProcessError:
# *             print(f"Retry {i+1}/{retries}... waiting {delay}s")
# *             time.sleep(delay)
# *     print("Max retries reached. Exiting.")
# *     return False

# ? Step 2: Dump data from source DB
# * dump_cmd = [
# *   "pg_dump",
# *   "-h","source_postgres",
# *   "-U","postgres",
# *   "-d","sourcedb",
# *   "-f","data_dump.sql"
# * ]
# * subprocess.run(dump_cmd, env={"PGPASSWORD":"secret"}, check=True)

# ? Step 3: Load data into destination DB
# * load_cmd = [
# *   "psql",
# *   "-h","destination_postgres",
# *   "-U","postgres",
# *   "-d","destdb",
# *   "-f","data_dump.sql"
# * ]
# * subprocess.run(load_cmd, env={"PGPASSWORD":"secret"}, check=True)

# * print("ELT script finished successfully.")

# & Running the Pipeline

# ? Start everything:
# * docker-compose up --build
# ? Logs will show:
# * Source DB initialized with fake data.
# * Destination DB created.
# * ELT script runs → dumps source data → loads into destination.

# & Verifying Results

# ? Connect to destination DB:
# * docker exec -it <destination_container_name> psql -U postgres -d destdb
# ^ ex in our case:
# ~ docker exec -it 05buildingdatapipeline-destination_postgres-1 psql -U postgres
# * \c destination_db : to check the connection to destination database
# * \dt             # list tables
# * SELECT * FROM actors;   # confirm data copied

# & Key Beginner Notes

# ? Why use pg_dump + psql?
# * pg_dump exports schema + data from source DB into a file.
# * psql imports that file into destination DB.
# * This is the simplest way to move data between two PostgreSQL databases.

# ? Why depends_on in Docker Compose?
# * Ensures the Python script waits until both DBs are ready, avoiding connection errors.

# ? Why no volume for destination?
# * Forces fresh data each run → helps confirm pipeline works correctly.

# & Recap

# ? You built a simple ELT pipeline:
# * Source DB → dump data → Python script → load into destination DB.
# ? This is the foundation. Later you’ll add:
# * Cron jobs (scheduling)
# * dbt (transformations)
# * Airflow (orchestration)
# * Airbyte (data ingestion from external sources)
