# SDIP Backend

Backend service for Sanestix Data Intelligence Platform (SDIP), built with Express.js and MongoDB.

## Setup

1. Install dependencies:
   npm install (inside backend/)
   npm install (inside database/)

2. Create `.env` file (copy from `.env.example`) and fill in values.

3. Seed the first admin (one-time, from repo root):
   node database/seed.js

## Running

npm run dev   (inside backend/)

Server runs on the port specified in `.env`.

## Features Implemented So Far

- User authentication (signup, login) with JWT stored in httpOnly cookies
- Role-based access control (admin, user)
- Protected routes via middleware
- Logout (clears auth cookie)
- Forgot password flow with OTP verification via email
- Job creation and tracking (create, list, status check)
- Results retrieval per job

## API Endpoints

See `docs/API.md` for full endpoint details.
