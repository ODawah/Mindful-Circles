# Deploy Mindful Circles on Vercel

This repo can be deployed as one Vercel Services project plus one Turso database:

- `frontend`: Vite React frontend from the `frontend` directory, mounted at `/`.
- `backend`: FastAPI backend from the `backend` directory, mounted at `/api`.
- Turso: SQLite/libSQL database connected to the backend.

## 1. Create the database

1. Create a Turso database.
2. Copy the database URL. It should look like `libsql://...turso.io`.
3. Create/copy a Turso auth token.
4. Keep both values private.

## 2. Deploy the Vercel project

Create a new Vercel project from the GitHub repo.

Project settings:

- Application Preset: `Services`
- Root Directory: repo root

The root `vercel.json` defines the services:

```json
{
  "experimentalServices": {
    "frontend": {
      "entrypoint": "frontend",
      "routePrefix": "/",
      "framework": "vite"
    },
    "backend": {
      "entrypoint": "backend",
      "routePrefix": "/api",
      "framework": "fastapi"
    }
  }
}
```

Environment variables:

```text
TURSO_DATABASE_URL=libsql://your-database-your-org.turso.io
TURSO_AUTH_TOKEN=your-turso-auth-token
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
FRONTEND_ORIGINS=https://your-frontend.vercel.app
ENABLE_SCHEDULER=false
```

Deploy it, then open:

```text
https://your-project.vercel.app/api/health
```

Expected response:

```json
{"status":"ok"}
```

## 3. Update backend CORS

After the project has its final Vercel URL, update the environment variable:

```text
FRONTEND_ORIGINS=https://your-project.vercel.app
```

Redeploy after changing this value.

For previews or custom domains, add comma-separated origins:

```text
FRONTEND_ORIGINS=https://your-project.vercel.app,https://www.yourdomain.com
```

The frontend defaults to `VITE_API_BASE_URL=/api`, so it can call the backend
through the same Vercel domain without extra CORS work.

## 4. Important serverless note

Vercel does not keep a normal always-running Python server process. The backend now creates today's question lazily when `/circles/{circle_id}/questions/today` is called, so it does not depend on a background scheduler in production.
