from flask import Flask

app = Flask(__name__)

from pandemic2020 import routes
