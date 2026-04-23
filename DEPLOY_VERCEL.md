# Deploy Mindful Circles on Vercel

This repo should be deployed as two Vercel projects plus one Turso database:

- `mindful-circles-api`: FastAPI backend from the `backend` directory.
- `mindful-circles-web`: Vite React frontend from the `frontend` directory.
- Turso: SQLite/libSQL database connected to the backend.

## 1. Create the database

1. Create a Turso database.
2. Copy the database URL. It should look like `libsql://...turso.io`.
3. Create/copy a Turso auth token.
4. Keep both values private.

## 2. Deploy the backend

Create a new Vercel project from the same GitHub repo.

Project settings:

- Root Directory: `backend`
- Framework Preset: Other / FastAPI auto-detected
- Build Command: `alembic upgrade head`
- Output Directory: leave empty
- Install Command: leave default

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
https://your-backend.vercel.app/health
```

Expected response:

```json
{"status":"ok"}
```

## 3. Deploy the frontend

Create a second Vercel project from the same GitHub repo.

Project settings:

- Root Directory: `frontend`
- Framework Preset: Vite
- Build Command: `npm run build`
- Output Directory: `dist`

Environment variables:

```text
VITE_API_BASE_URL=https://your-backend.vercel.app
```

Deploy it.

## 4. Update backend CORS

After the frontend has its final Vercel URL, update the backend project environment variable:

```text
FRONTEND_ORIGINS=https://your-frontend.vercel.app
```

Redeploy the backend after changing this value.

For previews or custom domains, add comma-separated origins:

```text
FRONTEND_ORIGINS=https://your-frontend.vercel.app,https://www.yourdomain.com
```

## 5. Important serverless note

Vercel does not keep a normal always-running Python server process. The backend now creates today's question lazily when `/circles/{circle_id}/questions/today` is called, so it does not depend on a background scheduler in production.
