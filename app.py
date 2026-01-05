from flask import Flask, request, jsonify
import traceback
from standings import get_standings

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "Football Standings API via API-Football"
    })

@app.route("/standings")
def standings():
    league = request.args.get("league")
    season = request.args.get("season") # Optional: e.g., 2023

    if not league:
        return jsonify({"error": "Missing league parameter"}), 400

    try:
        data = get_standings(league.lower(), season)
        return jsonify(data)
    except Exception as e:
        return jsonify({
            "error": "Standings Lookup Failed",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
