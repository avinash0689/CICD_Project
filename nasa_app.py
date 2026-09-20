import os
from datetime import date

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
NASA_URL = "https://science.nasa.gov/wp-json/wp/v2/apod-basic"


@app.route("/", methods=["GET", "POST"])
def home():
    nasa_data = None
    error = None

    if request.method == "POST":
        selected_date = request.form.get("date", "").strip()

        if not selected_date:
            error = "Please enter a date."
        else:
            params = {
                "date": selected_date,
                "api_key": API_KEY,
            }

            try:
                response = requests.get(
                    NASA_URL,
                    params=params,
                    timeout=10,
                )

                if response.status_code == 200:
                    data = response.json()

                    if isinstance(data, list):
                        data = data[0] if data else {}

                    if not data:
                        error = "No APOD data found for the selected date."
                    else:
                        nasa_data = {
                            "title": data.get("title"),
                            "date": data.get("date"),
                            "explanation": data.get("explanation"),
                            "url": data.get("url"),
                            "hdurl": data.get("hdurl"),
                            "media_type": data.get("media_type"),
                            "copyright": data.get("copyright"),
                            "credit": data.get("credit"),
                            "permalink": data.get("permalink"),
                            "alt": data.get("alt"),
                        }
                elif response.status_code == 404:
                    error = "APOD image not found for that date."
                else:
                    error = f"NASA API error: {response.status_code}"

            except requests.RequestException as e:
                error = f"Could not connect to NASA service: {e}"

    if nasa_data is None and request.method == "GET":
        default_date = date.today().strftime("%Y-%m-%d")
        try:
            response = requests.get(
                NASA_URL,
                params={"date": default_date, "api_key": API_KEY},
                timeout=10,
            )
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    nasa_data = {
                        "title": data.get("title"),
                        "date": data.get("date"),
                        "explanation": data.get("explanation"),
                        "url": data.get("url"),
                        "hdurl": data.get("hdurl"),
                        "media_type": data.get("media_type"),
                        "copyright": data.get("copyright"),
                        "credit": data.get("credit"),
                        "permalink": data.get("permalink"),
                        "alt": data.get("alt"),
                    }
        except requests.RequestException:
            pass

    return render_template(
        "index.html",
        nasa_data=nasa_data,
        error=error,
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
    )