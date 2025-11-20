#
# & Essential Docker Commands Cheat-Sheet

# ? Check Docker installation
# * docker --version          # shows installed Docker version
# * docker run hello-world    # runs a test container to verify setup

# ? Images (blueprints of containers)
# * docker build -t myapp .   # build image from Dockerfile in current directory
# * docker images             # list all images
# * docker rmi myapp          # remove an image

# ? Containers (running instances of images)
# * docker run -d -p 3000:3000 --name myapp myimage
#   -d = detached (background)
#   -p = port mapping (HOST:CONTAINER)
#   --name = assign container name
# * docker ps                 # list running containers
# * docker ps -a              # list all containers (including stopped)
# * docker stop myapp         # stop a running container
# * docker start myapp        # start a stopped container
# * docker rm myapp           # remove a container

# ? Volumes (persistent data storage)
# * docker volume create mydata       # create a named volume
# * docker run -v mydata:/app/data myimage
#   -v = mount volume into container
# * docker volume ls                  # list volumes
# * docker volume inspect mydata      # show details of a volume

# ? Networks (connect containers together)
# * docker network create mynet       # create a network
# * docker run --network=mynet myimage
# * docker network ls                 # list networks

# ? Docker Compose (multi-container apps)
# * docker compose up -d              # start all services in background
# * docker compose down               # stop and remove services
# * docker compose ps                 # list services managed by Compose

# ? Cleanup (free space)
# * docker system prune -a            # remove unused containers, images, networks


hat we're going to do is use Docker to completely run everything here so let's go ahead and take a look at what that
1:25:17
looks like because we've made everything and hooked everything up with Docker compos it's going to be a simple as this
1:25:25
all we have to do inside of our terminal obviously make sure that we're in the directory that we created I'm going to