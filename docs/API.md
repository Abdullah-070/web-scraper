# SDIP API Documentation

Base URL: `http://localhost:<PORT>/api`

## Response Format

All API responses follow this standardized structure:

**Success:**

```json
{
  "success": true,
  "message": "...",
  "data": {} // Can be an object, array, or null
}
```

**Error:**

```json
{
  "success": false,
  "message": "..."
}
```

## Authentication

### POST /auth/register

Public. Creates a new user with the default role of `user`.

**Body:**

```json
{ 
  "name": "string (min 3 chars)", 
  "email": "string (valid email)", 
  "password": "string (min 6 chars)" 
}
```

**Success Response (201):**

```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "id": "string",
    "name": "string",
    "email": "string",
    "role": "user"
  }
}
```

**Error Responses:**

- `400` - `{ "success": false, "message": "Name must be atleast 3 characters" }`
- `400` - `{ "success": false, "message": "Invalid Email Address" }`
- `400` - `{ "success": false, "message": "Password must be atleast 6 characters" }`
- `400` - `{ "success": false, "message": "Please provide all required fields" }`
- `400` - `{ "success": false, "message": "User already exists with this email" }`

### POST /auth/login

Public. Authenticates a user and sets an httpOnly JWT cookie.

**Body:**

```json
{ 
  "email": "string (valid email)", 
  "password": "string (min 6 chars)" 
}
```

