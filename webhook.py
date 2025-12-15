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

        # --- Ignore non-message events (e.g., system/sandbox events) ---
        if data.get("type") != "message":
            print(f"ℹ️ Ignoring webhook type: {data.get('type')}")
            return jsonify({"status": "ok"}), 200

        payload = data.get("payload", {})
        sender = payload.get("sender")
        timestamp = data.get("timestamp")  # Root-level timestamp

        message = payload.get("message", {})
        reply_text = None

        # --- Safety check for required fields ---
        if not all([sender, timestamp, message]):
            print("⚠️ Missing required fields (sender, timestamp, or message).")
            return jsonify({"status": "ok"}), 200

        # --- Text reply ---
        if "text" in message:
            reply_text = message["text"]

        # --- Button reply ---
        elif message.get("type") == "button_reply":
            reply_text = message["reply"]["id"]

            # Save sender (mobile) if "Yes" button clicked
            if reply_text.lower() == "yes":
                received_at = datetime.fromtimestamp(timestamp / 1000.0).strftime("%Y-%m-%d %H:%M:%S")
                with open("yes_responses.csv", "a") as f:
                    f.write(f"{sender},{received_at}\n")
                print(f"✅ Saved mobile {sender} at {received_at}")

        # Handle unsupported/non-text messages
        if reply_text is None:
            print(f"ℹ️ Received non-text message type: {message.get('type')}")
            return jsonify({"status": "ok"}), 200

        # Convert timestamp to human-readable
        received_at = datetime.fromtimestamp(timestamp / 1000.0).strftime("%Y-%m-%d %H:%M:%S")
        print(f"📱 Mobile: {sender}")
        print(f"💬 Reply: {reply_text}")
        print(f"⏰ Time: {received_at}")

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"status": "error"}), 500


if __name__ == "__main__":
    # Use gunicorn in production; app.run is fine for local testing
    app.run(host="0.0.0.0", port=5000)
