import os
import time

import requests
from dotenv import load_dotenv


def load_config():
    load_dotenv()
    station_ids = os.getenv("STATION_IDS")

    if not station_ids:
        raise ValueError("Missing STATION_IDS in .env")
    station_id = [sid.strip() for sid in station_ids.split(",") if sid.strip()]
    return station_id

def request_response():
    station_numbers = load_config()
    stations = []
    for station_number in station_numbers:
        try:
            response = requests.get(
                f"https://maps.mo-bi.ro/api/nextArrivals/{station_number}"
            )
            response.raise_for_status()
            data = response.json()
            stations.append(data)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching station {station_number}: {e}")

    return stations

def main():
    stations_data = request_response()
    station_name = stations_data[0].get("name", "")
    print(f"Statia: {station_name}")

    for station in stations_data:
            lines = station.get("lines", [])

            for line in lines:
                vehicle = line.get("name", "")
                arrival = line.get("arrivingTime", "N/A")
                direction = line.get("directionName", "")

                if arrival != "N/A":
                    minutes = int(arrival) // 60
                    print(f"  {vehicle} → {direction}: {minutes} min")
                else:
                    print(f"  {vehicle} → {direction}: no time available")


if __name__ == "__main__":
    main()
    time.sleep(10)
