# AEGIS Frontend

The frontend is a Next.js App Router application built with React, TypeScript, and Tailwind CSS. It currently provides a login-page shell and a dashboard placeholder; authentication and API requests are intentionally not connected yet.

## Requirements

- Node.js 20.9 or later
- npm

## Setup

From the `frontend` directory, install dependencies and create a local environment file:

```powershell
npm ci
Copy-Item .env.example .env.local
```

Set `NEXT_PUBLIC_API_BASE_URL` in `.env.local` to the FastAPI v1 base URL. The default example is `http://localhost:8000/api/v1`. This variable is reserved for the upcoming integration step and is not currently used by the UI.

Start the development server:

```powershell
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The login form is a visual placeholder and does not authenticate. The dashboard is available at `/dashboard` and displays no company or risk data.

## Production build

```powershell
npm run build
npm start
```
