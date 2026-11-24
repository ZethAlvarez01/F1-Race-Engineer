from pathlib import Path
import json
import requests

BASE_URL = "https://api.openf1.org/v1/laps"

SESSION_KEY = 9165

DRIVERS = {
    55: "Carlos Sainz",
    4: "Lando Norris",
    22: "Yuki Tsunoda",
    31: "Esteban Ocon",
    1: "Zeth_Test"
}

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "bronze"
RAW_DIR.mkdir(parents=True, exist_ok=True)

def extract_laps(driver_number: int,session_key: str|int = "latest") -> list[dict]:
    params = {
        "session_key": session_key,
        "driver_number":driver_number
        }

    datos = requests.get(BASE_URL,params=params,timeout=60).json()

    return datos

def load_laps(driver_number: int) -> list[dict]:

    with open(RAW_DIR / f"laps_{driver_number}.json","r",encoding="utf-8") as f:
        data = json.load(f)

    return data

if __name__ == "__main__":

    for driver in DRIVERS.keys():
        data = extract_laps(driver,SESSION_KEY)

        if driver != 1: # 1 -> Zeth Test

            with open(RAW_DIR / f"laps_{driver}.json","w",encoding="utf-8") as f:
                json.dump(data,f,indent=2,ensure_ascii=False)

    print("Data guardada")


    for driver in DRIVERS.keys():
        datos = load_laps(driver)

        print("Corredor: ", DRIVERS[driver])
        print("Vueltas registradas: ", len(datos))
        print("Vueltas vacias: ", len([lap for lap in datos if lap["lap_duration"] is None]))
        print("Vueltas validas: ", len([lap for lap in datos if isinstance(lap["lap_duration"],(int,float))
                                        and lap["lap_duration"] > 0]))

        print("")


