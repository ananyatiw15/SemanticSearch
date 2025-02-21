from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization"]}})

API_URL = "http://18.191.173.194:8080/query"

@app.route('/query', methods=['POST'])
def query_research_papers():
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        k = int(data.get("k", 10))  # Default to 10 results if not provided

        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400

        # 🔍 Debugging: Print the request being sent
        print(f"Sending request to {API_URL} with query: {query}, k: {k}")

        # 🔄 Forward the request to the external API
        response = requests.post(API_URL, json={"query": query, "k": k}, headers={"Content-Type": "application/json"})

        # 🔍 Debugging: Print the full response from external API
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")

        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch data. Status: {response.status_code}", "details": response.text}), response.status_code

        return jsonify(response.json())

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debugging
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
