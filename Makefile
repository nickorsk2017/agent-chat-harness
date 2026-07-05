# agent-chat — one-command control of the full stack (frontend + backend + mcp).
# Requires Docker with the Compose v2 plugin (`docker compose`).

COMPOSE ?= docker compose

.DEFAULT_GOAL := help

.PHONY: help up up-fg down build rebuild logs ps restart clean

help: ## Show this help
	@echo "agent-chat — available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

up: ## Build (if needed) and start the whole stack in the background
	$(COMPOSE) up -d --build

up-fg: ## Start the whole stack in the foreground (Ctrl-C to stop)
	$(COMPOSE) up --build

down: ## Stop and remove the stack's containers and network
	$(COMPOSE) down

build: ## Build all service images without starting them
	$(COMPOSE) build

rebuild: ## Rebuild images from scratch (no cache)
	$(COMPOSE) build --no-cache

logs: ## Follow logs from all services
	$(COMPOSE) logs -f

ps: ## Show the status of the stack's services
	$(COMPOSE) ps

restart: ## Restart all services
	$(COMPOSE) restart

clean: ## Stop the stack and remove volumes and locally-built images
	$(COMPOSE) down -v --rmi local
