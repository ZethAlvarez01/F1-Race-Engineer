import psycopg
import os
from pathlib import Path
from dotenv import load_dotenv
from psycopg.rows import dict_row


ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)

sql_upsert_laps = """
    INSERT INTO laps (session_key, driver_number, lap_number, lap_duration)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (session_key, driver_number, lap_number)
    DO UPDATE SET lap_duration = EXCLUDED.lap_duration;
"""

sql_upsert_race_control = """
    INSERT INTO race_control (
    session_key, date, driver_number, lap_number,
    category, flag, scope, sector, message
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)

ON CONFLICT ON CONSTRAINT race_control_event_uk
DO UPDATE SET
    message = EXCLUDED.message;
"""

sql_upsert_pit = """
    INSERT INTO pits_stop (
    session_key, date, driver_number, lap_number,
    lane_duration, pit_duration, stop_duration
)
VALUES (%s, %s, %s, %s, %s, %s, %s)

ON CONFLICT ON CONSTRAINT pits_stop_pkey
DO UPDATE SET
    pit_duration = EXCLUDED.pit_duration;
"""


def get_connection():
    return psycopg.connect(dbname=os.getenv("POSTGRESQL_DBNAME"), user=os.getenv("POSTGRESQL_USER"), password=os.getenv("POSTGRESQL_PASS"), host=os.getenv("POSTGRESQL_HOST"), port=os.getenv("POSTGRESQL_PORT"))


def upsert_laps_silver(data_laps: list[dict]) -> None:

    conn = get_connection()

    values = [(lap["session_key"],lap["driver_number"],lap["lap_number"],lap["lap_duration"]) for lap in data_laps]

    with conn.cursor() as cur:
        cur.executemany(sql_upsert_laps, values)

    conn.commit()

def upsert_race_control_silver(data_race_control: list[dict]) -> None:

    values = [(
        event["session_key"], event.get("date"), event.get("driver_number"), event.get("lap_number"),
        event.get("category"), event.get("flag"), event.get("scope"), event.get("sector"), event.get("message")
    ) for event in data_race_control]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(sql_upsert_race_control, values)

def upsert_pit_silver(data_pit: list[dict]) -> None:
    values = [(
            event["session_key"], event.get("date"), event.get("driver_number"), event.get("lap_number"),
            event.get("pit_duration"), event.get("lane_duration"), event.get("stop_duration")
        ) for event in data_pit]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(sql_upsert_pit, values)

def run_gold_metrics(session_key: int) -> None:
    if session_key != 9165:
        raise ValueError("El cálculo Gold tiene rangos de Safety Car definidos solo para la sesión 9165")

    ENV_GOLD = Path(__file__).resolve().parent.parent / "sql"

    with open(ENV_GOLD / "driver_race_metric.sql","r",encoding="utf-8") as f:
        query = f.read()

    with get_connection() as conn:
        conn.execute(query)


def get_gold_metrics(session_key: int) -> list[dict]:
    query = """
        SELECT session_key, driver_number, valid_laps, avg_lap_duration, fastest_lap
        FROM public.driver_race_metric
        WHERE session_key = %s
        ORDER BY driver_number
    """

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query, (session_key,))
            return cur.fetchall()
