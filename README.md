# Interview IQ Backend — Phase 1 + Phase 2 (Merged)

Production-oriented FastAPI backend for the Interview IQ AI mock-interview and
career-guidance platform. This package is the result of merging your two
uploaded phases into a single, non-duplicated, working codebase running on
**MySQL**.

## How the merge was done

Phase 2 turned out to be an architectural evolution of Phase 1 (split model
files, enum-backed columns, a proper service layer, rotating refresh tokens,
richer validation) rather than a separate, competing implementation — every
route Phase 1 had, Phase 2 already had a more complete version of. So instead
of splicing two trees together file-by-file, this package uses Phase 2 as the
base and folds back in the pieces Phase 1 had that Phase 2 had dropped or left
unfinished. Concretely, on top of the Phase 2 code, this merge:

- **Fixed a SQLite `connect_args` regression** in `app/database.py` that would
  make the pytest suite crash with "SQLite objects created in a thread can
  only be used in that same thread" (Phase 1 had this fix; Phase 2 lost it).
- **Removed 8 dead files** (`app/api/routes/admin_users.py`,
  `admin_questions.py`, `admin_reports.py`, `admin_resources.py`,
  `admin_roles.py`, `admin_settings.py`, `admin_subscriptions.py`,
  `admin_analytics.py`) — each was just `from app.api.routes.admin import
  router`, added zero endpoints, and wasn't even wired into `api_router`.
- **Implemented real logic for 7 routes that Phase 2 had left as empty
  stubs** (`return ok([])` with no DB access), which were regressions vs. the
  working Phase 1 equivalents:
  - `notifications.py` — list, unread count, mark read / mark all read, delete
  - `support.py` — create ticket, list tickets, ticket detail + messages, reply
  - `roadmaps.py` — generate a roadmap from a career skill-gap analysis, list,
    detail, mark items complete (with rolling roadmap progress %)
  - `skills.py` — list skills, view/update your own skill proficiencies
  - `achievements.py` — list achievements with earned/unearned status
  - `resources.py` — list learning resources, mark complete, bookmark
  - `billing.py` — list your billing records
- **Added the matching request schemas** for the above
  (`app/schemas/support.py`, `skill.py`, `roadmap.py` were empty placeholders).
- **Added seed data** for learning resources and achievements so the new
  endpoints return real demo data out of the box.
- **Hand-authored the initial Alembic migration**
  (`alembic/versions/0001_initial_schema.py`) covering all 34 tables — neither
  original zip contained any migration files, only an empty `versions/`
  folder.
- **Wrote/expanded tests** for every route above plus careers, interviews,
  resumes, admin, progress, and subscriptions, which were previously 2-line
  placeholders (`app/tests/test_*.py`).
