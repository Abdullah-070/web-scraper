# SDIP API Documentation

Base URL: `http://localhost:<PORT>/api`

## Authentication

### POST /auth/register
Public. Creates a new user with the default role of `user`.

**Body:**
```json
{ "name": "string", "email": "string", "password": "string" }
```

**Success Response (201):**
```json
{
  "message": "User registered successfully",
  "user": { "id": "string", "name": "string", "email": "string", "role": "user" }
}
```

**Error Responses:**
- `400` - Missing fields: `{ "message": "Please provide all required fields" }`
- `400` - User already exists: `{ "message": "User already exists" }`

### POST /auth/login
Public. Authenticates a user and sets an httpOnly JWT cookie.

**Body:**
```json
{ "email": "string", "password": "string" }
```

**Success Response (200):**
```json
{
  "message": "Login successful",
  "user": { "id": "string", "name": "string", "email": "string", "role": "user" }
}
```

**Error Responses:**
- `400` - Missing fields: `{ "message": "Please provide all required fields" }`
- `400` - Invalid email: `{ "message": "Invalid credentials email" }`
- `400` - Invalid password: `{ "message": "Invalid credentials" }`

### POST /auth/logout
Protected. Clears the auth cookie.

**Success Response (200):**
```json
{ "message": "Logout successful" }
```

**Error Responses:**
- `401` - Unauthorized: depends on `authMiddleware`

### GET /auth/me
Protected. Returns the authenticated user's profile.

**Success Response (200):**
```json
{
  "message": "User found",
  "user": {
    "_id": "string",
    "name": "string",
    "email": "string",
    "role": "user"
  }
}
```

**Error Responses:**
- `404` - User not found: `{ "message": "User not found" }`
- `401` - Unauthorized: depends on `authMiddleware`

### POST /auth/forgot-password
Public. Generates an OTP, stores it on the user record, and sends it by email.

**Body:**
```json
{ "email": "string" }
```

**Success Response (200):**
```json
{ "message": "OTP sent to email" }
```

**Error Responses:**
- `404` - User not found: `{ "message": "User not found" }`
- `500` - Server error: `{ "message": "Error occurred while processing forgot password request" }`

### POST /auth/verify-otp
Public. Verifies the OTP sent to email.

**Body:**
```json
{ "email": "string", "otp": "string" }
```

**Success Response (200):**
```json
{ "message": "OTP verified successfully" }
```

**Error Responses:**
- `404` - User not found: `{ "message": "User not found" }`
- `400` - No OTP requested: `{ "message": "No OTP found, please request a new one." }`
- `400` - OTP expired: `{ "message": "OTP has expired" }`
- `400` - Wrong OTP: `{ "message": "Invalid OTP" }`
- `400` - Too many attempts: `{ "message": "Maximum OTP attempts exceeded. Please request a new OTP." }`

### POST /auth/reset-password
Public. Resets the password after OTP verification.

**Body:**
```json
{ "email": "string", "newPassword": "string" }
```

**Success Response (200):**
```json
{ "message": "Password reset successful" }
```

**Error Responses:**
- `404` - User not found: `{ "message": "User not found" }`
- `400` - OTP not verified: `{ "message": "OTP not verified. Please verify OTP before resetting password." }`

## Users

### GET /users
Protected. Admin only. Returns all users without passwords.

**Success Response (200):**
```json
{
  "users": [
    { "_id": "string", "name": "string", "email": "string", "role": "user" }
  ]
}
```

**Error Responses:**
- `401` - Unauthorized: depends on `authMiddleware`
- `403` - Forbidden: depends on `roleMiddleware`
- `500` - Server error: `{ "message": "Internal server error" }`

## Jobs

### POST /jobs
Protected. User only. Creates a new scraping job for the logged-in user.
After creation, the job payload is pushed to Redis queue `jobQueue` for background processing.

**Body:**
```json
{
  "scraperType": "string",
  "inputParams": {}
}
```

**Success Response (201):**
```json
{
  "message": "Job created successfully",
  "job": {
    "_id": "string",
    "userId": "string",
    "scraperType": "string",
    "inputParams": {},
    "status": "pending"
  }
}
```

**Error Responses:**
- `401` - Unauthorized: depends on `authMiddleware`
- `403` - Forbidden: depends on `roleMiddleware`

### GET /jobs
Protected. User only. Returns all jobs created by the logged-in user.

**Success Response (200):**
```json
{
  "message": "User jobs fetched successfully",
  "jobs": [
    {
      "_id": "string",
      "userId": "string",
      "scraperType": "string",
      "inputParams": {},
      "status": "pending"
    }
  ]
}
```

**Error Responses:**
- `401` - Unauthorized: depends on `authMiddleware`
- `403` - Forbidden: depends on `roleMiddleware`
- `404` - No jobs found: `{ "message": "No jobs found for this user" }`

### GET /jobs/:id
Protected. User only. Returns a single job by ID if it belongs to the logged-in user.

**Path Params:**
```json
{ "id": "string" }
```

**Success Response (200):**
```json
{
  "message": "Job fetched successfully",
  "job": {
    "_id": "string",
    "userId": "string",
    "scraperType": "string",
    "inputParams": {},
    "status": "pending"
  }
}
```

**Error Responses:**
- `401` - Unauthorized: depends on `authMiddleware`
- `403` - Forbidden: depends on `roleMiddleware`
- `403` - Not job owner: `{ "message": "You are not authorized to view this job" }`
- `404` - Job not found: `{ "message": "Job not found" }`

## Results

### GET /results/:jobId
Protected. User only. Returns all results for a job that belongs to the logged-in user.

**Path Params:**
```json
{ "jobId": "string" }
```

**Success Response (200):**
```json
{
  "message": "Job results fetched successfully",
  "results": [
    {
      "_id": "string",
      "jobId": "string",
      "userId": "string",
      "scraperType": "string",
      "data": {}
    }
  ]
}
```

**Error Responses:**
- `401` - Unauthorized: depends on `authMiddleware`
- `403` - Forbidden: depends on `roleMiddleware`
- `403` - Not job owner: `{ "message": "You are not authorized to view this job results" }`
- `404` - Job not found: `{ "message": "Job not found" }`
- `404` - No results found: `{ "message": "No results found for this job" }`