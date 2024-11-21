from flask import Flask
from pymongo import MongoClient
from test_config import TestConfig

app = Flask(__name__)
app.config.from_object(TestConfig)
testing_client = MongoClient('localhost', 27017)
db = testing_client["pm-tool-test"]