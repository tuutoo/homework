IMAGE ?= tuutoo/homework
TAG ?= latest

.PHONY: build push publish prod

build:
	docker build -t $(IMAGE):$(TAG) .

push:
	docker push $(IMAGE):$(TAG)

publish: build push

prod:
	docker compose -p homework-prod -f ./docker-compose.prod.yml up -d --remove-orphans
