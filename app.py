from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/')
def home():
    return "Starting flask backend"

@app.route("/api/submit", methods=['POST'])
def submit_data():
    event = request.args.get("event")
    
@app.route("/api/chat", methods=['GET'])
def submit_data():
    persona_Id = request.args.get("persona_Id")
    


