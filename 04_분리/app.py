from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from views.chat import chat_bp 
from views.facefit_model import facefit_bp

app = Flask(__name__)
# CORS(app) 
CORS(app, origins=["http://127.0.0.1:5000"])

# Blueprint 
app.register_blueprint(chat_bp)
app.register_blueprint(facefit_bp)

# 페이지 이동 
@app.route("/")
def index():
    return render_template("main.html")

# 서버용 페이지이동..
@app.route("/chating")  
def chating():
    return render_template("chating.html")


if __name__ == "__main__":
    app.run( debug=True)
    # app.run(host="0.0.0.0", port=5017, debug=True)