**Success Response (200):**

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "id": "string",
    "name": "string",
    "email": "string",
    "role": "user"
  }
}
```

**Error Responses:**

- `400` - `{ "success": false, "message": "Invalid Email Address" }`
- `400` - `{ "success": false, "message": "Password must be atleast 6 characters" }`
- `400` - `{ "success": false, "message": "Please provide both email and password" }`
- `400` - `{ "success": false, "message": "Invalid credentials" }`

### POST /auth/logout

Protected. Clears the auth cookie.

**Success Response (200):**

```json
{
  "success": true,
  "message": "Logout successful",
  "data": null
}
```

**Error Responses:**

- `401` - `{ "success": false, "message": "Unauthorized: No token provided" }`
- `401` - `{ "success": false, "message": "Unauthorized: Invalid token" }`

### GET /auth/me

Protected. Returns the authenticated user's profile.

**Success Response (200):**

```json
{
  "success": true,
  "message": "User fetched successfully",
  "data": {
    "_id": "string",
    "name": "string",
    "email": "string",
    "role": "user"
  }
}
```

**Error Responses:**

- `401` - `{ "success": false, "message": "Unauthorized: No token provided" }`
- `401` - `{ "success": false, "message": "Unauthorized: Invalid token" }`
- `403` - `{ "success": false, "message": "Forbidden: Insufficient role" }`
- `404` - `{ "success": false, "message": "User not found" }`

### POST /auth/forgot-password

Public. Generates an OTP, stores it on the user record, and sends it by email.

**Body:**

```json
{ 
  "email": "string (valid email)" 
}
```

**Success Response (200):**

```json
{
  "success": true,
  "message": "OTP sent to email",
  "data": null
}
```

**Error Responses:**

- `400` - `{ "success": false, "message": "Invalid Email Address" }`
- `404` - `{ "success": false, "message": "User not found" }`

### POST /auth/verify-otp

Public. Verifies the OTP sent to email.

**Body:**

```json
{ 
  "email": "string (valid email)", 
  "otp": "string (exactly 6 digits)" 
}
```

**Success Response (200):**

```json
{
  "success": true,
  "message": "OTP verified successfully",
  "data": null
}
```

**Error Responses:**

- `400` - `{ "success": false, "message": "Invalid Email Address" }`
- `400` - `{ "success": false, "message": "OTP must be 6 digits" }`
- `404` - `{ "success": false, "message": "User not found" }`
- `400` - `{ "success": false, "message": "No OTP found, please request a new one." }`
- `400` - `{ "success": false, "message": "OTP has expired" }`
- `400` - `{ "success": false, "message": "Invalid OTP" }`
- `400` - `{ "success": false, "message": "Maximum OTP attempts exceeded. Please request a new OTP." }`

### POST /auth/reset-password

Public. Resets the password after OTP verification.

**Body:**

```json
{ 
  "email": "string (valid email)", 
  "newPassword": "string (min 6 chars)" 
}
```

**Success Response (200):**

```json
{
  "success": true,
  "message": "Password reset successful",
  "data": null
}
```

**Error Responses:**

- `400` - `{ "success": false, "message": "Invalid Email Address" }`
- `400` - `{ "success": false, "message": "Password must be atleast 6 characters" }`
- `404` - `{ "success": false, "message": "User not found" }`
- `400` - `{ "success": false, "message": "OTP not verified. Please verify OTP before resetting password." }`

## Users

### GET /users

Protected. Admin only. Returns all users without passwords.

**Success Response (200):**

```json
{
  "success": true,
  "message": "Users fetched successfully",
  "data": [
    {
      "_id": "string",
      "name": "string",
      "email": "string",
      "role": "user"
    }
  ]
}
```

**Error Responses:**

- `401` - `{ "success": false, "message": "Unauthorized: No token provided" }`
- `401` - `{ "success": false, "message": "Unauthorized: Invalid token" }`
- `403` - `{ "success": false, "message": "Forbidden: Insufficient role" }`

## Jobs

### POST /jobs

Protected. User only. Creates a new scraping job for the logged-in user.
After creation, the job payload is pushed to Redis queue `jobQueue` for background processing.

**Body:**

```json
{
  "scraperType": "string (required)",
  "inputParams": "object (required, cannot be empty)"
}
```

**Success Response (201):**

```json
{
  "success": true,
  "message": "Job created successfully",
  "data": {
    "_id": "string",
    "userId": "string",
    "scraperType": "string",
    "inputParams": {},
    "status": "pending"
  }
}
```

**Error Responses:**

- `400` - `{ "success": false, "message": "Scraper type is required" }`
- `400` - `{ "success": false, "message": "inputParams cannot be empty" }`
- `401` - `{ "success": false, "message": "Unauthorized: No token provided" }`
- `401` - `{ "success": false, "message": "Unauthorized: Invalid token" }`
- `403` - `{ "success": false, "message": "Forbidden: Insufficient role" }`

### GET /jobs

Protected. User only. Returns all jobs created by the logged-in user.

**Success Response (200):**

```json
{
  "success": true,
  "message": "User jobs fetched successfully",
  "data": [
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

- `401` - `{ "success": false, "message": "Unauthorized: No token provided" }`
- `401` - `{ "success": false, "message": "Unauthorized: Invalid token" }`
- `403` - `{ "success": false, "message": "Forbidden: Insufficient role" }`
- `404` - `{ "success": false, "message": "No jobs found for this user" }`

### GET /jobs/:id

Protected. User only. Returns a single job by ID if it belongs to the logged-in user.

**Path Params:**

```json
{ "id": "string" }
```

**Success Response (200):**

```json
{
  "success": true,
  "message": "Job fetched successfully",
  "data": {
    "_id": "string",
    "userId": "string",
    "scraperType": "string",
    "inputParams": {},
    "status": "pending"
  }
}
```

**Error Responses:**

- `401` - `{ "success": false, "message": "Unauthorized: No token provided" }`
- `401` - `{ "success": false, "message": "Unauthorized: Invalid token" }`
- `403` - `{ "success": false, "message": "Forbidden: Insufficient role" }`
- `403` - `{ "success": false, "message": "You are not authorized to view this job" }`
- `404` - `{ "success": false, "message": "Job not found" }`

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
  "success": true,
  "message": "Job results fetched successfully",
  "data": [
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

- `401` - `{ "success": false, "message": "Unauthorized: No token provided" }`
- `401` - `{ "success": false, "message": "Unauthorized: Invalid token" }`
- `403` - `{ "success": false, "message": "Forbidden: Insufficient role" }`
- `403` - `{ "success": false, "message": "You are not authorized to view this job results" }`
- `404` - `{ "success": false, "message": "Job not found" }`
- `404` - `{ "success": false, "message": "No results found for this job" }`

## Export

### GET /export/:jobId

Protected. User only. Exports the results for a job that belongs to the logged-in user.
Supports downloading the data as CSV, Excel, or JSON.

**Path Params:**

```json
{ "jobId": "string" }
```

**Query Params:**

```json
{ "format": "csv | excel | json" }
```

**Success Response (200):**
Returns a file download with one of the following content types:

- `text/csv` for `format=csv`
- `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` for `format=excel`
- `application/json` for `format=json`

**Error Responses:**

- `401` - `{ "success": false, "message": "Unauthorized: No token provided" }`
- `401` - `{ "success": false, "message": "Unauthorized: Invalid token" }`
- `403` - `{ "success": false, "message": "Forbidden: Insufficient role" }`
- `403` - `{ "success": false, "message": "You are not authorized to export this job result" }`
- `404` - `{ "success": false, "message": "Job not found" }`
- `400` - `{ "success": false, "message": "Invalid format. Only csv is supported" }`

## Delete User

### DELETE /users/:id

Protected. Admin only. Deletes a user by ID. Admin users cannot be deleted.

**Path Params:**

```json
{ "id": "string" }
```

**Success Response (200):**

```json
{
  "success": true,
  "message": "User deleted successfully",
  "data": null
}
```

**Error Responses:**

- `401` - `{ "success": false, "message": "Unauthorized: No token provided" }`
- `401` - `{ "success": false, "message": "Unauthorized: Invalid token" }`
- `403` - `{ "success": false, "message": "Forbidden: Insufficient role" }`
- `403` - `{ "success": false, "message": "Cannot delete admin user" }`
- `404` - `{ "success": false, "message": "User not found" }`
