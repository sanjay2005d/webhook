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

        payload = data.get("payload", {})
        sender = payload.get("sender")
        timestamp = payload.get("timestamp")

        message = payload.get("message", {})
        reply_text = None

        # TEXT reply
        if "text" in message:
            reply_text = message["text"]

        # BUTTON reply
        elif message.get("type") == "button_reply":
            reply_text = message["reply"]["id"]

            # Save mobile number if the user clicked "Yes"
            if reply_text.lower() == "yes":
                received_at = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                with open("yes_responses.csv", "a") as f:
                    f.write(f"{sender},{received_at}\n")
                print(f"✅ Saved mobile {sender} at {received_at}")

        # Convert timestamp for logging
        received_at = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        print(f"📱 Mobile: {sender}")
        print(f"💬 Reply: {reply_text}")
        print(f"⏰ Time: {received_at}")

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"status": "error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
