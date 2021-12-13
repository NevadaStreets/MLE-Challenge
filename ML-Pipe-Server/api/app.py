import pandas as pd
import pickle
import json
from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello welcome to the ML API, to make predictions, send a json object to /predict\n'

@app.route('/predict', methods = ['POST'])
def predict():
    request_data = request.get_json()
    json_data = json.dumps(request_data["data"])
    data = pd.read_json(json_data)
    loaded_model = pickle.load(open("final_model.sav", 'rb'))
    y_predicted = loaded_model.predict(data)
    prediction = json.dumps(y_predicted.tolist())

    return prediction
