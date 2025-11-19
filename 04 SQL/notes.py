#
# * let's move on to the SQL module where we're going to be using SQL
# * but we're also going to start our own little database inside Docker as well


# & SQL Module Basics

# ? SQL = Structured Query Language
# * It is the standard language used to create, manage, and query databases.
# * Databases like PostgreSQL and MySQL use SQL to store and retrieve data.

# & Setting up PostgreSQL with Docker

# ? Instead of installing PostgreSQL manually, we use Docker to run it inside a container.
# * docker pull postgres                # download PostgreSQL image
# ~ docker run --name data_eng_pg -e POSTGRES_PASSWORD=secret -d postgres
# *   --name = container name
# *   -e = environment variable (here we set password)
# *   -d = run in background

# ? Create a new database inside the container:
# * docker exec -U postgres data_eng_pg createdb postgresdb

# ? Connect to the database:
# * docker exec -it data_eng_pg psql -U postgres -d postgresdb

# & Creating Tables

# ? Tables are like spreadsheets: rows = records, columns = fields.
# * CREATE TABLE users (
# *   id SERIAL PRIMARY KEY,          # auto-increment unique ID
# *   first_name VARCHAR(50),
# *   last_name VARCHAR(50),
# *   email VARCHAR(100),
# *   date_of_birth DATE
# * );

# ? Check tables:
# * \dt   # lists tables in PostgreSQL

# & Inserting Data

# ? Insert rows into a table:
# * INSERT INTO users (first_name, last_name, email, date_of_birth)
# * VALUES ('Alice','Smith','alice@example.com','1990-05-12');

# ? Insert multiple rows at once:
# * INSERT INTO users (...) VALUES (...), (...), (...);

# & Selecting Data

# ? SELECT retrieves data from tables.
# * SELECT * FROM users;       # select all columns and rows
# * SELECT first_name, email FROM users;   # select specific columns

# ? DISTINCT removes duplicates:
# * SELECT DISTINCT email FROM users;

# & Updating Data

# ? UPDATE changes existing records.
# * UPDATE users SET email='newmail@gmail.com' WHERE first_name='John';
# ^   Without WHERE → updates ALL rows (dangerous!)

# & Inserting into Films Table

# ? Example table with constraints:
# * CREATE TABLE films (
# *   film_id SERIAL PRIMARY KEY,
# *   title VARCHAR(100),
# *   release_date DATE,
# *   price DECIMAL(5,2),
# *   rating VARCHAR(10),
# *   user_rating INT CHECK (user_rating BETWEEN 1 AND 5)
# * );

# ? Insert multiple films:
# * INSERT INTO films (title, release_date, price, rating, user_rating)
# * VALUES ('Inception','2010-07-16',9.99,'PG-13',5), (...);

# & Limiting Results

# ? LIMIT restricts how many rows are returned.
# * SELECT * FROM films LIMIT 5;

# & Aggregate Functions

# ? Aggregate functions compute values across rows.
# * SELECT COUNT(*) FROM films;        # count rows
# * SELECT SUM(price) FROM films;      # total of all prices
# * SELECT AVG(user_rating) FROM films;# average rating
# * SELECT MAX(price), MIN(price) FROM films; # highest and lowest price

# & Grouping Data

# ? GROUP BY groups rows by a column, often used with aggregates.
# * SELECT rating, AVG(user_rating)
# * FROM films
# * GROUP BY rating;

# & Joins (Combining Tables)

# ? JOIN combines rows from multiple tables based on relationships.
# * INNER JOIN → only rows with matches in both tables.
# * LEFT JOIN → all rows from left table, even if no match.

# ^ Example INNER JOIN:
# * SELECT f.film_id, f.title, a.actor_name
# * FROM films f
# * INNER JOIN film_actors fa ON f.film_id = fa.film_id
# * INNER JOIN actors a ON fa.actor_id = a.actor_id
# * ORDER BY f.film_id;

# ? Explanation:
# * films table → has movies
# * actors table → has actor names
# * film_actors table → bridge linking films to actors
# * INNER JOIN → only shows films with matching actors
# * LEFT JOIN → shows all films, even if no actors assigned

# & Union vs Union All

# ^ UNION combines results of two SELECT queries but removes duplicates.
# ^ UNION ALL keeps duplicates.

# * SELECT title FROM films
# * UNION
# * SELECT category_name FROM film_categories;

# & Key Notes for Beginners

# * Always end SQL statements with a semicolon (;).
# * Use uppercase for SQL keywords (SELECT, INSERT, UPDATE) → best practice.
# * Use lowercase for table/column names.
# * WHERE clause is critical to avoid updating/deleting all rows by mistake.
# * Joins are powerful: they let you combine multiple tables into one result set.
