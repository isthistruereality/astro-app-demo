from http.server import BaseHTTPRequestHandler
import json
import requests
from timezonefinder import TimezoneFinder
from datetime import datetime
from zoneinfo import ZoneInfo
from kerykeion import AstrologicalSubject, KerykeionChartSVG

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        try:
            # Geocode city if provided
            if 'birth_city' in data and data['birth_city']:
                geo_url = f"https://nominatim.openstreetmap.org/search?q={data['birth_city']}&format=json&limit=1"
                geo_resp = requests.get(geo_url, headers={'User-Agent': 'AstroApp/1.0'})
                geo_resp.raise_for_status()
                geo_data = geo_resp.json()
                if geo_data:
                    lat = float(geo_data[0]['lat'])
                    lon = float(geo_data[0]['lon'])
                else:
                    raise ValueError("City not found. Try adding country or more details.")
            else:
                raise ValueError("Birth city required.")

            # Get timezone name from lat/long
            tf = TimezoneFinder()
            tz_name = tf.timezone_at(lng=lon, lat=lat)
            if not tz_name:
                raise ValueError("Timezone not found for location.")

            # Compute offset for birth date (handles DST)
            birth_dt = datetime(data["year"], data["month"], data["date"], data["hours"], data["minutes"])
            tz = ZoneInfo(tz_name)
            offset = birth_dt.astimezone(tz).utcoffset().total_seconds() / 3600

            # Create natal chart
            subject = AstrologicalSubject(
                name="User",
                year=data["year"],
                month=data["month"],
                day=data["date"],
                hour=data["hours"],
                minute=data["minutes"],
                lat=lat,
                lng=lon,
                tz_str=str(offset),
            )

            # Extract planets
            output = []
            for planet in subject.planets_list:
                output.append({
                    "name": planet["name"],
                    "sign": planet["sign"],
                    "degree": planet["position"] % 30,
                    "full_degree": planet["position"],
                    "retrograde": planet["retrograde"],
                })

            result = {
                "output": output,
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())