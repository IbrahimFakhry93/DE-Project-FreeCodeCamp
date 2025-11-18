#
# & Docker for aspiring data engineers

# ? What Docker is (plain English):
# * Docker is a free (open‑source) tool that packages an app
# * and everything it needs (dependencies, settings) into a "container"
# * so it runs the same everywhere—on your laptop, a teammate’s machine, or in the cloud.

# ? Why containers matter:
# * Apps often fail on other machines due to missing libraries or different settings ("it works on my machine").

# ^ A container includes:
# *  your code + runtime (e.g., Node) + libraries + environment variables + config files.

# ^ Result:
# *  predictable, reproducible environments for testing, deployment (pushing to cloud or into production),
# *  and scaling.

# ^ containerization concept
# * in software development we're looking at Docker in the form of testing deployment
# * for its ease of use, speed and flexibility

# * it assists with the deployment scaling and management of those applications using what we call
# * containerization which is just a lightweight form of virtualization

# & Core Docker concepts

# ? Dockerfile (the blueprint):
# * A plain text file with step‑by‑step instructions in order to build your app’s environment.
# *A Dockerfile is simply a text-based file with no file extension that contains a script of instructions.
# * Docker uses this script to build a container image.

# ~ elt_script/Dockerfile: (from the course repo)
# * This Dockerfile sets up a Python environment and installs the PostgreSQL client.
# * It also copies the ELT script into the container and sets it as the default command.

# ^ Example instructions:
# * choose a base image
# * set a working directory
# * copy code
# * install deps
# * set the start app command
# * expose ports


# ! Order matters:
# * Docker builds in layers; changing a step may invalidate later cached layers.

# ? Image (the packaged app):
# * The output of building a Dockerfile. An image is a read‑only, immutable snapshot
# * that contains everything needed to run.
# * It's a standalone executable package that included everything needed to run the app
# * You cannot edit an image; to change behavior, edit the Dockerfile and build a new image.
# ~  Think: “frozen recipe card” created from your Dockerfile.


# ? Container (a running instance):
# * A container is the live, isolated (runtime instance) created from an image.
# * You can start, stop, and delete containers independently—even multiple containers from the same image.
# * Each container has its own filesystem
# ~ Think: “a dish served from the recipe card.” Many dishes can be served from one recipe.

# * Container is the running version of the image

# * The docker image containerizes the application that the docker file is sitting in

# & Install essentials

# ? Install Docker Desktop:
# * Download Docker Desktop for your OS (macOS, Windows, Linux).
# * Docker Desktop includes Docker Engine (daemon) and a graphical UI.
# * Also install Docker Compose (usually bundled with Desktop) to run multi‑container apps using one file.

# & Build and run your first container

# ? Create a Dockerfile (example: Node.js todo app):
# * FROM node:18           # choose base runtime
# * WORKDIR /app           # set working directory inside container
# * COPY . .               # copy project files
# * RUN yarn install --production   # install dependencies
# * CMD ["node", "src/index.js"]    # start the app
# * EXPOSE 3000            # declare app port inside container

# ^ open: Docker desktop , click on its shortcut on desktop to run it

# ? Build an image:
# * docker build -t getting-started .
# * -t tags (names) the image;
# * "." means build context is current directory. (containerize everything in the current directory)

# ^ go to Docker desktop -> images tab and check the created image

# ? Run a container:
# * docker run -d -p 127.0.0.1:3000:3000 --name getting-started getting-started
# * -d runs in background (detached).
# * -p maps local port to container port: HOST:CONTAINER (here both 3000).
# * Access the app at http://127.0.0.1:3000.

# ^ note:
# * the host port can be changed but the container host must be the same port as the one selected n the docker file
# * docker run -d -p 127.0.0.1:3000:3000


# ? View running containers:
# * docker ps             # lists active containers with their IDs and names
# ~ Tip: you can use short IDs (first few characters) for commands.

# ? Update the app:
# * Edit code → rebuild a NEW image (images are immutable):
# * docker build -t getting-started .
# * If a container with the same name already exists on port 3000, remove or stop it:
# * docker rm -f getting-started   # stops and removes the running container
# * Then run again with docker run ...

# & Persisting data with volumes

# ? Why volumes:
# * By default, data written inside a container disappears when the container is removed.
# ! Volumes are special storage locations managed by Docker to persist data across container restarts and recreations.

# ? Create and use a named volume:
# * docker volume create todo-db
# * docker run -d -p 127.0.0.1:3000:3000 \
# *   --mount type=volume,source=todo-db,target=/var/lib/app-data \
# *   --name getting-started getting-started
# * type=volume → use a Docker-managed volume.
# * source=todo-db → the volume name.
# * target=/var/lib/app-data → where your app reads/writes data inside the container.

# ? Inspect a volume:
# * docker volume inspect todo-db   # shows metadata like mountpoint and created time.

# & Multi-container apps and networking

#! Multi‑Container Apps

#* Up to now, you worked with single‑container apps. Next step: add MySQL (App DB) to the stack.

#^ Common question: 
#* "Where should Application's Database run? Same container or separate?"

#* Rule of thumb: Each container should do one thing and do it well.

#^ Reasons to run MySQL in a separate container:
   - #* APIs/front‑ends often need different scaling than databases.
   - #* Separate containers allow versioning and updates in isolation.
   - #* In production, you may prefer a managed DB service → don’t ship DB engine with app.
   - #* Multiple processes in one container require a process manager → adds complexity.
   - #* Simpler startup/shutdown when each container runs a single process.

