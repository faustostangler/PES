# ==============================================================================
# PES / Cresmo Infrastructure Control Plane
# Binary State: All Running vs Nothing Running (KISS Principle)
# ==============================================================================

SHELL := /bin/bash
.DEFAULT_GOAL := up

COMPOSE_FILES := -f docker-compose.langfuse.yml -f docker-compose.yml

.PHONY: up
up:
	@echo "Starting all required services..."
	docker compose $(COMPOSE_FILES) up -d
	@echo "All services are up and running."

.PHONY: down
down:
	@echo "Stopping all services..."
	docker compose $(COMPOSE_FILES) down --remove-orphans
	@echo "All services have been shut down."

.PHONY: seed
seed:
	@echo "Seeding canonical prompts into Langfuse..."
	uv run cresmo seed-prompts

