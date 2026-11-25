from pathlib import Path
import json


DIR = Path(__file__).resolve().parents[1] / "data" 


def load_laps(driver_number: int,environment: str) -> list[dict]:
    try:
        with open(DIR / environment / f"laps_{driver_number}.json","r",encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError,json.JSONDecodeError):
        print(f"No se pudo cargar el archivo laps_{driver_number}.json")
        return []


def summarize_laps(data_laps: list[dict],driver: str) -> dict:
    return {
         "driver": driver,
         "total_laps": len(data_laps),
         "empty": [lap for lap in data_laps if lap["lap_duration"] is None],
         "valid": filter_valid_laps(data_laps)
    }

def filter_valid_laps(data_laps: list[dict]) -> list[dict]:
        return [lap for lap in data_laps if isinstance(lap["lap_duration"],(int,float))
                and lap["lap_duration"] > 0]


def save_silver_laps(driver: int,data_laps: list[dict]) -> None:

    DIR = Path(__file__).resolve().parents[1] / "data" / "silver"
    DIR.mkdir(parents=True, exist_ok=True)

    path = DIR / f"laps_{driver}.json"

    try: 
        with open(path,"w",encoding="utf-8") as f:
                    json.dump(data_laps,f,indent=2,ensure_ascii=False)
    except OSError as e:
         raise f"Error al manipular el archivo {path.name}: {e}"