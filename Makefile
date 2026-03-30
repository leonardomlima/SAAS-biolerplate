up:
	docker compose up -d --build

down:
	docker compose down

migrate:
	cd backend && poetry run alembic upgrade head

seed:
	cd backend && poetry run python ../infra/scripts/seed_db.py

test-backend:
	cd backend && poetry run pytest -v --cov=app

frontend-dev:
	cd frontend && npm run dev

bootstrap:
	$(MAKE) migrate
	$(MAKE) seed
	cd frontend && npm run build
