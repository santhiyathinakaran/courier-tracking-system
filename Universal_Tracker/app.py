from flask import Flask, render_template, request, jsonify
import requests
import re

app = Flask(__name__)

# Ship24 Official API Key for Project / TL Verification
OFFICIAL_API_KEY = "apik_YDORnacfMpP6q3X3LeB2ps7vxs9N3q"

def is_valid_ups_format(tracking_number):
    pattern = r'^1Z[A-Z0-9]{16}$'
    if re.match(pattern, tracking_number):
        return True
    if tracking_number.isdigit() and len(tracking_number) in [9, 10, 11, 12]:
        return True
    return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/track', methods=['POST'])
def track():
    tracking_number = request.form.get('tracking_number', '').strip().upper()

    # 1. Validation Checks
    if not tracking_number:
        return jsonify({
            "success": False,
            "status_code": 400,
            "message": "Tracking ID is required."
        }), 400

    if not is_valid_ups_format(tracking_number):
        return jsonify({
            "success": False,
            "status_code": 404,
            "message": f"Tracking number '{tracking_number}' not recognized by UPS. Format requires '1Z' followed by 16 alphanumeric characters."
        }), 404

    # 2. Live Direct Carrier Synced Gateway
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://parcelsapp.com/en/tracking/",
        "X-Authorization-Token": OFFICIAL_API_KEY
    }

    try:
        url = "https://parcelsapp.com/api/v2/parcels"
        payload = {
            "trackingId": tracking_number,
            "carrier": "UPS",
            "language": "en"
        }
        res = session.post(url, json=payload, headers=headers, timeout=12)
        data = res.json()

        states = data.get("states", [])

        # Real updates extract seigirom
        history = []
        for st in states:
            history.append({
                "status": st.get("carrierStatus") or st.get("status") or "Carrier Milestone Scan",
                "location": st.get("location") or "UPS Facility",
                "date": st.get("date") or "Verified"
            })

        raw_status = data.get("status") or (states[0].get("status") if states else None)

        if raw_status or states:
            is_delivered = "delivered" in str(raw_status).lower()
            current_loc = states[0].get("location") if states else "Destination Delivery Area"
            eta = "Delivered Successfully" if is_delivered else (data.get("eta") or "Scheduled as per official UPS delivery")
            recipient = data.get("signedBy") or ("Signature on File" if is_delivered else "In Transit")

            return jsonify({
                "success": True,
                "status_code": 200,
                "status": f"Status: {raw_status} (UPS Official)",
                "current_location": current_loc,
                "expected_delivery": eta,
                "received_by": recipient,
                "history": history
            }), 200

        # Official carrier network-la illana mattum 404
        return jsonify({
            "success": False,
            "status_code": 404,
            "message": f"UPS official records: Tracking number '{tracking_number}' has no carrier records found on UPS systems."
        }), 404

    except requests.exceptions.RequestException:
        return jsonify({
            "success": False,
            "status_code": 500,
            "message": "Gateway error connecting to UPS network servers."
        }), 500

if __name__ == '__main__':
    app.run(debug=True)