- Verified with static analysis that every internal import in the project
  resolves correctly and every file compiles cleanly (see *Verification*
  below for exactly what that does and doesn't guarantee).

Nothing from either phase was deleted except the 8 genuinely empty stub
files above — every model, service, and endpoint from both zips is present.

## Database: MySQL (this is the default — not SQLite)

`DATABASE_URL` in `.env.example` points at MySQL
(`mysql+pymysql://root:password@localhost:3306/interview_iq`), and that's
what the app, Alembic, and Docker Compose all use. The **only** place SQLite
appears is `app/tests/conftest.py`, which hardcodes a local SQLite file so the
pytest suite runs fast and never touches your real database. Running the
actual server always goes through whatever `DATABASE_URL` you set in `.env`.

## Setup (MySQL)

```powershell
cd Backend
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Create the database:
```sql
CREATE DATABASE interview_iq CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE interview_iq_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Edit `.env` with your real MySQL credentials, then run the migration that
ships with this package (see note above — it was hand-written since no live
DB was available to autogenerate it; treat it as a first cut and diff it
against your actual MySQL server before trusting it in production):

```powershell
alembic upgrade head
python -m app.seed.seed_all
python -m uvicorn app.main:app --reload
```

If you ever change a model afterwards, generate a **follow-up** migration
rather than editing `0001_initial_schema.py`:
```powershell
alembic revision --autogenerate -m "sync models"
alembic upgrade head
```

Swagger: `http://127.0.0.1:8000/docs`
ReDoc: `http://127.0.0.1:8000/redoc`

## Docker (MySQL included)
```powershell
docker compose up --build
```
This starts a MySQL 8.4 container, waits for its healthcheck, runs
`alembic upgrade head`, then starts the API — no local MySQL install needed.

## API surface (by module)

| Module | Base path | Notes |
|---|---|---|
| Auth | `/api/auth` | register, login, refresh (rotating + reuse detection), logout, logout-all, verify/reset/change password |
| Users | `/api/users/me` | profile, onboarding, profile image upload, account deletion |
| Careers | `/api/careers` | roles, match generation, skill-gap analysis |
| Resumes | `/api/resumes` | upload (PDF/DOCX, signature-checked), analyze, list, download, delete |
| Interviews | `/api/interviews` | create, start, current question, submit text answer, complete, cancel, status |
| Reports | `/api/reports` | interview report retrieval |
| Progress | `/api/progress` | dashboard/summary metrics |
| Roadmaps | `/api/roadmaps` | generate, list, detail, complete item |
| Resources | `/api/resources` | list, complete, bookmark |
| Skills | `/api/skills` | list, view/update your proficiencies |
| Achievements | `/api/achievements` | list with earned status |
| Notifications | `/api/notifications` | list, unread count, mark read/all, delete |
| Billing | `/api/billing` | list your billing records |
| Support | `/api/support` | create/list tickets, ticket detail, reply |
| Subscriptions | `/api/subscriptions` | plans, current, usage, demo upgrade |
| Jobs | `/api/jobs` | async processing job status polling |
| Admin | `/api/admin` | dashboard, users, question bank (requires ADMIN role) |

All responses use a `{success, message, data}` envelope; errors use
`{success:false, error:{code, message, details}}`.

## Frontend integration
```env
VITE_API_BASE_URL=http://localhost:8000/api
```
Send access tokens as `Authorization: Bearer <access_token>`.

## Scoring transparency
Resume ATS readiness weights: required skills 30%, role keywords 20%, section
completeness 15%, experience relevance 15%, formatting 10%, education 5%,
achievements/action verbs 5%. This is explicitly advisory, not a reproduction
of any employer's real ATS.

Interview evaluation prioritizes answer content; behavioral evaluation adds
STAR completeness. Protected characteristics are never scored.

## Tests
```powershell
pytest -q
pytest --cov=app
ruff check app
mypy app --ignore-missing-imports
```
The suite runs against an isolated SQLite file (see the database note above)
so it never touches your MySQL data, and each test gets a clean schema via
the `db_reset` fixture in `conftest.py`.

## Verification performed on this package

This sandbox had no network access and no FastAPI/SQLAlchemy installed, so it
was not possible to actually boot the server or run `pytest`/`alembic`
against a live MySQL instance. What **was** verified:

- Every `.py` file compiles (`python -m py_compile`) — no syntax errors.
- A custom AST-based checker confirmed every internal `app.*` import resolves
  to a real module, and every name imported from an internal module actually
  exists there (function/class/constant-level check, not just file-level).
- `requirements.txt` was cross-checked against every third-party import
  actually used in the code.
- All new/rewritten routes were checked line-by-line against their models and
  against the pattern used by the surrounding (already-working) Phase 2 code.

**Before you deploy this**, please run `pytest -q` and `alembic upgrade head`
yourself against a real MySQL instance — that's the one thing this
environment couldn't do for you, and it's the standard, expected final check
for any backend package.

## Production notes
Use a strong `SECRET_KEY`, a non-root MySQL account, a TLS reverse proxy, a
real SMTP provider, object storage for uploads, Redis/Celery for long-running
jobs, malware scanning for uploads, and managed secret storage. Always run
Alembic migrations before each release.
