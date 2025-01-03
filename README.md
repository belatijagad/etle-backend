# Setup
## 1. Create virtual environment
```bash
py -m venv .venv
```

## 2. Activate virtual environment
```bash
# Windows
.venv/scripts/activate

# MacOS/Linux
source .venv/bin/activate
```

## 3. Install requirements
```bash
pip install -r requirements.txt
```

## 4. Create `.env` file on project root
Minimum content for the .env
```bash
DB_TYPE=sqlite  # Change to "postgres" for PostgreSQL
# SQLite settings
SQLITE_DB_FILE=sql_app.db
# PostgreSQL settings
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=db

ROBOFLOW_API_KEY=INSERT_API_KEY_HERE
BASE_URL=BACKEND_URL
```

## 5. Run the server
```bash
# Development mode
fastapi dev

# Deployment
fastapi run --workers <insert number of workers> app/main.py
```

## Extras:
In case of needing to reset the database and directory, run this script:
```bash
py scripts/cleanup.py
```
It will clear the content within `cropped_images`, `images`, and `sql_app.db`.

## TODO
- [] Migrate database from sqlite to postgres on deployment