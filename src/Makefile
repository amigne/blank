ENV ?= dev
SERVICE *= app

COMPOSE = ./bin/compose ${ENV}

.PHONY:
init
config
build
pull
up
start
stop
restart
down
logs
ps
shell
run
test
destroy

init:
	./bin/init-dev

config:
	$(COMPOSE) config --quiet

build:
	$(COMPOSE) build --pull

pull:
	$(COMPOSE) pull

up: config
	$(COMPOSE) up -d --remove-orphans

start:
	$(COMPOSE) start

stop:
	$(COMPOSE) stop

restart:
	$(COMPOSE) restart

down:
	$(COMPOSE) down --remove-orphans

logs:
	$(COMPOSE) logs --follow --tail=200 $(SERVICE)

ps:
	$(COMPOSE) ps

shell:
	$(COMPOSE) exec $(SERVICE) sh

run:
	@test -n "$(CMD)" ||
	(echo "CMD is required."; exit 1)
	$(COMPOSE) run --rm $(SERVICE) $(CMD)

test:
	./bin/compose test up /
	  --build /
	  --abort-on-container-exit /
	  --exit-code-from app
	./bin/compose test down /
	  --volumes /
	  --remove-orphans

destroy:
	@test "$(CONFIRM)" = "yes" ||
	(echo "Use CONFIRM=yes to delete containers and volumes"; exit 1)
	$(COMPOSE) down /
	  --volumes /
	  --remove-orphans
