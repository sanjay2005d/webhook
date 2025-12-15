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

        # --- Ignore non-message events (system events, sandbox events) ---
        if data.get("type") != "message":
            print(f"ℹ️ Ignoring webhook type: {data.get('type')}")
            return jsonify({"status": "ok"}), 200

        # --- Extract timestamp from root ---
        timestamp = data.get("timestamp")
        if timestamp is None:
            print("⚠️ Missing timestamp in webhook")
            return jsonify({"status": "ok"}), 200
        received_at = datetime.fromtimestamp(timestamp / 1000.0).strftime("%Y-%m-%d %H:%M:%S")

        # --- Extract payload and sender ---
        payload = data.get("payload", {})
        sender_info = payload.get("sender", {})
        sender = sender_info.get("phone")
        if not sender:
            print("⚠️ Missing sender phone number")
            return jsonify({"status": "ok"}), 200

        # --- Extract message / reply ---
        message_type = payload.get("type")
        reply_payload = payload.get("payload", {})
        reply_text = reply_payload.get("text")  # This is the user reply (Yes/No)

        if not reply_text:
            print(f"ℹ️ No reply text found (message type: {message_type})")
            return jsonify({"status": "ok"}), 200

        print(f"📱 Mobile: {sender}")
        print(f"💬 Reply: {reply_text}")
        print(f"⏰ Time: {received_at}")

        # --- Save mobile if user clicked "Yes" ---
        if reply_text.strip().lower() == "yes":
            with open("yes_responses.csv", "a") as f:
                f.write(f"{sender},{received_at}\n")
            print(f"✅ Saved mobile {sender} at {received_at}")

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"status": "error"}), 500


if __name__ == "__main__":
    # Use gunicorn in production; app.run is fine for testing
    app.run(host="0.0.0.0", port=5000)
