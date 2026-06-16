.PHONY: test lint thesis docker-up docker-down docker-build docker-logs help

help:
	@echo "Available targets:"
	@echo "  test          Run voctocore unit tests"
	@echo "  lint          Run PEP8 style check"
	@echo "  thesis        Compile LaTeX thesis (memoria_tfg/)"
	@echo "  thesis-clean  Remove LaTeX build artifacts"
	@echo "  docker-build  Build Docker image"
	@echo "  docker-up     Start full Docker stack"
	@echo "  docker-down   Stop Docker stack"
	@echo "  docker-logs   Follow logs for all services"
	@echo "  docker-ps     Show service health status"

test:
	./voctocore/test.sh

lint:
	./check_pep8.sh

thesis:
	cd memoria_tfg && latexmk -pdf main.tex

thesis-clean:
	cd memoria_tfg && latexmk -C

thesis-watch:
	cd memoria_tfg && latexmk -pdf -pvc main.tex

docker-build:
	docker compose build

docker-up:
	xhost +local:$$(id -un)
	./launch_docker_studio.sh

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-ps:
	docker compose ps

docker-restart:
	docker compose down
	./launch_docker_studio.sh
