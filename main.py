import os
import json
import requests
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    print("Error: API_KEY missing from .env file!")
    exit(1)

BASE_URL = "https://json.freeastrologyapi.com"

def get_western_planets(birth_data):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    payload = {
        "year": birth_data["year"],
        "month": birth_data["month"],
        "date": birth_data["day"],
        "hours": birth_data["hour"],
        "minutes": birth_data["minute"],
        "seconds": 0,
        "latitude": birth_data["lat"],
        "longitude": birth_data["lon"],
        "timezone": birth_data["tz"],
    }

    endpoint = "/western/planets"

    try:
        response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        print("\n=== Raw API Response ===")
        print(json.dumps(data, indent=2))

        print("\n=== Western Natal Positions ===")

        if "output" in data and isinstance(data["output"], list):
            for item in data["output"]:
                planet_name = item.get("planet", {}).get("en", "Unknown")
                full_deg = item.get("fullDegree", 0)
                norm_deg = item.get("normDegree", full_deg % 30)
                sign = item.get("sign", {}).get("en", "Unknown")  # API may return sign
                if sign == "Unknown":  # fallback
                    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
                    sign = signs[int(full_deg // 30) % 12]
                retro = " (Retrograde)" if item.get("isRetro") == "True" else ""

                print(f"{planet_name}: {sign} {norm_deg:.2f}°{retro} (full {full_deg:.2f}°)")

        else:
            print("No 'output' list found. Check raw response above.")

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        if 'response' in locals() and response.text:
            print("Response details:", response.text)

# Interactive input
if __name__ == "__main__":
    print("Western Natal Chart (freeastrologyapi.com /western/planets)")
    print("Using Denver coordinates for now (lat 39.7392, lon -104.9903)")
    print("Timezone: adjust for DST (-6.0 MDT summer, -7.0 MST winter)\n")

    year   = int(input("Birth year (e.g. 1995): "))
    month  = int(input("Month (1-12): "))
    day    = int(input("Day (1-31): "))
    hour   = int(input("Hour (0-23): "))
    minute = int(input("Minute (0-59): "))

    # Denver example
    lat = 39.7392
    lon = -104.9903
    tz  = -7.0   # Change to -6.0 if birth during Daylight Saving Time

    birth = {
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "minute": minute,
        "lat": lat,
        "lon": lon,
        "tz": tz,
    }

    get_western_planets(birth)