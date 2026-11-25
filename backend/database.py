import psycopg
import os
from pathlib import Path
from dotenv import load_dotenv


ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)

sql_upsert = """
    INSERT INTO laps (session_key, driver_number, lap_number, lap_duration)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (session_key, driver_number, lap_number)
    DO UPDATE SET lap_duration = EXCLUDED.lap_duration;
"""

def get_connection():
    return psycopg.connect(dbname=os.getenv("POSTGRESQL_DBNAME"), user=os.getenv("POSTGRESQL_USER"), password=os.getenv("POSTGRESQL_PASS"), host=os.getenv("POSTGRESQL_HOST"), port=os.getenv("POSTGRESQL_PORT"))


def upsert_laps_silver(data_laps: list[dict]) -> None:

    conn = get_connection()

    values = [(lap["session_key"],lap["driver_number"],lap["lap_number"],lap["lap_duration"]) for lap in data_laps]

    with conn.cursor() as cur:
        cur.executemany(sql_upsert, values)

    conn.commit()