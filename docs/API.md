# SDIP API Documentation

Base URL: `http://localhost:<PORT>/api`

## Authentication

### POST /auth/signup
Public endpoint. Creates a new user (role is always "user").

**Body:**
{
  "name": "string",
  "email": "string",
  "password": "string"
}

**Response (201):**
{
  "message": "User registered successfully",
  "user": { "id", "name", "email", "role" }
}

### POST /auth/login
Public endpoint. Logs in and sets an httpOnly cookie containing the JWT.

**Body:**
{
  "email": "string",
  "password": "string"
}

**Response (200):**
{
  "message": "Login successful",
  "user": { "id", "name", "email", "role" }
}

### GET /auth/me
Protected (requires valid cookie). Returns the logged-in user's own info.

**Response (200):**
{ "id", "name", "email", "role" }

## Users

### GET /users
Protected + Admin only. Returns list of all users.

**Response (200):**
[ { "id", "name", "email", "role" }, ... ]