# portal

Production-minded boilerplate for a Django + React app with:

- Session-based authentication with CSRF protection
- Email/password registration, verification, login, logout, and password reset
- Google sign-in via Google Identity Services
- Role-based access control (`superadmin`, `admin`, `staff`, `customer`)
- User management, notifications, audit logging, and per-user preferences

## Stack

- Backend: Django 6, Django REST Framework, PostgreSQL
- Frontend: React 19, React Router 7, Vite
- Auth model: Django session cookies + CSRF, not bearer tokens

## Quick Start

### Backend

1. Create `backend/portal/.env` from [backend/portal/.env.example](D:/Projects/Basecode%20(Boilerplate)/backend/portal/.env.example)
2. Set PostgreSQL values for `DB_NAME` and `DB_USER`
3. Install dependencies from [backend/portal/requirements.txt](D:/Projects/Basecode%20(Boilerplate)/backend/portal/requirements.txt)
4. Run migrations
5. Start Django from [backend/portal](D:/Projects/Basecode%20(Boilerplate)/backend/portal)

### Frontend

1. Create `frontend/.env` from [frontend/.env.example](D:/Projects/Basecode%20(Boilerplate)/frontend/.env.example)
2. Leave `VITE_API_BASE_URL` empty for local dev so Vite proxies `/api` to Django
3. Install dependencies from [frontend/package.json](D:/Projects/Basecode%20(Boilerplate)/frontend/package.json)
4. Start the Vite dev server from [frontend](D:/Projects/Basecode%20(Boilerplate)/frontend)

## Configuration Notes

- Local development defaults to `DEBUG=true`
- Production should set `DEBUG=false`, real `ALLOWED_HOSTS`, and HTTPS cookie settings
- Repeated wrong-password attempts are rate-limited by `LOGIN_MAX_FAILED_ATTEMPTS` and `LOGIN_LOCKOUT_MINUTES`
- Google login needs only the `GOOGLE_CLIENT_ID` value in env; do not commit downloaded OAuth client-secret JSON files
- The test suite defaults to SQLite so it can run without a local PostgreSQL instance

## Documentation

Architecture, module map, API surface, and workflows:

[docs/Boilerplate.md](D:/Projects/Basecode%20(Boilerplate)/docs/Boilerplate.md)
