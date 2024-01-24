# Blog App

Posts CRUD app

## Prerequisites

- Docker
- Docker Compose

## Setup

1. **Setup Environment Variables**

   Create a `.env` file in the root directory of the project and add the necessary environment variables. based on
   .env.instance file


2. **Build and run the Docker containers**

    ```
    docker-compose up
    ```

   This command will start the Blog app and any other necessary services declared in `docker-compose.yml` file.

## Usage

Once the Docker containers are up and running, you can access the Blog app API at `http://localhost:8000`.

## GitHub Actions

1.Put these secrets in your remote repository secrets. the required .env file will be created automatically.

     SECRET_KEY=secret key
     DEBUG=1 
     PG_NAME=blog
     PG_USERNAME=postgres
     PG_PASSWORD=postgres
     PG_HOST=db
     PG_PORT=5432
     CELERY_BROKER_URL=redis://redis:6379
     CELERY_RESULT_BACKEND=redis://redis:6379
     REDIS_ADDRESS=redis://redis:6379

2.merge your commits in master branch and push to the remote repo.