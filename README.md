# Home task

## Prerequisites

- [docker](https://www.docker.com/)
- [docker-compose](https://docs.docker.com/compose/)

## The repository structure

- `crawler_service/`: Django backend with job manager (python 3.10).
- `nginx/`: UI static files and configuration for nginx.

## Production mode

- Deliver the code to the production machine.
- Make sure the `.env.prod` file contains the correct environment variables. Check who has access to it.
- `docker-compose --env-file ./.env.prod up` - build and start services.
- Bind 8080 port of the application with the external port if needed.
- Go to `http://<your_hostname>:8080/` or `http://<your_hostname>:8080/api/jobs/`.

## Development mode

- `docker-compose -f ./docker-compose.yml -f ./docker-compose-dev.yml --env-file ./.env.dev up`
