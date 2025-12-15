from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

@app.route("/gupshup/webhook", methods=["POST"])
def gupshup_webhook():
    try:
        data = request.get_json()
        print("🔔 Incoming webhook:")
        print(json.dumps(data, indent=2))

        # --- NEW: Check if the webhook is a user message event ---
        # The 'type' must be "message" for user conversations
        if data.get("type") != "message":
            print(f"ℹ️ Ignoring webhook type: {data.get('type')}")
            # Acknowledge the event and return 200 OK without processing further
            return jsonify({"status": "ok"}), 200
        # --- END NEW ---

        payload = data.get("payload", {})
        sender = payload.get("sender")
        timestamp = payload.get("timestamp")

        message = payload.get("message", {})
        reply_text = None

        # --- IMPORTANT CHECK for missing fields after filtering ---
        if not all([sender, timestamp, message]):
            print("⚠️ Missing required fields (sender, timestamp, or message).")
            # Return 200 OK to stop retries, but note the missing data
            return jsonify({"status": "ok"}), 200


        # TEXT reply
        if "text" in message:
            reply_text = message["text"]

        # BUTTON reply
        elif message.get("type") == "button_reply":
            reply_text = message["reply"]["id"]
            
        # --- NEW: Handle cases where reply_text is still None (e.g., media/location) ---
        if reply_text is None:
            print(f"ℹ️ Received non-text message type: {message.get('type')}")
            return jsonify({"status": "ok"}), 200 # Acknowledge non-text messages


        # Convert timestamp (now guaranteed to exist and be an integer/float)
        # Note: Gupshup timestamps are usually in milliseconds, but Python's fromtimestamp
        # expects seconds. Dividing by 1000.0 is safer.
        received_at = datetime.fromtimestamp(timestamp / 1000.0).strftime("%Y-%m-%d %H:%M:%S")

        print(f"📱 Mobile: {sender}")
        print(f"💬 Reply: {reply_text}")
        print(f"⏰ Time: {received_at}")

        # -------------------------
        # TODO: Save to DB / CRM
        # -------------------------

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("❌ Error:", str(e))
        # Important: Return 500 so Gupshup retries if the crash was temporary
        return jsonify({"status": "error"}), 500


if __name__ == "__main__":
    # Note: Use gunicorn for production, but app.run is fine for local testing
    app.run(host="0.0.0.0", port=5000)