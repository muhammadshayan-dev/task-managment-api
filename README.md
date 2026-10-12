# Task Management API

A robust, production-ready RESTful API built with **FastAPI**, **SQLAlchemy**, **PostgreSQL**, and **Docker**.

---

## Features
- **Authentication**: JWT-based Authentication (User Registration, Login, Current User profile).
- **Task Management**: Full CRUD operations with task ownership isolation.
- **Search, Filter & Sort**: Query tasks by status, priority, text search, and priority sorting.
- **Database**: PostgreSQL with Alembic migrations and SQLAlchemy ORM.
- **Testing**: Automated test suite with 'pytest' (42 tests passing; no deprecation warnings).
- **Containerization**: Fully Dockerized with Docker Compose.

---

## Project Structure
```text
Task-Management-API/
├── app/
│   ├── main.py
│   ├── auth_router.py
│   ├── task_router.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   └── ...
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_tasks.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── PHASE_10_TESTING_REPORT.md