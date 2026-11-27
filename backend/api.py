from fastapi import FastAPI
from pydantic import BaseModel

if __package__:
    from .database import get_gold_metrics
else:
    from database import get_gold_metrics


class RaceMetric(BaseModel):
    session_key: int
    driver_number: int
    valid_laps: int | None
    avg_lap_duration: float | None
    fastest_lap: float | None


app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/v1/race-metrics", response_model=list[RaceMetric])
def race_metrics(session_key: int) -> list[dict]:
    return get_gold_metrics(session_key)
