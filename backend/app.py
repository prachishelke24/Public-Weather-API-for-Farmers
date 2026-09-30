from flask import Flask, jsonify
from flask_caching import Cache
import requests

app = Flask(__name__)
cache = Cache(app, config={
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
})

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
@cache.cached()
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

@app.route("/api/forecast/<location>")
def forecast(location):
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

        # Step 2: Get 7-day weather forecast
        forecast_url = "https://api.open-meteo.com/v1/forecast"

        forecast_params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": (
                "temperature_2m_max,"
                "temperature_2m_min,"
                "precipitation_probability_max,"
                "precipitation_sum,"
                "weather_code"
            ),
            "forecast_days": 7,
            "timezone": "auto"
        }

        forecast_response = requests.get(
            forecast_url,
            params=forecast_params,
            timeout=10
        )

        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        # Step 3: Return clean REST API response
        return jsonify({
            "location": place.get("name"),
            "country": place.get("country"),
            "latitude": latitude,
            "longitude": longitude,
            "forecast": forecast_data.get("daily", {})
        })

    except requests.exceptions.RequestException:
        return jsonify({
            "error": "Weather service is currently unavailable"
        }), 503

    except Exception:
        return jsonify({
            "error": "An unexpected error occurred"
        }), 500

@app.route("/api/advisory/<crop>")
def advisory(crop):
    crop = crop.lower()

    advisories = {
        "wheat": {
            "crop": "Wheat",
            "irrigation": "Provide regular irrigation during the growing period.",
            "rain_advice": "Avoid excessive irrigation during periods of heavy rainfall.",
            "temperature": "Suitable temperature is approximately 15°C to 25°C.",
            "recommendation": "Monitor soil moisture and protect the crop from waterlogging."
        },

        "rice": {
            "crop": "Rice",
            "irrigation": "Maintain adequate water in the field during the growing stage.",
            "rain_advice": "Ensure proper drainage during excessive rainfall.",
            "temperature": "Suitable temperature is approximately 20°C to 35°C.",
            "recommendation": "Monitor water levels and check regularly for pests and diseases."
        },

        "cotton": {
            "crop": "Cotton",
            "irrigation": "Provide irrigation when soil moisture becomes low.",
            "rain_advice": "Avoid waterlogging and ensure proper drainage.",
            "temperature": "Suitable temperature is approximately 21°C to 30°C.",
            "recommendation": "Monitor soil moisture and regularly inspect plants for pests."
        },

        "sugarcane": {
            "crop": "Sugarcane",
            "irrigation": "Provide regular irrigation, especially during dry periods.",
            "rain_advice": "Ensure proper drainage during heavy rainfall.",
            "temperature": "Suitable temperature is approximately 20°C to 35°C.",
            "recommendation": "Maintain soil moisture and monitor the crop for pests."
        }
    }

    if crop not in advisories:
        return jsonify({
            "error": "Crop advisory not available",
            "crop": crop,
            "available_crops": list(advisories.keys())
        }), 404

    return jsonify({
        "status": "success",
        "advisory": advisories[crop]
    })

@app.route("/api/alerts/<location>")
def alerts(location):
    try:
        # Step 1: Find latitude and longitude
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

        # Step 2: Get current weather data
        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "precipitation,"
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

        current = weather_data.get("current", {})

        temperature = current.get("temperature_2m")
        precipitation = current.get("precipitation")
        wind_speed = current.get("wind_speed_10m")

        alerts_list = []

        # Heavy rain alert
        if precipitation is not None and precipitation >= 10:
            alerts_list.append({
                "type": "Heavy Rain",
                "severity": "High",
                "message": "Heavy rainfall detected. Avoid unnecessary field operations."
            })

        # High temperature alert
        if temperature is not None and temperature >= 35:
            alerts_list.append({
                "type": "High Temperature",
                "severity": "Medium",
                "message": "High temperature detected. Monitor crop water requirements."
            })

        # Strong wind alert
        if wind_speed is not None and wind_speed >= 40:
            alerts_list.append({
                "type": "Strong Wind",
                "severity": "High",
                "message": "Strong winds detected. Protect crops and check vulnerable structures."
            })

        if not alerts_list:
            alerts_list.append({
                "type": "No Major Alert",
                "severity": "Low",
                "message": "No major weather alerts detected at this time."
            })

        return jsonify({
            "location": place.get("name"),
            "country": place.get("country"),
            "alerts": alerts_list,
            "current_weather": current
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