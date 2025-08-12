SHELL := /bin/bash
IMAGE ?= py-demo-project:dev
SERVICE ?= web
N ?= 12

.PHONY: build up up-build down restart logs ps curl-debug curl-fib open clean

build:
	@echo "Building image $(IMAGE) ..."
	docker build -t $(IMAGE) .

up:
	@echo "Starting compose service $(SERVICE) ..."
	docker compose up -d $(SERVICE)

up-build:
	@echo "Building and starting compose service $(SERVICE) ..."
	docker compose up -d --build $(SERVICE)

restart:
	@echo "Restarting compose service $(SERVICE) ..."
	docker compose restart $(SERVICE)

logs:
	docker compose logs -f $(SERVICE)

ps:
	docker compose ps

down:
	@echo "Stopping and removing compose services ..."
	docker compose down

curl-debug:
	@echo "Calling /debug to trigger attach ..."
	curl -fsS http://127.0.0.1:5455/debug || true

curl-fib:
	@echo "Calling /fib/$(N) ..."
	curl -fsS http://127.0.0.1:5455/fib/$(N) || true

open:
	@URL="http://127.0.0.1:5455"; \
	if command -v open >/dev/null 2>&1; then open "$$URL"; \
	elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$$URL"; \
	else echo "Open $$URL in your browser"; fi

clean:
	-@docker rm -f py-demo-web 2>/dev/null || true
	-@docker rmi -f $(IMAGE) 2>/dev/null || true
