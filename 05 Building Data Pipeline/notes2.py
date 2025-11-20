#
# & Data pipeline (PostgreSQL + Docker + Python) — full walkthrough

# ? Goal
# * Build a simple ELT pipeline: Source Postgres → dump → load → Destination Postgres,
# * orchestrated by Docker Compose and a Python script.
# * You’ll understand: why we expose ports, how services talk over a Docker network, and why YAML indentation matters.

# & Why expose ports (5433:5432 and 5434:5432)

# ? Port mapping basics
# * Inside the container, PostgreSQL listens on port 5432.
# * Port mapping "HOST:CONTAINER" (e.g., 5433:5432) exposes the container’s 5432 to your machine’s 5433.

# * We need to expose the ports of source and destination databases in order to access them

# ? Why two different host ports?
# * **5433:5432 (source)** → lets you connect from your host to the source DB at localhost:5433.
# * **5434:5432 (destination)** → lets you connect from your host to the destination DB at localhost:5434.
# * If you used the same host port for both, they would conflict.
# * Inside the Docker network, containers still use service names (source_postgres, destination_postgres) and port 5432.

# & Exact steps the tutor followed (reproducible)

# ? Create project structure
# * mkdir elt && cd elt
# * touch docker-compose.yaml
# * mkdir elt_script && touch elt_script/elt_script.py
# * touch Dockerfile
# * mkdir -p source_db_init && touch source_db_init/init.sql

# ? Fill docker-compose.yaml (correct YAML + indentation)

# ! version: "3.9"
# ! services:
# ^  source_postgres:
# ~     image: postgres:latest               # pull from dockerhub the latest version of postgress image
# ~     container_name: source_postgres
# ~     ports:
# *       - "5433:5432"
# ~     environment:
# *       POSTGRES_DB: sourcedb
# *       POSTGRES_USER: postgres
# *       POSTGRES_PASSWORD: secret
# ~     volumes:
# *       - ./source_db_init:/docker-entrypoint-initdb.d   #: look down for explanation of this path
# ~     networks:
# *       - elt_network
# *
# ^   destination_postgres:
# ~     image: postgres:latest
# ~     container_name: destination_postgres
# ~     ports:
# *       - "5434:5432"
# ~     environment:
# *       POSTGRES_DB: destdb
# *       POSTGRES_USER: postgres
# *       POSTGRES_PASSWORD: secret
# ~     networks:
# *       - elt_network

#! why we place elt_script here in composer file
# * to tell Docker that we utilizing a script here (elt script)
# * to send data from the source to the destination databases
# * so we place it in the docker container which is runtime instance
# * so Docker will run this script instead of us having to manually do it

# ^   elt_script:
# ~     build:
# *       context: .
# *       dockerfile: Dockerfile
# ~     command: ["python","elt_script/elt_script.py"]
# ~     depends_on:
# *       - source_postgres
# *       - destination_postgres
# ~     networks:
# *       - elt_network
# *
# ? Explanation: The script container waits until both DBs are ready before running.

# ! networks:
# *   elt_network:
# *     driver: bridge

# ? YAML indentation rules (crucial)
# * Use spaces, NOT tabs. 2 spaces per indent is common, 2–4 works consistently.
# * Keys aligned at the same level (services, networks) must have identical indentation.
# * Lists (e.g., ports, volumes) use a dash with one space: "- \"5433:5432\"" on its own line under the key.

#! Initializing Postgres Database with Data
# ^ We will prepare sample data to initialize the Postgres database using an init.sql file.

# * Create an init.sql file inside the source_db_init folder.
# * This file contains SQL commands to set up tables and insert initial data.
# * Docker will use this file during container startup.

# & Mapping Local Directory to Docker
# ^ The colon (:) in Docker volumes maps a local path to a path inside the container.

# * Local directory: ./source_db_init/init.sql
# * Container directory: /docker-entrypoint-initdb.d/init.sql
# ^ Effect:
# * Docker copies our local init.sql into the container’s initdb.d folder.
# ^ Purpose:
# * Ensures the database is automatically initialized with our SQL script when the container starts.

# & Docker Compose Volume Example
# * Add this to docker-compose.yaml:
# volumes:
#   - ./source_db_init/init.sql:/docker-entrypoint-initdb.d/init.sql


# ^=============================================================

#! Destination Postgres Setup (Testing Mode)
# * We intentionally avoid using volumes so data does not persist between runs.
# * This ensures the ELT script is tested fresh each time.