#^ Conclusion: 
#* Best practice is to run apps in multiple containers (e.g., app + database).

# ? Why networking:
# * Real apps use multiple services (e.g., a frontend app + a MySQL database).
# * Containers communicate over virtual networks created by Docker.

#* Containers run in isolation by default.  
#* They don’t know about other processes or containers on the same machine.  
#* To enable communication between containers → use networking.  
#* Place containers on the same network → they can talk to each other.  

#^ Two ways to put a container on a network:
   - #* Assign the network when starting the container.
   - #* Connect an already running container to a network.

#^ In practice: 
#* create the network first, then attach the MySQL container at startup.


# ? Create a network:
# * docker network create todo-app

# ? Run MySQL with a persistent volume and env vars:
# * docker run -d --name mysql \
# *   --network todo-app \
# *   --mount type=volume,source=todo-mysql-data,target=/var/lib/mysql \
# *   -e MYSQL_ROOT_PASSWORD=secret \
# *   -e MYSQL_DATABASE=todos \
# *   mysql:8
#^ Env vars configure MySQL: root password and initial database name.

# ? Connect the app container to MySQL:
# * docker run -d --name getting-started \
# *   --network todo-app \
# *   -p 127.0.0.1:3000:3000 \
# *   -e DB_HOST=mysql -e DB_USER=root -e DB_PASSWORD=secret -e DB_NAME=todos \
# *   getting-started
# * Here DB_HOST=mysql uses the MySQL container’s network alias/name for resolution.

# ? Enter a running container (interactive shell):
# * docker exec -it mysql mysql -u root -p   # then enter password to run SQL commands inside MySQL.

# * container has its own IP address.

# & Docker Compose (run everything with one file)

# ? What Compose is:
# * Docker Compose uses a YAML file to define and run multi‑container apps with one command.
# ~ Benefits:
# * one source of truth for services, networks, volumes, ports, and environment settings.

# ? Example docker-compose.yml:
# ^ services:
# ^   app:
# *     image: node:18
# *     working_dir: /app
# ^     volumes:
# *       - .:/app                    # map project files into container (bind mount for dev)
# *     command: sh -c "yarn install && yarn dev"
# ^     ports:
# *       - "127.0.0.1:3000:3000"
# ^     environment:
# *       DB_HOST: mysql
# *       DB_USER: root
# *       DB_PASSWORD: secret
# *       DB_NAME: todos
# *
# ^   mysql:
# *     image: mysql:8
# *     environment:
# *       MYSQL_ROOT_PASSWORD: secret
# *       MYSQL_DATABASE: todos
# ^     volumes:
# *       - todo-mysql-data:/var/lib/mysql
# *
# ^ volumes:
# *   todo-mysql-data:

# ? Run with Compose:
# * docker compose up -d      # starts both services in background
# * docker compose down       # stops and removes containers, networks (keeps named volumes unless --volumes is used)
# ~ Troubleshooting:
# * if port 3000 is busy (already used), stop the conflicting container or change the host port (e.g., 127.0.0.1:6000:3000).

# & Key definitions explained simply

# ? Base image:
# * A starting point with a preinstalled runtime (e.g., node:18 or python:3.11) from Docker Hub.

# ? Environment variables:
# * Small key/value settings the app reads at startup (e.g., DB passwords, hostnames). They keep configs out of code.

# ? Port mapping:
# * Lets you access a container’s internal port from your machine.
# * Format: HOST_PORT:CONTAINER_PORT (e.g., -p 127.0.0.1:3000:3000 exposes the app at localhost:3000).

# ? Bind mount vs volume (for completeness):

# ~ Bind mount:
# * maps a host folder directly into the container (great for local dev; changes reflect instantly).

# ~ Volume:
# * managed by Docker, better for persisting data in production and avoiding host‑specific paths.

# & Common pitfalls and safe habits

# ? Immutability of images:
# * You cannot “edit” an image; rebuild from Dockerfile after changes. Use tags (e.g., :v1, :v2) to track versions.

# ? Name conflicts and ports:
# * Reusing container names or occupied ports causes errors. Remove old containers: docker rm -f <name>.

# ? YAML strictness:
# * docker-compose.yml is sensitive to spaces/indentation. Misaligned indentation causes errors.

# ? Data safety:
# * Always mount volumes for databases; otherwise data vanishes when containers are removed.
# * For experiments, use separate volumes per project to avoid mixing data.

# ? Reproducibility mindset:
# * Keep Dockerfile minimal, deterministic, and documented.
# * Pin versions (e.g., node:18, mysql:8) for consistent builds.

# & Mental model recap

# ? Think in three layers:
# * Dockerfile → defines how to build
# * Image → the built artifact (read‑only)
# * Container → the running instance (stateful, isolated)

# ? For multi‑service apps:
# * Use networks so services can talk by name (e.g., DB_HOST=mysql).
# * Use volumes to persist state (e.g., database files).
# * Use Compose to define everything in one file and run with a single command.

# ? Outcome for a data engineer:
# * You can spin up (run) databases (MySQL, Postgres),
# * ETL workers (Airflow, Spark),
# * message brokers (Kafka), and analytics apps
# * in consistent, isolated environments—quickly, safely,
# * and reproducibly, which is essential for building real data pipelines.
