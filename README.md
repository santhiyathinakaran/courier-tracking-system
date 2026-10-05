# Courier Tracking System

A Flask web application that lets users enter a courier tracking number and view its live shipment status. The app validates the tracking number format, fetches tracking details from the carrier's API and shows them on a clean, responsive page.

## Features

- Tracking number format validation before calling the API
- Real-time shipment status and tracking history
- Simple, responsive web interface (HTML, CSS, JavaScript)
- API credentials kept out of the code using environment variables

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML5, CSS3, JavaScript |
| API | Carrier tracking REST API (via `requests`) |
| Config | python-dotenv (`.env`) |

## Project Structure

```
Courier_Project/
├── Universal_Tracker/
│   ├── app.py            # Flask app and tracking logic
│   └── templates/
│       └── index.html    # Web UI
├── .gitignore
└── README.md
```

## Setup and Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/santhiyathinakaran/courier-tracking-system.git
   cd courier-tracking-system
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS / Linux
   ```

3. **Install dependencies**
   ```bash
   pip install flask requests python-dotenv
   ```

4. **Create a `.env` file** inside the `Universal_Tracker` folder and add your own API credentials:
   ```
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   ```

5. **Run the app**
   ```bash
   cd Universal_Tracker
   python app.py
   ```

6. Open **http://127.0.0.1:5000** in your browser and enter a tracking number.

## Usage

1. Enter a valid tracking number on the home page.
2. Click **Track**.
3. View the current status and shipment details.

## Future Improvements

- Support for multiple courier services
- Save tracking history in a MySQL database
- Email / SMS notifications on status change

## Author

**Santhiya P** — Full Stack Developer (Python | React.js | MySQL)
[LinkedIn](https://www.linkedin.com/in/santhiyathinakaran) | [GitHub](https://github.com/santhiyathinakaran)# courier-tracking-system
