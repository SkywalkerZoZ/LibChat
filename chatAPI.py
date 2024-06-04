from flask import Flask, request, jsonify,Response
from chatBot import LibChatBot
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
chat_model = LibChatBot()

@app.route('/chat', methods=['POST'])

def ask():
    data = request.get_json()
    question = data.get('question')
    if not question:
        return jsonify({"error": "No question provided"}), 400
    try:
        def generate():
            for item in chat_model.ask_api(question):
                yield item
        return Response(generate(), content_type='text/plain')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except RuntimeError as e:
        print(f"Initialization failed: {e}")