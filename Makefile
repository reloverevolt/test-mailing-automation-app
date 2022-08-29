compose := docker-compose

init: init-envs pre-commit
init-envs:	## Generate '.env' and 'config.yaml' files based on example files.
	cp env.example .env
	cp config.example.yaml config.yaml

build:	## Build all project services.
	sudo $(compose) up --build -d

stop:	## Stop project compose.
	sudo $(compose) stop

full-migrate: makemigrations migrate	## Run migrate and makemigrations at the same time
makemigrations:	## Run django management command 'makemigrations'
	sudo $(compose) exec web ./manage.py makemigrations
migrate:	## Run django management command 'migrate'
	sudo $(compose) exec web ./manage.py migrate

shell:	## Run shell_plus with ptpython
	sudo $(compose) exec web /backend/manage.py shell_plus
collectstatic:	## Run django management command 'collectstatic'
	sudo $(compose) exec web ./manage.py collectstatic
admin:	## Run django management command 'createsuperuser'
	sudo $(compose) exec web ./manage.py createsuperuser

web-build:	## Build django service.
	sudo $(compose) up -d --build web
web-logs:	## Run django logs.
	sudo $(compose) logs -f web

db-build:  ## Build db service.
	sudo $(compose) up -d --build db
db-logs:  ## Run db logs.
	sudo $(compose) logs -f db

pre-commit:	## Install and use pre-commit config.
	pip install pre-commit --upgrade
	pre-commit install

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
