# Data Ingestion Pipeline

This project contains a production-ready data ingestion pipeline that loads CSV files into a PostgreSQL database and includes pgAdmin4 for database management.

## Setup and Deployment

### 1. Spin up the environment

Navigate to the `pipeline` directory and run:

```bash
docker compose up -d --build
```

This will start three services:
- `pgdatabase`: PostgreSQL 18 database.
- `pgadmin`: pgAdmin4 web interface for managing the database.
- `ingestor`: Python script that automatically ingests all CSV files in the `./data` directory into PostgreSQL.

### 2. Connect pgAdmin4 to Postgres

1. Open your browser and go to [http://localhost:8080](http://localhost:8080).
2. Login with:
   - **Email**: `admin@admin.com`
   - **Password**: `root`
3. Add a new server:
   - **Name**: `Local Postgres`
   - **Connection Tab**:
     - **Host name/address**: `pgdatabase` (this is the container name)
     - **Port**: `5432`
     - **Maintenance database**: `ny_taxi`
     - **Username**: `root`
     - **Password**: `root`

### 3. Verify Data Ingestion

The `ingestor` service automatically scans the `./data` folder and creates a table for each CSV file (named after the file).

To check the progress, view the logs:
```bash
docker compose logs ingestor
```

In pgAdmin, you should see the tables under `Servers` > `Local Postgres` > `Databases` > `ny_taxi` > `Schemas` > `public` > `Tables`.

## Dynamic Ingestion

To ingest new data, simply place your CSV files in the `pipeline/data` directory and restart the ingestor:
```bash
docker compose restart ingestor
```
Each file `filename.csv` will be ingested into a table named `filename`.
