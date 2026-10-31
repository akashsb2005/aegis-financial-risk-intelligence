# AEGIS Frontend

The frontend is a Next.js App Router application built with React, TypeScript, and Tailwind CSS. It provides login and logout through the existing FastAPI authentication endpoints and a dashboard placeholder. Company and risk data are not connected.

## Requirements

- Node.js 20.9 or later
- npm

## Setup

From the `frontend` directory, install dependencies and create a local environment file:

```powershell
npm ci
Copy-Item .env.example .env.local
```

Set `NEXT_PUBLIC_API_BASE_URL` in `.env.local` to the FastAPI v1 base URL. The default example is `http://localhost:8000/api/v1`. Next.js proxies `/api/v1/*` requests to this configured URL so browser requests remain same-origin.

Start the development server:

```powershell
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Sign in with an existing backend account; successful login opens `/dashboard`, where the session is checked and can be ended with **Sign out**. The bearer token is stored in `sessionStorage` for the current browser tab. It is not stored in an HttpOnly cookie; avoid untrusted scripts and use HTTPS outside local development. The dashboard displays no company or risk data.

## Production build

```powershell
npm run build
npm start
```
