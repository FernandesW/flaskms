from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>This is it hy and Final Bla blab Release Branch, World!</p>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5200, debug=True, use_reloader=False)
