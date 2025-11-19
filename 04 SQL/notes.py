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
# ~ docker run --name de_dbpg -e POSTGRES_PASSWORD=secret -d postgres
# *   --name = container name
# *   -e = environment variable (here we set password)
# *   -d = run in background

# ? Create a new database inside the container:
# * docker exec -U postgres de_dbpg createdb postgresdb

# ? Connect to the database:
# * docker exec -it de_dbpg psql -u postgres -d postgresdb

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

# * Aggregate function are useful for analytics to calculate metrics and gain insights from our data

# ? Aggregate functions compute values across rows.
# * SELECT COUNT(*) FROM films;        # count rows (or count number of records)
# * SELECT SUM(price) FROM films;      # total of all prices
# * SELECT AVG(user_rating) FROM films;# average rating
# * SELECT MAX(price), MIN(price) FROM films; # highest and lowest price

# & Grouping Data

# ? GROUP BY groups rows by a column, often used with aggregates.
# * SELECT rating, AVG(user_rating)
# * FROM films
# * GROUP BY rating;

# * Group identical forms of data

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
# ~ (We use film_actors as a bridge to connect the actor names to their correct films)

# * INNER JOIN → only shows films with matching actors
# * LEFT JOIN → shows all films, even if no actors assigned

# & Union vs Union All

# ^ UNION combines results of two SELECT queries but removes duplicates.
# ^ UNION ALL keeps duplicates.

# * SELECT title FROM films
# * UNION
# * SELECT category_name FROM film_categories;

# * use Join to combine tables have different data sets
# * use Union to combine results sets of two queries

# & Key Notes for Beginners

# * Always end SQL statements with a semicolon (;).
# * Use uppercase for SQL keywords (SELECT, INSERT, UPDATE) → best practice.
# * Use lowercase for table/column names.
# * WHERE clause is critical to avoid updating/deleting all rows by mistake.
# * Joins are powerful: they let you combine multiple tables into one result set.


# & SQL Subqueries

# ? What is a subquery?
# * A subquery is a query inside another query, written in parentheses.
# * SQL executes the inner query first, then uses its result in the outer query.
# * Subqueries can appear in SELECT, WHERE, FROM, or HAVING clauses.
# ? Think of it like: "Ask one question, then use its answer to help answer another."

# & Example 1: Subquery inside SELECT

# ? We want to show each film title along with one of its actors.
# ? Instead of joining directly, we use a subquery inside SELECT.

# * SELECT f.title,
# *        (SELECT a.actor_name
# *         FROM actors a
# *         JOIN film_actors fa ON a.actor_id = fa.actor_id
# *         WHERE fa.film_id = f.film_id
# *         LIMIT 1) AS actor_name
# * FROM films f;

# ? Explanation:
# * Outer query → selects film titles from films table (alias f).
# * Inner query → finds actor_name for that film_id by joining actors + film_actors.
# * LIMIT 1 → ensures only one actor is returned per film.
# * SQL runs the inner query for each film row, then adds the result to the outer query.

# & Example 2: Subquery with IN operator

# ^ Goal:
# ^ Find films that feature Leonardo DiCaprio or Tom Hanks.
# * We use a subquery in the WHERE clause with IN.

# * SELECT title
# * FROM films
# * WHERE film_id IN (
# *   SELECT fa.film_id
# *   FROM film_actors fa
# *   JOIN actors a ON fa.actor_id = a.actor_id
# *   WHERE a.actor_name IN ('Leonardo DiCaprio', 'Tom Hanks')
# * );

# ? Explanation:
# * Outer query → selects film titles from films table.
# * WHERE film_id IN (...) → only include films whose IDs are returned by the subquery.
# * Inner query → finds film_ids where actor_name is Leonardo DiCaprio or Tom Hanks.
# * Result → Inception, Forrest Gump, Toy Story (all feature those actors).

# & Why subqueries are useful

# ? They allow complex filtering or calculations without writing multiple queries manually.
# ? They can replace joins in some cases, though joins are often more efficient.
# ? They make queries more readable when you want to "nest" logic.

# & Beginner Tips

# * Always wrap subqueries in parentheses.
# * Use aliases (like f, a, fa) to shorten table names and make queries clearer.
# * Subqueries can be correlated (depend on outer query values) or independent.
# * Correlated subquery example: WHERE fa.film_id = f.film_id (depends on outer query row).
# * Independent subquery example: SELECT AVG(price) FROM films (does not depend on outer query).

# & Quick Recap

# ? Subqueries = queries inside queries.
# * They can appear in SELECT (return a value), WHERE (filter rows), or FROM (act as a table).
# * They are powerful for filtering, calculations, and combining data across multiple tables.


#! ask chatgpt about the sequence of execution and performance

# ^ Subquery in the `SELECT` Clause:

# ~ - Retrieve each film's title along with the name of one of its actors.

# SELECT title,
#        (SELECT actor_name
#         FROM actors a
#         JOIN film_actors fa ON a.actor_id = fa.actor_id
#         WHERE fa.film_id = f.film_id
#         LIMIT 1) AS actor_name
# FROM films f;

# ^ Subqueries with `IN`:

# ~ - Retrieve films that have either Leonardo DiCaprio or Tom Hanks as actors.

# SELECT title
# FROM films
# WHERE film_id IN
# (SELECT fa.film_id
#  FROM film_actors fa
#  JOIN actors a ON a.actor_id = fa.actor_id
#  WHERE a.actor_name IN ('Leonardo DiCaprio', 'Tom Hanks'));

#     title
# --------------
#  Inception
#  Forrest Gump
#  Toy Story
