.PHONY: help up down restart logs ps read clean reset-db

COMPOSE = docker compose -f docker-compose.yml

help: ## Exibe esta ajuda
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Sobe o monitor continuamente em segundo plano (com rebuild)
	$(COMPOSE) up -d --build

down: ## Para e remove o container
	$(COMPOSE) down

restart: ## Reinicia o container com rebuild
	$(COMPOSE) down
	$(COMPOSE) up -d --build

logs: ## Acompanha os logs em tempo real
	$(COMPOSE) logs -f

ps: ## Exibe o status do container
	$(COMPOSE) ps

read: ## Exibe os ultimos registros do banco sqlite
	@python3 read_log.py

reset-db: ## Remove o banco sqlite e CSVs antigos para recriar do zero
	@rm -f data/ping_log.db data/*.csv
	@echo "Dados antigos (SQLite e CSV) removidos com sucesso."

clean: down reset-db ## Para o container e remove os dados
