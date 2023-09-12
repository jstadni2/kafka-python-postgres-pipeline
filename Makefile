CONTAINERS := $(shell docker ps -a -q)

# All targets are phony
.PHONY: *

test-component:
	pytest -m component tests/ --fixture_scope=session

test-integration:
	pytest -m integration tests/ --fixture_scope=session

clean:
	rm -rf .pytest_cache
	python3 -Bc "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
	python3 -Bc "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]"

containers:
	@echo $(CONTAINERS)

# This would be safer if it cleaned specific containers and images
clean-docker:
	docker stop $(CONTAINERS)
	docker system prune -f

# Pulling these images actually got the test suites to work
# TODO: Get docker-compose to work in lieu of these targets 

pull-zk:
	docker pull confluentinc/cp-zookeeper:7.5.0

pull-server:
	docker pull confluentinc/cp-server:7.5.0

pull-postgres:
	docker pull postgres:15.4

pull-services: pull-zk pull-server pull-postgres

# Docker image troubleshooting

postgres-run:
	docker run --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword -d postgres:15.4

postgres-psql:
	docker run -it --rm --network some-network postgres psql -h some-postgres -U postgres:15.4