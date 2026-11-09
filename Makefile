
.PHONY: runserver migrations makemigrations migrate test check \
        send-mails run run-d down logs shell \
        celery-worker celery-beat tailwind build-css

# Django avec uv
UV = uv run --env-file .env

# ----------------------------------------
# Django - Développement local
# ----------------------------------------

runserver:
	$(UV) python manage.py runserver

migrations makemigrations:
	$(UV) python manage.py makemigrations

migrate:
	$(UV) python manage.py migrate

test:
	$(UV) python manage.py test

check:
	$(UV) python manage.py check

shell:
	$(UV) python manage.py shell

# ----------------------------------------
# Emails - Django Post Office
# ----------------------------------------

send-mails:
	$(UV) python manage.py send_queued_mail

# ----------------------------------------
# Celery - Développement local
# ----------------------------------------

celery-worker:
	$(UV) celery -A config worker --loglevel=info

celery-beat:
	$(UV) celery -A config beat --loglevel=info

# ----------------------------------------
# Tailwind CSS - pnpm
# ----------------------------------------

tailwind:
	pnpm run dev

build-css:
	pnpm run build

# ----------------------------------------
# Docker Compose
# ----------------------------------------

run:
	docker compose up --build

run-d:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

check-env:
	$(UV) python manage.py shell -c "from django.conf import settings; d=settings.DATABASES['default']; print(d['HOST'], d['PORT'], d['NAME'])"

# ----------------------------------------
# Django dans Docker
# ----------------------------------------

migrate-docker:
	docker compose exec web python manage.py migrate

send-mails-docker:
	docker compose exec web python manage.py send_queued_mail

