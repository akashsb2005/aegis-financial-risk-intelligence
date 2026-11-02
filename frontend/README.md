# AEGIS Frontend

The AEGIS frontend is a Next.js App Router application built with React, TypeScript, and Tailwind CSS. It integrates with the existing FastAPI backend for authentication and PostgreSQL-backed application data.

## Features

The current frontend provides:

- Account registration
- Login and logout
- Session-protected dashboard
- Company monitoring
- Risk assessment summary and history
- Financial-record viewing
- FastAPI API integration through a configurable API base URL

## Requirements

- Node.js 20.9 or later
- npm
- Running AEGIS FastAPI backend and configured PostgreSQL database

## Setup

From the `frontend` directory:

```powershell
npm ci
Copy-Item .env.example .env.local
```

Set `NEXT_PUBLIC_API_BASE_URL` in `.env.local` to the FastAPI v1 base URL. For local development:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

The Next.js rewrite forwards `/api/v1/*` requests to this API URL. Keep `.env.local` local and do not commit credentials or tokens.

## Run in development

The FastAPI backend and its PostgreSQL database must be configured and running. From the `frontend` directory:

```powershell
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Visitors can register an account and then sign in. Registration does not sign the user in automatically. A successful login opens the session-protected dashboard; users can sign out from there.

## Session storage limitation

The current frontend keeps the bearer session token in browser `sessionStorage` for the active tab. It is not stored in an HttpOnly cookie. This is a known security limitation; the implementation should not be considered production-grade authentication security.

## Production build

From the `frontend` directory, build the production application:

```powershell
npm run build
```

The current production build has been verified successfully. To serve the built application locally, run:

```powershell
npm start
```
