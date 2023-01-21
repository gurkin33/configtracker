## ALL BELOW INFO IS FOR DEVELOPERS
Below commands can help to start and manage a development.
### Start developer containers
There are only two containers in this mode - database and api
```shell
docker-compose --env-file ./.env-dev -f ./docker-compose-dev.yml up
```

### Stop developer containers
```shell
docker-compose --env-file ./.env-dev -f ./docker-compose-dev.yml down
```

### Remove developer image
```shell
docker image rm configtracker-dev:latest
```

### Remove database and all config files:
```shell
docker-compose -f ./docker-compose-dev.yml down -v
```

### Connect to container:
```shell
docker exec -it configtracker-dev /bin/bash 
```
---

### Make release notes
#### Build release image (delete old interface before)
```shell
docker volume rm nginx-web
docker build --no-cache -t gurkin33/configtracker:<VERSION> -f ./api/Dockerfile .
```
#### Make new latest
```shell
docker tag gurkin33/configtracker:<VERSION> gurkin33/configtracker:latest
```
#### Simple test docker compose
```shell
docker-compose -f ./docker-compose.yml down -v
docker-compose -f ./docker-compose.yml up
```
### OR
#### Simple test docker
```shell
docker network rm configtracker-net
docker volume rm pgdata
docker volume rm repositories
docker volume rm settings
docker volume rm nginx-web

docker network create -d bridge configtracker-net
docker volume create pgdata
docker volume create repositories
docker volume create settings
docker volume create nginx-web

docker run --rm -d --name configtracker-db --env POSTGRES_DB='configtracker' \
--env POSTGRES_USER='configtracker' --env POSTGRES_PASSWORD='configtracker' \
--expose 5432 --network configtracker-net --volume pgdata:/var/lib/postgresql/data \
--net-alias postgres postgres:15-alpine

docker run --rm -d --name configtracker --env FLASK_APP='api/app.py' \
--env API_DATABASE='postgresql+psycopg2://configtracker:configtracker@postgres:5432/configtracker' \
--expose 5000 --network configtracker-net --volume repositories:/app/repositories \
--volume  settings:/app/settings --volume nginx-web:/app/dist \
--net-alias configtracker gurkin33/configtracker:<VERSION>

docker build --no-cache -t configtracker-nginx -f ./nginx/Dockerfile .

docker run --rm -d --name configtracker-nginx -p 80:80 -p 443:443 \
--network configtracker-net --volume nginx-web:/opt/dist/ configtracker-nginx
```
#### Push it to docker hub
```shell
docker push gurkin33/configtracker:<VERSION>
docker push gurkin33/configtracker:latest
```
