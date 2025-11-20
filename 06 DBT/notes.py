#





---

#& Introduction to DBT in the Pipeline

#? Key Takeaway  
#* DBT (Data Build Tool) is an open‑source framework 
#* used to transform data inside your destination database after it has been loaded. 
#* It allows you to build custom models, create new tables, 
#* and structure data for analysts and scientists.

#* DBT is the next step after building the ELT pipeline.  
#* Analysts/scientists often need data combined or reshaped into specific formats.  
#* DBT lets you write SQL models (and even Python scripts) to transform data directly in the warehouse.  
#* This makes data cleaner, more structured, and easier to use for reporting or analysis.

#? Important Definitions:
#* DBT (Data Build Tool) → Framework for transforming data inside warehouses using SQL + Jinja.

#* Adapter → Plugin that lets DBT connect to a specific database (e.g., Postgres, Snowflake).

# * dbt-core: is the open source version of dbt
---

#& Prerequisites for DBT

#* DBT must be installed locally (or inside Docker).  
#* Installation uses **pip** (Python package manager).  
#~ Example installation for Postgres adapter:  
  pip install dbt-postgres
  #^ → This installs DBT Core + Postgres adapter.  
#~ Verify installation:  
  dbt --version
  #^ → Shows DBT version and installed adapters.

---

#& Initializing a DBT Project

#* Run inside your project root:  
  dbt init
#* Prompts for project name (e.g., `custom_postgres`).  
#* Creates folders:  
  - analysis/  
  - macros/  
  - models/  
  - seeds/  
  - snapshots/  
  - tests/  
#* Focus for beginners: **models/** and **macros/**.

---

#& Configuring DBT Profiles

#? Crucial Note  
#* Profiles tell DBT how to connect to your database. Without correct configuration, DBT cannot run models.

#* DBT creates a `profiles.yml` file in your local `~/.dbt/` directory.  
#~ Example dev profile for Postgres:  
  custom_postgres:
    target: dev
    outputs:
      dev:
        type: postgres
        host: host.docker.internal
        port: 5434
        user: postgres
        password: secret
        dbname: destination_db
        schema: public
        threads: 1

---
#* Profiles.yml → Configuration file that stores database connection details (host, port, user, password).

#& DBT Project File (`dbt_project.yml`)

#* Defines how models are materialized (stored).  
#* Options: `view`, `table`, `incremental`.  
#* For Postgres, use `table` so DBT creates physical tables.  
#* Example:  
  models:
    custom_postgres:
      +materialized: table

---

#& Writing DBT Models

#? Key Takeaway  
#* Models are just SQL files stored in the `models/` folder. 
#* DBT compiles them and runs them in your warehouse.

#~ Example: `film_actors.sql`  
  SELECT * FROM {{ source('destination_db','film_actors') }}
#* Create similar references for `actors.sql` and `films.sql`.  
#* These references allow DBT to know which raw tables to query.

---

#& Schema and Sources

#* Define schema tests in `schema.yml`.  
#* Example:  
  models:
    - name: films
      columns:
        - name: film_id
          tests:
            - unique
            - not_null
#* Define sources in `sources.yml`:  
  sources:
    - name: destination_db
      tables:
        - name: film_actors
        - name: actors
        - name: films

---

#& Example Custom Model: Film Ratings

#* Create `film_ratings.sql` model:  
  WITH films_with_ratings AS (
    SELECT film_id, title, release_date, price, rating, user_rating,
      CASE
        WHEN user_rating >= 4.5 THEN 'Excellent'
        WHEN user_rating >= 4.0 THEN 'Good'
        WHEN user_rating >= 3.0 THEN 'Average'
        ELSE 'Poor'
      END AS rating_category
    FROM {{ ref('films') }}
  ),
  films_with_actors AS (
    SELECT f.film_id, f.title,
           STRING_AGG(a.actor_name, ', ') AS actors
    FROM {{ ref('films') }} f
    LEFT JOIN {{ ref('film_actors') }} fa ON f.film_id = fa.film_id
    LEFT JOIN {{ ref('actors') }} a ON fa.actor_id = a.actor_id
    GROUP BY f.film_id, f.title
  )
  SELECT fwr.*, fwa.actors
  FROM films_with_ratings fwr
  LEFT JOIN films_with_actors fwa ON fwr.film_id = fwa.film_id;

---

#& Running DBT in Docker

#* Add DBT service in `docker-compose.yml`:  
  dbt:
    image: ghcr.io/dbt-labs/dbt-postgres:1.4.7
    command: ["run", "--profiles-dir", "/root", "--project-dir", "/dbt"]
    volumes:
      - ./custom_postgres:/dbt
      - ~/.dbt:/root
    networks:
      - elt_network
    depends_on:
      - elt_script

---

#& Macros in DBT

#? Key Takeaway  
#* Macros = reusable SQL snippets. 
#* They prevent repetition and follow the DRY principle (Don’t Repeat Yourself).

#* Example macro file `film_ratings_macro.sql`:  
  {% macro generate_film_ratings() %}
    -- SQL logic from film_ratings.sql
  {% endmacro %}
#* Call macro inside model:  
  {{ generate_film_ratings() }}

---

#& Jinja in DBT

#? Jinja = templating language DBT uses inside SQL.
#* Allows loops, conditionals, and dynamic SQL.  
#* Example:  
  {% for method in ['Credit Card','Bank Transfer','Gift Card'] %}
    SUM(CASE WHEN payment_method = '{{ method }}' THEN amount ELSE 0 END) AS {{ method | lower }}_amount,
  {% endfor %}

---

#& Beginner Glossary (Technical Jargon Explained)

#* DBT (Data Build Tool) → Framework for transforming data inside warehouses using SQL + Jinja.

#* Adapter → Plugin that lets DBT connect to a specific database (e.g., Postgres, Snowflake).

#* Profiles.yml → Configuration file that stores database connection details (host, port, user, password).

#* Materialization → How DBT stores models: as views, tables, or incremental tables.

#* CTE (Common Table Expression) → A temporary named query (like a subquery) used inside SQL for clarity.

#* Macro → Reusable SQL function written in Jinja, helps avoid repeating code.

#* Jinja → Templating language DBT uses to add loops, conditions, and dynamic behavior to SQL.

#* Source → Definition in DBT that points to raw tables in your warehouse.

#* Schema.yml → File where you define tests and metadata for models (e.g., uniqueness, not null).

#* dbt run → Command to execute all models and build tables in the warehouse.

#* dbt test → Command to run data quality tests defined in schema.yml.
