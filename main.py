from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Commited on laptop</p>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5200, debug=True, use_reloader=False)
