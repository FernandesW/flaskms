from flask import Flask
from functools import update_wrapper
app = Flask(__name__)


@app.route("/side")
def hello_world():
    return "<p>cherry in FWS0001</p>"


if __name__=='__main__':
    print(hello_world())