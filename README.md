# GossipGuard Rate Limiter

A FastAPI-based distributed rate limiting project with gossip sync, JWT authentication, and role-based permissions.

## Overview

This project demonstrates how to combine:

- JWT + OAuth2 password authentication
- role-based authorization with permissions
- distributed rate limiting with gossip replication
- HMAC-SHA256 signatures for internal node messages
- in-memory demo users for local development
- a small test suite for auth, permissions, and repository behavior

## Features

- Permission-based access control using roles and permissions
- Token-based login and `/auth/me` user lookup
- Middleware-driven request rate limiting
- Gossip synchronization across multiple nodes
- TTL cleanup for stale rate-limit records
- Demo users for local development, disabled by default

## Project Structure

```text
app/
	api/routes/        API endpoints
	core/              settings, auth helpers, security dependencies
	middleware/        rate-limiting middleware
	models/            user and enum definitions
	repositories/      auth and rate-limit storage
	services/          business logic
	server_b.py        secondary node example
	server_c.py        tertiary node example
frontend/            dashboard UI
tests/               pytest suite
```

## Requirements

- Python 3.11+
- FastAPI
- Uvicorn
- httpx
- pytest for tests

## Quick Start

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -e .
pip install -e .[test]
```

### 3. Create your `.env`

Copy the example file:

```bash
cp .env.example .env
```

Then set the required values:

```env
GOSSIP_SECRET_KEY=your-long-random-gossip-secret
JWT_SECRET_KEY=your-long-random-jwt-secret
NODE_ID=node-1
PEER_URLS=http://127.0.0.1:8001,http://127.0.0.1:8002
```

## Configuration

| Variable | Purpose | Required |
| --- | --- | --- |
| `GOSSIP_SECRET_KEY` | Signs internal gossip payloads | Yes |
| `JWT_SECRET_KEY` | Signs JWT access tokens | Yes |
| `NODE_ID` | Unique node identifier | No |
| `PEER_URLS` | Comma-separated peer URLs | No |
| `ENABLE_DEMO_USERS` | Enables seeded demo accounts | No |
| `ADMIN_PASSWORD` | Demo admin password | Only if demo users are enabled |
| `VIEWER_PASSWORD` | Demo viewer password | Only if demo users are enabled |

## Demo Users

Demo accounts are **disabled by default**. To enable them for local development:

```env
ENABLE_DEMO_USERS=true
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
VIEWER_USERNAME=viewer
VIEWER_PASSWORD=viewer123
```

When enabled, the app seeds the in-memory auth repository with the demo users at startup.

## Running the App

### Single node

```bash
uvicorn app.main:app --reload
```

### Multi-node gossip setup

Run three terminals:

```bash
# Terminal 1
uvicorn app.main:app --reload
```

```bash
# Terminal 2
python app/server_b.py
```

```bash
# Terminal 3
python app/server_c.py
```

Default ports:

- `app.main:app` -> `http://127.0.0.1:8000`
- `server_b.py` -> `http://127.0.0.1:8001`
- `server_c.py` -> `http://127.0.0.1:8002`

## Testing

This repository includes tests for:

- permission checks and auth routes
- JWT login and `/auth/me`
- internal gossip access control
- repository merge and expiry behavior
- peer IP verification logic

Run the full suite with:

```bash
pytest
```

Or run the focused tests:

```bash
pytest tests/test_permissions_and_routes.py
pytest tests/test_rate_limit_repository.py
```

## Example API Flow

1. Log in with `POST /auth/token`
2. Copy the returned `access_token`
3. Use `Authorization: Bearer <token>` for protected endpoints
4. Visit `/auth/me` to confirm the active user

