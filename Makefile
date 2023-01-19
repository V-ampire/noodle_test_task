build:
	docker compose -f docker-compose.dev.yml build;

up:
	docker compose -f docker-compose.dev.yml up --remove-orphans;

down:
	docker compose -f docker-compose.dev.yml down;

make bash:
	docker compose -f docker-compose.dev.yml exec django bash;

make createsuperuser:
	docker compose -f docker-compose.dev.yml exec django python manage.py createsuperuser;