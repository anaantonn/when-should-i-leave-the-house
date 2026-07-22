import os
import time

import requests
from dotenv import load_dotenv


def load_config():
    load_dotenv()
    station_ids = os.getenv("STATION_IDS")
    expected_lines = os.getenv("EXPECTED_LINES")

    if not station_ids:
        raise ValueError("Missing STATION_IDS in .env")
    if not expected_lines:
            raise ValueError("Missing EXPECTED_LINES in .env")

    station_ids_list = [
        sid.strip() for sid in station_ids.split(",") if sid.strip()
        ]
    expected_lines_list = [
        line.strip() for line in expected_lines.split(",") if line.strip()
        ]

    return station_ids_list, expected_lines_list

def request_response(station_numbers):
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

def parse_arrival(line):
    name = line.get("name", "?")
    direction = line.get("directionName", "?")
    vehicle_type = line.get("type", "BUS")
    arriving_raw = line.get("arrivingTime", None)
    is_timetable = line.get("isTimetable", True)
    color_hex = line.get("color", "#FFFFFF")

    if arriving_raw is not None:
        minutes = int(arriving_raw) // 60
        arriving_str = f"{minutes} min"
    else:
        arriving_str = "Încă nu."

    try:
        color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
    except (ValueError, IndexError):
        color_rgb = (255, 255, 255)

    return {
        "name": name,
        "direction": direction,
        "type": vehicle_type,
        "color": color_rgb,
        "arriving": arriving_str,
        "is_timetable": is_timetable,
        "suspended": False,
    }

def fetch_all_stations():
    station_numbers, expected_lines = load_config()
    stations_data = request_response(station_numbers)

    merged_stations = {}
    remaining_expected = expected_lines.copy()

    for station in stations_data:
        station_name = station.get("name", "Unknown")
        lines = station.get("lines", [])

        if station_name not in merged_stations:
            merged_stations[station_name] = {"lines": []}

        for line in lines:
            parsed = parse_arrival(line)

            if parsed["name"] in remaining_expected:
                remaining_expected.remove(parsed["name"])

            merged_stations[station_name]["lines"].append(parsed)

    if remaining_expected and merged_stations:
        first_station = next(iter(merged_stations))
        for missing_line in remaining_expected:
            merged_stations[first_station]["lines"].append({
                "name": missing_line,
                "direction": "Nicio informație disponibilă. Verifică InfoTB",
                "type": "UNKNOWN",
                "color": (180, 180, 180),
                "arriving": "N/A",
                "is_timetable": False,
                "suspended": True,
            })

    return merged_stations

if __name__ == "__main__":
    while True:
        data = fetch_all_stations()
        for station_name, station in data.items():
            print(f"\nStația: {station_name}")
            for line in station["lines"]:
                if line["suspended"]:
                    print(f"  {line['name']} → {line['direction']}")
                else:
                    print(f"  {line['name']} → {line['direction']}: {line['arriving']}")
        time.sleep(10)
