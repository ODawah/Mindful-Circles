# Deploy Mindful Circles with Docker Compose

This setup runs everything in Docker:

- React frontend served by Nginx
- FastAPI backend
- Postgres database stored in a Docker volume
- Alembic migrations run automatically before the backend starts

## Local Run

From the repo root:

```bash
docker compose up -d --build
```

Open:

```text
http://localhost:8080
```

The frontend proxies API requests through Nginx:

```text
http://localhost:8080/api/health
```

Useful commands:

```bash
docker compose ps
docker compose logs -f backend frontend database
docker compose down
```

The Postgres data is kept in the `pgdata` Docker volume. `docker compose down`
does not delete it. Only remove the volume if you intentionally want to erase
the database:

```bash
docker compose down -v
```

## Public Deployment

Docker Compose needs a server that can run Docker. For a no-paid-Postgres setup,
run this Compose stack on a VM and let the `database` service store data in the
Docker volume.

Before putting it on the internet:

1. Copy `.env.example` to `.env`.
2. Replace `SECRET_KEY` with a long random value.
3. Set `FRONTEND_ORIGINS` to your public site origin.
4. Open the chosen frontend port on the server firewall.
5. Put HTTPS in front of the app with a reverse proxy such as Caddy, Traefik, or
   Nginx plus Let's Encrypt.

Example production `.env`:

```text
FRONTEND_PORT=80
VITE_API_BASE_URL=/api
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
FRONTEND_ORIGINS=https://your-domain.example
ENABLE_SCHEDULER=true
```

## Free Hosting Reality

The Compose file removes the need to buy a separate Postgres host, but it does
not remove the need for a machine that stays online.

The closest free fit is an always-free VM where you install Docker and run:

```bash
docker compose up -d --build
```

Free platform services usually have limits that matter for this app:

- Some do not run a full multi-service `docker-compose.yml`.
- Some free databases expire or have very small storage.
- Some free web services sleep when idle.
- A single Docker volume is not a production-grade backup strategy.

For a hobby project, a free VM plus this Compose file is reasonable. For real
users, add database backups and expect to pay for hosting eventually.
