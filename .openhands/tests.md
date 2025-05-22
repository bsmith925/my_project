# .openhands/tests.md
## Purpose
Establish consistent, discoverable, and maintainable tests across all OpenHands projects.

## 1 – Directory & file layout
```
project_root/
├── app/                 # application code
│   └── utils/
│       └── file_ops.py
└── tests/               # *mirror* app/ layout
    └── utils/
        └── test_file_ops.py   # mirrors file_ops.py
```
* Put every test module in **`tests/`** and mirror the package path of the code‑under‑test.  
* Name files `test_<module>.py` (or `<module>_test.py`) so `pytest` can auto‑discover them.

## 2 – Test naming conventions
* **Function names** start with `test_…`.
* **Class names** start with `Test` and group related behaviours.
* Spell out the behaviour in the name:  
  `test_read_item_returns_200()` > `test_read_item()`.

## 3 – Arrange‑Act‑Assert (AAA)
1. **Arrange** – set inputs, fixtures, or mocks.  
2. **Act** – execute exactly *one* behaviour.  
3. **Assert** – check *one* expectation.

## 4 – FastAPI integration
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
```
Call regular (non‑async) methods on the client inside your tests.

## 5 – Fixtures & factories
* Prefer `pytest` fixtures for database or session setup.
* Generate example objects with factory libraries (e.g., `factory_boy`).

## 6 – Isolation
* Never hit real external services; mock with `unittest.mock`, `responses`, or lightweight HTTP servers.
* Provide a test‑specific settings profile (e.g., `settings.TESTING=True`) to disable background jobs & email.

## 7 – CI hints
* Run `pytest --exitfirst --failed-first -q` locally for quick feedback.
* Fail the build if code‑coverage is below **80 %** (adjust in `pyproject.toml`).
