from pathlib import Path
import json
import requests
from transform import load_laps, summarize_laps, filter_valid_laps,save_silver_laps
from database import get_connection, upsert_laps_silver,upsert_race_control_silver,upsert_pit_silver
import psycopg

LAPS_URL = "https://api.openf1.org/v1/laps"
RACE_CONTROL_URL = "https://api.openf1.org/v1/race_control"
PIT_URL = "https://api.openf1.org/v1/pit"

SESSION_KEY = 9165

DRIVERS = {
    55: "Carlos Sainz",
    4: "Lando Norris"
}

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "bronze"
RAW_DIR.mkdir(parents=True, exist_ok=True)

def extract_laps(driver_number: int,session_key: str|int = "latest") -> list[dict]:
    params = {
        "session_key": session_key,
        "driver_number":driver_number
        }

    response = requests.get(LAPS_URL,params=params,timeout=60)

    response.raise_for_status()

    return response.json()

def extract_race_control(session_key: str|int = "latest") -> list[dict]:
    params = {
            "session_key": session_key
            }

    response = requests.get(RACE_CONTROL_URL,params=params,timeout=60)

    response.raise_for_status()

    return response.json()

def extract_pit(session_key: str|int = "latest") -> list[dict]:
    params = {
            "session_key": session_key
            }

    response = requests.get(PIT_URL,params=params,timeout=60)

    response.raise_for_status()

    return response.json()


def save_laps(data_laps: list[dict],driver: int) -> None:
    path = RAW_DIR / f"laps_{driver}.json"
    try: 
        with open(path,"w",encoding="utf-8") as f:
                    json.dump(data_laps,f,indent=2,ensure_ascii=False)
    except OSError as e:
        print(f"Error al manipular el archivo {path.name}: {e}")
        raise 

def save_race_control(data_race_control: list[dict]) -> None:
    path = RAW_DIR / f"race_control_{SESSION_KEY}.json"
    try: 
        with open(path,"w",encoding="utf-8") as f:
                    json.dump(data_race_control,f,indent=2,ensure_ascii=False)
    except OSError as e:
        print(f"Error al manipular el archivo {path.name}: {e}")
        raise 

def save_pit(data_pit: list[dict]) -> None:
    path = RAW_DIR / f"pit_{SESSION_KEY}.json"
    try: 
        with open(path,"w",encoding="utf-8") as f:
                    json.dump(data_pit,f,indent=2,ensure_ascii=False)
    except OSError as e:
        print(f"Error al manipular el archivo {path.name}: {e}")
        raise 

if __name__ == "__main__":

    for driver in DRIVERS.keys():
        response = extract_laps(driver,SESSION_KEY)

        save_laps(response,driver)

        data = load_laps(driver,"bronze")
        
        #print("bronze ", len(data))

        summarize = summarize_laps(data,DRIVERS[driver])

        valid_laps = filter_valid_laps(data)

        save_silver_laps(driver,valid_laps)

        data = load_laps(driver,"silver")

        #print("silver ", len(data))
        
        upsert_laps_silver(data)

    print("----------------")

    data_race_control = extract_race_control(SESSION_KEY)

    save_race_control(data_race_control)

    banderas = [event for event in data_race_control if event["category"] == 'Flag']

    virtual_safety_car = [event for event in data_race_control if event["category"] == 'SafetyCar' and "VIRTUAL" in event["message"]]

    safety_car = [event for event in data_race_control if event["category"] == 'SafetyCar' and "VIRTUAL" not in event["message"]]


    upsert_race_control_silver(data_race_control)

    print("----------------")

    data_pit = extract_pit(SESSION_KEY)

    save_pit(data_pit)

    upsert_pit_silver(data_pit)


