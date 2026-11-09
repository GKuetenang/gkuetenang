# --------------------------------------
# Stage 1 : Tailwind CSS avec pnpm
# --------------------------------------
FROM node:24-alpine AS frontend

WORKDIR /app

# Activer pnpm via Corepack
RUN corepack enable

# Copier les manifestes pour optimiser le cache
COPY package.json pnpm-lock.yaml ./

# Installer les dépendances exactement
# comme définies dans pnpm-lock.yaml
RUN --mount=type=cache,id=pnpm-store,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile

# Copier le code source
COPY . .

# Compiler Tailwind CSS pour la production
RUN pnpm run build


# --------------------------------------
# Stage 2 : Python / uv
# --------------------------------------
FROM python:3.13-slim AS builder

# Installer uv depuis l'image officielle
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /uvx /bin/

ENV UV_PYTHON_DOWNLOADS=0 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

WORKDIR /app

# Installer les dépendances en conservant
# le cache si le code source change
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY . .

# Vérifier le lockfile et installer le projet
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable


# --------------------------------------
# Stage 3 : Production
# --------------------------------------
FROM python:3.13-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Utilisateur non-root
RUN groupadd --system appgroup \
    && useradd --system --gid appgroup \
       --create-home appuser \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R appuser:appgroup /app

# Environnement Python déjà installé
COPY --from=builder /opt/venv /opt/venv

# Code Django
COPY --chown=appuser:appgroup . .

# Assets frontend générés par Vite
COPY --from=frontend \
    --chown=appuser:appgroup \
    /app/static/ \
    /app/static/

USER appuser

EXPOSE 8000

CMD ["gunicorn", \
     "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
