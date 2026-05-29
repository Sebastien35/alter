install-dev:
	uv pip install --editable .[dev]

up-dev:
	docker compose -f docker/compose-dev.yml up -d