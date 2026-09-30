from flask import Flask, jsonify
import requests

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "message": "Public Weather API for Farmers",
        "status": "running"
    })


@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "Farmer Weather REST API"
    })


@app.route("/api/weather/<location>")
def weather(location):
    try:
        # Step 1: Find latitude and longitude of the location
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"

        geo_params = {
            "name": location,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        geo_response = requests.get(
            geo_url,
            params=geo_params,
            timeout=10
        )

        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if "results" not in geo_data or not geo_data["results"]:
            return jsonify({
                "error": "Location not found",
                "location": location
            }), 404

        place = geo_data["results"][0]

        latitude = place["latitude"]
        longitude = place["longitude"]

        # Step 2: Get current weather
        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "precipitation,"
                "weather_code,"
                "wind_speed_10m"
            ),
            "timezone": "auto"
        }

        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10
        )

        weather_response.raise_for_status()
        weather_data = weather_response.json()

        # Step 3: Return a clean REST API response
        return jsonify({
            "location": place.get("name"),
            "country": place.get("country"),
            "latitude": latitude,
            "longitude": longitude,
            "weather": weather_data.get("current", {})
        })

    except requests.exceptions.RequestException:
        return jsonify({
            "error": "Weather service is currently unavailable"
        }), 503

    except Exception:
        return jsonify({
            "error": "An unexpected error occurred"
        }), 500


if __name__ == "__main__":
    app.run(debug=True)