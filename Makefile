dev:
	docker-compose -p homework -f ./docker/docker-compose.dev.yml up --remove-orphans

prod:
	docker compose -p homework -f ./docker/docker-compose.prod.yml up --build -V --remove-orphans -d
