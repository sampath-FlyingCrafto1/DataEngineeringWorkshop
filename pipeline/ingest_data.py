#!/usr/bin/env python
# coding: utf-8

import os
import click
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--data-dir', default='./data', help='Directory containing CSV files')
@click.option('--chunksize', default=100000, type=int, help='Chunk size for reading CSV')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, data_dir, chunksize):
    """Ingest CSV files from a directory into PostgreSQL database."""
    # Using the standard postgresql driver (psycopg2)
    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    if not os.path.exists(data_dir):
        print(f"Directory {data_dir} does not exist.")
        return

    csv_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.csv')])

    if not csv_files:
        print(f"No CSV files found in {data_dir}")
        return

    for csv_file in csv_files:
        file_path = os.path.join(data_dir, csv_file)
        table_name = os.path.splitext(csv_file)[0]

        print(f"Ingesting {csv_file} into table {table_name}...")

        try:
            df_iter = pd.read_csv(file_path, iterator=True, chunksize=chunksize)

            first = True
            for df_chunk in tqdm(df_iter, desc=f"Processing {csv_file}"):
                if first:
                    # Drop table if exists and create new one with schema
                    df_chunk.head(0).to_sql(name=table_name, con=engine, if_exists='replace', index=False)
                    first = False

                df_chunk.to_sql(name=table_name, con=engine, if_exists='append', index=False)

            print(f"Successfully ingested {csv_file} into {table_name}")
        except Exception as e:
            print(f"Error ingesting {csv_file}: {e}")

if __name__ == '__main__':
    run()
