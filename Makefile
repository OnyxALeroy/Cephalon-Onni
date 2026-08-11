.PHONY: up down restart logs logs-backend logs-frontend logs-postgres logs-redis shell-backend shell-postgres shell-redis clean clean-volumes health setup

up:
	@./scripts/start-everything.sh

down:
	@docker compose down

restart:
	@docker compose down && docker compose up --build

logs:
	@docker compose logs -f

logs-backend:
	@docker compose logs -f backend

logs-frontend:
	@docker compose logs -f frontend

logs-postgres:
	@docker compose logs -f postgres

logs-redis:
	@docker compose logs -f redis

shell-backend:
	@docker exec -it cephalon-onni-backend /bin/sh

shell-postgres:
	@docker exec -it cephalon-onni-postgres psql -U postgres -d cephalon_onni

shell-redis:
	@docker exec -it cephalon-onni-redis redis-cli

clean:
	@docker compose down --remove-orphans
	@docker image prune -f

clean-volumes:
	@docker compose down -v
	@docker volume prune -f

health:
	@echo "Checking services..." && \
	docker ps --filter "name=cephalon-onni" --format "table {{.Names}}\t{{.Status}}" | grep cephalon-onni

setup:
	@if [ ! -f .env ]; then cp .env.example .env && echo "Created .env from .env.example"; else echo ".env already exists"; fi
