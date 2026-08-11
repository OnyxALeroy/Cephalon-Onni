# Development Usage

This file aims at explaining how to setup the environment to allow easy and fluid development.

**Prerequisites:**
- Docker
- Java 21 + Maven (for backend development outside Docker)
- NPM

## Environment description

The whole application uses four different Docker containers:
- `cephalon-onni-redis`:
- `cephalon-onni-postgres`:
- `cephalon-onni-frontend`:
- `cephalon-onni-backend`:

To launch them to explore the application, you can use the following Bash scripts:
- `scripts/start-standalones.sh`: which launches the Redis and PostgreSQL containers ;
- `scripts/start-apps.sh`: which launches the Frontend and Backend containers, performing quick health checks on both ;
- `scripts/start-everything.sh`: which runs the two previous scripts, launching the standalones containers then the Frontend and Backend.

However, those scripts, especially the one for the Frontend and Backend, aren't ideal to launch environment development.

## Launching the application in "dev-mode"

For the two standalone containers, simply use the Bash script. **Ensure they both are running before launching the Backend or the Frontend**.

### Launching everything

To run both Frontend and Backend, run from the project root:
```bash
docker compose up --build
```

The services include:
- **Backend API**: Spring Boot server (port 8080) ;
- **Frontend**: Vue.js application (port 3000, proxying `/api/*` to the backend) ;
- **PostgreSQL**: relational database (port 5432) ;
- **Redis**: worldstate cache (port 6379).

### Frontend

From `./frontend` :

```bash
npm install     # Install dependancies (once per setup)
npm run dev     # Run the Frontend
```

The app will then be available at:

```
http://localhost:5173
```

### Backend

Just run the Backend container.
```bash
docker compose up --build
```

The backend will be available at `http://localhost:8080`.
Once you're done, stop the containers by pressing `Ctrl+C` in the terminal and don't forget to remove them with `docker compose down`.

## DB Setup

The project uses one PostgreSQL database for everything (static catalog data - warframes,
weapons, mods, etc. - and dynamic user data: accounts, builds, inventory). Schema is managed by
Flyway migrations under `backend/src/main/resources/db/migration/`, applied automatically on
backend startup.

**Static catalog seeding is not yet ported to Java** - the JSON-file-based seeder
(`app/database/static/db_init/`) still only exists in `backend-python-legacy/`. See the comment
at the top of `scripts/setup-static-db.sh` for how to run it against a fresh Postgres in the
meantime; run that script to verify catalog tables are populated:

```
./scripts/setup-static-db.sh
```

## Quick Commands (Makefile)

The `Makefile` provides shortcuts for common development tasks:

```bash
make up              # Start all services (same as ./scripts/start-everything.sh)
make down           # Stop all containers
make restart        # Restart all services (rebuilds containers)
make health         # Show status of all running containers
make setup          # Copy .env.example to .env if missing
```

### Logs

```bash
make logs            # Tail all logs
make logs-backend    # Tail backend logs only
make logs-frontend   # Tail frontend logs only
make logs-postgres   # Tail PostgreSQL logs only
make logs-redis      # Tail Redis logs only
```

Or use the script directly:
```bash
./scripts/logs.sh [backend|frontend|postgres|redis|all]
```

### Shell Access

```bash
make shell-backend    # Shell in backend container
make shell-postgres   # PostgreSQL shell (psql)
make shell-redis      # Redis CLI
```

Or use the script directly:
```bash
./scripts/shell.sh [backend|postgres|redis]
```

### Cleanup

```bash
make clean           # Remove containers and unused images
make clean-volumes   # Remove containers, volumes, and images (DESTRUCTIVE)
```

Or use the script directly:
```bash
./scripts/clean.sh [all|volumes]
```

**Warning:** `clean volumes` will delete all database data. You'll need to re-run the DB setup script.
