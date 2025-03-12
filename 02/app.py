from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app) 

@app.route("/")
def index():
    return render_template("main.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5017, debug=True)