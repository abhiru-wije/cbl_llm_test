from flask import Flask, request, jsonify
import json
from executor import execution_function
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

@app.route('/', methods=['POST'])
def health_check():
    return jsonify("Health Check Success")


@app.route("/send_email", methods=["POST"])
def send_email():
    try:
        email_payload = request.json
        if not email_payload:
            return jsonify({"error": "No JSON payload provided"}), 400
        
        required_fields = ["from_address", "to_address", "subject", "body", "created_date"]
        missing_fields = [field for field in required_fields if field not in email_payload]
        
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        response = execution_function(email_payload)
        return jsonify("EMAIL PROCESS SUCCESSFUL", response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)