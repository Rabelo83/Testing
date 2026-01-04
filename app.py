from flask import Flask, jsonify, request
from scraper import get_standings

app = Flask(__name__)

@app.route("/")
def home():
    return {"status": "ok", "message": "SofaScore Scraper"}

@app.route("/scrape", methods=["GET"])
def scrape():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        data = get_standings(url)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
