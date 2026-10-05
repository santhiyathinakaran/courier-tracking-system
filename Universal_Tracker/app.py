import base64
import os
import time

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()  # loads credentials from the .env file

app = Flask(__name__)

# UPS API credentials are read from environment variables (.env file)
UPS_CLIENT_ID = os.getenv("UPS_CLIENT_ID")
UPS_CLIENT_SECRET = os.getenv("UPS_CLIENT_SECRET")

# Production endpoints (for the sandbox, replace "onlinetools" with "wwwcie")
TOKEN_URL = "https://onlinetools.ups.com/security/v1/oauth/token"
TRACK_URL = "https://onlinetools.ups.com/api/track/v1/details/"

token_cache = {
    "access_token": None,
    "expires_at": 0
}


def get_ups_token():
    """Fetch a Bearer token using the OAuth 2.0 Client Credentials flow."""
    now = time.time()
    if token_cache["access_token"] and now < token_cache["expires_at"]:
        return token_cache["access_token"], 200

    if not UPS_CLIENT_ID or not UPS_CLIENT_SECRET:
        return None, 500

    creds = f"{UPS_CLIENT_ID}:{UPS_CLIENT_SECRET}"
    encoded = base64.b64encode(creds.encode()).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded}"
    }
    payload = {"grant_type": "client_credentials"}

    try:
        res = requests.post(TOKEN_URL, headers=headers, data=payload, timeout=10)
        if res.status_code == 200:
            data = res.json()
            token_cache["access_token"] = data.get("access_token")
            token_cache["expires_at"] = now + int(data.get("expires_in", 3600)) - 300
            return token_cache["access_token"], 200
        return None, res.status_code
    except requests.exceptions.RequestException:
        return None, 500


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/track", methods=["POST"])
def track():
    tracking_number = request.form.get("tracking_number", "").strip()

    if not tracking_number:
        return jsonify({"success": False, "status_code": 400, "message": "Tracking number is required."}), 400

    token, token_status = get_ups_token()
    if not token:
        return jsonify({
            "success": False,
            "status_code": token_status,
            "message": f"Authentication failed (HTTP {token_status}). Verify UPS credentials."
        }), token_status

    headers = {
        "Authorization": f"Bearer {token}",
        "transId": f"track_{int(time.time())}",
        "transactionSrc": "UPS_Live_Tracker"
    }

    try:
        res = requests.get(f"{TRACK_URL}{tracking_number}", headers=headers, timeout=12)
        status_code = res.status_code

        if status_code == 200:
            data = res.json()
            shipment = data.get("trackResponse", {}).get("shipment", [{}])[0]
            package = shipment.get("package", [{}])[0]

            current_status = package.get("currentStatus", {}).get("description", "In Transit")

            # Delivery date parsing
            delivery_date = package.get("deliveryDate", [{}])[0].get("date", "")
            delivery_time = package.get("deliveryTime", {}).get("endTime", "")
            expected_delivery = f"{delivery_date} {delivery_time}".strip() or "Standard Transit Schedule"

            activity_raw = package.get("activity", [])
            history = []
            current_location = "UPS Facility"

            for i, act in enumerate(activity_raw):
                city = act.get("location", {}).get("address", {}).get("city", "")
                country = act.get("location", {}).get("address", {}).get("countryCode", "")
                loc_str = f"{city}, {country}".strip(", ") or "In Transit"
                if i == 0 and loc_str:
                    current_location = loc_str

                history.append({
                    "date": f"{act.get('date', '')} {act.get('time', '')}",
                    "status": act.get("status", {}).get("description", "Status Update"),
                    "location": loc_str
                })

            return jsonify({
                "success": True,
                "status_code": 200,
                "status": current_status,
                "current_location": current_location,
                "expected_delivery": expected_delivery,
                "history": history
            }), 200

        elif status_code == 404:
            return jsonify({"success": False, "status_code": 404, "message": "Package not found in UPS database."}), 404
        elif status_code == 429:
            return jsonify({"success": False, "status_code": 429, "message": "UPS API rate limit exceeded."}), 429
        else:
            return jsonify({"success": False, "status_code": status_code, "message": f"UPS API returned status {status_code}"}), status_code

    except requests.exceptions.RequestException:
        return jsonify({"success": False, "status_code": 500, "message": "Failed to reach the UPS API."}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)  # port 5001 to avoid conflicts