# ^ Reason:
# *    - Persisted data could hide whether the ELT script worked correctly.
# *    - By removing volumes, every container restart wipes the database.
# *    - Guarantees reproducible tests: ELT must succeed from scratch each run.

# & docker-compose.yaml (destination_postgres service)
# ^   destination_postgres:
# ~     image: postgres:latest
# ~     ports: ["5434:5432"]          # expose destination DB on localhost:5434
# ~     environment:
# *       POSTGRES_DB: destdb
# *       POSTGRES_USER: postgres
# *       POSTGRES_PASSWORD: secret
# ? Note: No volume section → data resets each run, pipeline always starts clean.
# ^===============================================

#! Docker Compose: depends_on Property
# * Ensures container startup order → one service waits until its dependencies are ready.

# * Syntax example:
# ~     depends_on:
# *       - source_postgres
# *       - destination_postgres

# ^  Meaning:
# *    - This container will not initialize until both `source_postgres` and `destination_postgres` are built.
# *    - Guarantees that dependent services (like the ELT script) only start after databases are available.
# *    - Prevents race conditions where a script runs before its required DBs are ready.


# ^=================================================================================
# & What each section does in compose yaml file above

# ? services.source_postgres
# * Pulls the official Postgres image.
# * Exposes 5433 on your host to connect via localhost:5433.
# * Environment variables initialize DB name/user/password.
# * Mounts init SQL folder to /docker-entrypoint-initdb.d → Postgres runs all .sql files at startup to seed data.

# ? services.destination_postgres
# * Same Postgres image, but exposed at localhost:5434.
# * No init volume (fresh DB) so the ELT script proves data was copied each run.

# ? services.elt_script
# * Builds a Python container from your Dockerfile, runs the ELT script.
# * depends_on ensures containers start in order;

# ^ note:
# * it doesn’t guarantee DB “readiness”, only that containers are started.


# & Dockerfile (for the Python ELT container)

# ? Purpose
# ^ Provide: Python runtime + Postgres CLI tools (pg_dump/psql) to perform ELT.
# ^ Python runtime means the python environment (or py engine or the py interpreter) that runs the python code
# ^ pg_dump for extracting data into an sql file, psql for loading this sql file into destination

# * FROM python:3.11-slim
# * RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*
# * COPY elt_script/elt_script.py /app/elt_script.py       : # copy ELT script into container
# * WORKDIR /app
# * CMD ["python","/app/elt_script.py"]


# & Source DB init SQL (auto-seeded)

# ? Place in source_db_init/init.sql (runs automatically at container start)
# * -- Example minimal seed (extend as needed)
# * CREATE TABLE actors (id SERIAL PRIMARY KEY, actor_name TEXT NOT NULL);
# * CREATE TABLE films (
# *   film_id SERIAL PRIMARY KEY,
# *   title TEXT NOT NULL,
# *   release_date DATE,
# *   price DECIMAL(5,2),
# *   rating TEXT,
# *   user_rating INT CHECK (user_rating BETWEEN 1 AND 5)
# * );
# * CREATE TABLE film_actors (film_id INT, actor_id INT, PRIMARY KEY (film_id, actor_id));
# * INSERT INTO actors (actor_name) VALUES ('Leonardo DiCaprio'), ('Tom Hanks');
# * INSERT INTO films (title, release_date, price, rating, user_rating)
# * VALUES ('Inception','2010-07-16',9.99,'PG-13',5), ('Forrest Gump','1994-07-06',7.99,'PG-13',5);
# * INSERT INTO film_actors (film_id, actor_id) VALUES (1,1),(2,2);

# & ELT script logic (Python subprocess + pg_dump/psql)

# ? Readiness check (because depends_on ≠ “ready”)
# ~ Run a fallback (double check) that elt script will not run unless source and destination databases and working)


def wait_for_postgres(host, max_retries=5, delay_seconds=5):
    """Wait for PostgreSQL to become available."""
    retries = 0
    while retries < max_retries:
        try:
            result = subprocess.run(
                ["pg_isready", "-h", host], check=True, capture_output=True, text=True
            )
            if "accepting connections" in result.stdout:
                print("Successfully connected to PostgreSQL!")
                return True
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to PostgreSQL: {e}")
            retries += 1
            print(
                f"Retrying in {delay_seconds} seconds... (Attempt {retries}/{max_retries})"
            )
            time.sleep(delay_seconds)
    print("Max retries reached. Exiting.")
    return False


# * Use the function before running the ELT process
if not wait_for_postgres(host="source_postgres"):
    exit(1)


