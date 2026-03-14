# Development Usage

This file aims at explaining how to setup the environment to allow easy and fluid development.

**Prerequisites:**
- Docker
- Python
- NPM

## Environment description

The whole application uses four different Docker containers:
- `cephalon-onni-redis`:
- `cephalon-onni-mongo`: 
- `cephalon-onni-frontend`: 
- `cephalon-onni-backend`:

To launch them to explore the application, you can use the following Bash scripts:
- `scripts/start-standalones.sh`: which launches the Redis and MongoDB containers ;
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
- **Backend API**: FastAPI server (port 8000) ;
- **Frontend**: Vue.js application (port 8080) ;
- **PostgreSQL with Apache AGE**: Graph database (port 5432) ;
- **MongoDB**: Document database (port 27017).

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

The backend will be available at `http://localhost:8000`.
Once you're done, stop the containers by pressing `Ctrl+C` in the terminal and don't forget to remove them with `docker compose down`.

## DB Setup

The project uses one MongoDB database. It stores both static (loot tables, missions, Mod data, etc.) and dynamic (user-based) data, so you might want to initialize it with correct values. Using the script to do so directly on your PC won't work however, due to potential mismatches between authentifications to the DB so run:

```
docker exec -it cephalon-onni-backend python app/db_init_script.py -y
```

**Note:** eventually remove the parameter `-y` if you want to manually handle the setup.

For each run of this script, a logging file is created inside the Docker container, in `var/log/db_init` :
- to list all logs: `docker exec cephalon-onni-backend ls /app/logs/db_init/` ;
- to access it: `docker exec cephalon-onni-backend ls /app/logs/db_init/db_init_<time>.log` ;
- to copy all logs to your local machine: `docker cp cephalon-onni-backend:/app/logs/db_init/* ./db_init_logs/`.
