import os
import sys
import asyncio
from flask import Flask, request, jsonify, render_template

# Add project root and agents to sys.path so imports work properly
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import the orchestrator process_message function
from agents.orchestrator import process_message
from memory import load_profile

app = Flask(__name__)

@app.route("/")
def index():
    profile = load_profile()
    if profile.skin_type and profile.undertone:
        greeting = f"Hey! Welcome back, gorgeous. 💖 Still matching your {profile.skin_type} skin and {profile.undertone} undertone! What are we working on today? ✨"
    else:
        greeting = "Hey love! Welcome to Jamalek, your new skincare and makeup bestie. 💖 Tell me a bit about your skin, or drop a selfie so we can get started! ✨"
        
    disclaimer = "Jamalek provides personalised beauty guidance only. It is not a medical tool and does not diagnose skin conditions. Always patch test new products and consult a dermatologist for persistent skin concerns."
    return render_template("index.html", greeting=greeting, disclaimer=disclaimer)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400
        
    user_message = data["message"]
    
    try:
        # Run the async orchestrator function synchronously using asyncio.run
        response_text = asyncio.run(process_message(user_message))
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5001))
    debug_mode = os.environ.get("FLASK_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
