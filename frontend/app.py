import streamlit as st
import requests

API_URL = "http://127.0.0.1:5000"

st.set_page_config(
    page_title="Farmer Weather Assistant",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Farmer Weather Assistant")
st.write("Weather information and farming guidance through a REST API.")

st.divider()

# Location input
location = st.text_input(
    "📍 Enter your location",
    placeholder="Example: Pune"
)

# Crop selection
crop = st.selectbox(
    "🌱 Select your crop",
    ["Wheat", "Rice", "Cotton", "Sugarcane"]
)

st.write("Selected crop:", crop)

# Button
if st.button("🌤️ Get Weather", use_container_width=True):

    if not location:
        st.warning("Please enter your location.")
        st.stop()

    try:
        # Current Weather
        response = requests.get(
            f"{API_URL}/api/weather/{location}",
            timeout=10
        )

        if response.status_code != 200:
            st.error("Unable to get weather information.")
            st.stop()

        data = response.json()
        weather = data["weather"]

        st.divider()
        st.header(f"🌤️ Current Weather — {data['location']}")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "🌡️ Temperature",
                f"{weather.get('temperature_2m')} °C"
            )

        with col2:
            st.metric(
                "💧 Humidity",
                f"{weather.get('relative_humidity_2m')} %"
            )

        with col3:
            st.metric(
                "💨 Wind Speed",
                f"{weather.get('wind_speed_10m')} km/h"
            )

        with col4:
            st.metric(
                "🌧️ Rainfall",
                f"{weather.get('precipitation')} mm"
            )

        # 7-Day Forecast
        st.divider()
        st.header("📅 7-Day Forecast")

        forecast_response = requests.get(
            f"{API_URL}/api/forecast/{location}",
            timeout=10
        )

        if forecast_response.status_code == 200:

            forecast = forecast_response.json()["forecast"]

            dates = forecast["time"]
            max_temp = forecast["temperature_2m_max"]
            min_temp = forecast["temperature_2m_min"]
            rain_probability = forecast["precipitation_probability_max"]
            rain_amount = forecast["precipitation_sum"]

            for i in range(len(dates)):
                st.write(
                    f"**📅 {dates[i]}** | "
                    f"Max: **{max_temp[i]} °C** | "
                    f"Min: **{min_temp[i]} °C** | "
                    f"Rain Probability: **{rain_probability[i]}%** | "
                    f"Rainfall: **{rain_amount[i]} mm**"
                )

        # Crop Advisory
        st.divider()
        st.header(f"🌾 {crop} Crop Advisory")

        advisory_response = requests.get(
            f"{API_URL}/api/advisory/{crop.lower()}",
            timeout=10
        )

        if advisory_response.status_code == 200:

            advisory = advisory_response.json()["advisory"]

            st.info(
                f"💧 **Irrigation:** {advisory['irrigation']}"
            )

            st.info(
                f"🌧️ **Rain Advice:** {advisory['rain_advice']}"
            )

            st.info(
                f"🌡️ **Temperature:** {advisory['temperature']}"
            )

            st.success(
                f"🌱 **Recommendation:** {advisory['recommendation']}"
            )

        # Weather Alerts
        st.divider()
        st.header("⚠️ Weather Alerts")

        alert_response = requests.get(
            f"{API_URL}/api/alerts/{location}",
            timeout=10
        )

        if alert_response.status_code == 200:

            alerts = alert_response.json()["alerts"]

            for alert in alerts:

                if alert["severity"] == "High":
                    st.error(
                        f"🚨 **{alert['type']}**\n\n"
                        f"{alert['message']}"
                    )

                elif alert["severity"] == "Medium":
                    st.warning(
                        f"⚠️ **{alert['type']}**\n\n"
                        f"{alert['message']}"
                    )

                else:
                    st.success(
                        f"✅ **{alert['type']}**\n\n"
                        f"{alert['message']}"
                    )

    except requests.exceptions.RequestException:
        st.error(
            "❌ Cannot connect to the Flask API. "
            "Make sure the backend is running."
        )

    except Exception as e:
        st.error(f"❌ Error: {e}")