# * Configuration for the source PostgreSQL database
source_config = {
    "dbname": "source_db",
    "user": "postgres",
    "password": "secret",
    # ^ Use the service name from docker-compose as the hostname
    "host": "source_postgres",
}

# * Configuration for the destination PostgreSQL database
destination_config = {
    "dbname": "destination_db",
    "user": "postgres",
    "password": "secret",
    # ^ Use the service name from docker-compose as the hostname
    "host": "destination_postgres",
}


# ? Main steps (extract → load)

# ^ import subprocess
# * SOURCE = {"host":"source_postgres","db":"sourcedb","user":"postgres","pwd":"secret"}
# * DEST   = {"host":"destination_postgres","db":"destdb","user":"postgres","pwd":"secret"}
# * wait_for_postgres(SOURCE["host"]); wait_for_postgres(DEST["host"])
# * print("Starting ELT...")
# *
# ^ Extract: dump source DB to file
# * dump_cmd = ["pg_dump","-h",SOURCE["host"],"-U",SOURCE["user"],"-d",SOURCE["db"],"-f","/app/data_dump.sql","-w"]
# * subprocess.run(dump_cmd, env={"PGPASSWORD":SOURCE["pwd"]}, check=True)
# *
# ^ # Load: apply dump file to destination DB
# * load_cmd = ["psql","-h",DEST["host"],"-U",DEST["user"],"-d",DEST["db"],"-f","/app/data_dump.sql","-w"]
# * subprocess.run(load_cmd, env={"PGPASSWORD":DEST["pwd"]}, check=True)
# * print("ELT complete.")

# ? Notes
# * "-w" with env PGPASSWORD avoids interactive password prompts.
# * Use absolute paths inside the container (e.g., /app/data_dump.sql) to avoid “file not found”.

# & Running and verifying

# ? Build and start everything
# * docker-compose up --build
# ? What you should see
# * Source DB initializes (runs init.sql).
# * Destination DB starts empty.
# * ELT container waits for readiness → pg_dump → psql → “ELT complete.”


# & Verifying Results

# ? Connect to destination DB:
# * docker exec -it <destination_container_name> psql -U postgres -d destdb
# ^ ex in our case:
# ~ docker exec -it 05buildingdatapipeline-destination_postgres-1 psql -U postgres
# * \c destination_db : to check the connection to destination database
# * \dt             # list tables
# * SELECT * FROM actors;   # confirm data copied

# & Troubleshooting (common issues seen in the tutorial)

# ? “DB not ready” errors
# * Use pg_isready; add retries (see wait_for_postgres).
# * Docker depends_on only guarantees start order, not readiness.

# ? “command exit status” from pg_dump/psql
# * Check flags: uppercase -U for user, -h for host, -d for DB.
# * Ensure PGPASSWORD is set in env; otherwise you’ll get auth prompts (and failures in non-interactive scripts).

# ? “file not found” for data_dump.sql
# * Confirm working directory in the Dockerfile (WORKDIR /app).
# * Make sure the script uses the same path (/app/data_dump.sql).

# ? YAML parse errors
# * Use spaces, not tabs. Keep indentation consistent.
# * Lists (ports/volumes) must be under their keys with “- value”.
# * Validate compose file with: docker-compose config

# & Why the network is needed

# ? Docker bridge network (elt_network)
# * Lets services resolve each other by **service name** (source_postgres → host “source_postgres”).
# * Internal traffic stays isolated; you don’t need to expose ports for containers to talk to each other.
# * Ports are only for host access (your terminal apps like psql or GUI tools).

# & Clean runs and resets

# ? Stop and remove containers
# * docker-compose down
# ? Remove data to re-test fresh (destination only persists if you add volumes)
# * docker-compose down -v            # removes named/anonymous volumes
# ? Rebuild after Dockerfile or script changes
# * docker-compose up --build

# & Quick mental model (beginner-friendly)
# * Compose starts 3 containers: source DB, destination DB, ELT worker.
# * Source seeds itself from init.sql (auto-run).
# * ELT worker waits → pg_dump (export source) → psql (import to dest).
# * You connect from your host (5432) to source (5433) and dest (5434) to check results.

# & Safety and reproducibility tips

# ? Keep destination stateless during testing
# * Avoid volumes for destination so you can confirm each ELT run actually copied data.

# ? Keep credentials and hosts consistent
# * Use service names for -h (source_postgres/destination_postgres), not localhost inside containers.

# ? Validate compose early
# * docker-compose config → catches indentation and schema mistakes in YAML.

# ? Log clearly in the script
# * Print steps (“waiting…”, “dumping…”, “loading…”) to quickly pinpoint failures.
