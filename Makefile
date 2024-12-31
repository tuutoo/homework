prod:
	docker compose -p homework-prod -f ./docker-compose.prod.yml up --build -V --remove-orphans -d
