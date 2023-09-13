CONTAINERS := $(shell docker ps -a -q)

# All targets are phony
.PHONY: *

up:
	docker-compose up -d

down:
	docker-compose down

test-component:
	pytest -m component tests/

test-integration:
	pytest -m integration tests/

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


# Docker image troubleshooting

postgres-run:
	docker run --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword -d postgres:15.4

postgres-psql:
	docker run -it --rm --network some-network postgres psql -h some-postgres -U postgres:15.4