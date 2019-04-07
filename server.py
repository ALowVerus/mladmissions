from flask import Flask
import json
from flask.ext.api import status
from flask import jsonify,request,Response
import uuid, random
from flask_cors import CORS
from navianceScraper.admittance_predictor import main_admittance_predictor

app=Flask(__name__)
CORS(app)
college_model_data = main_admittance_predictor()

@app.route('/predict', methods=['post'])
def predict():
	request_data = request.json['data']
	gpa = request_data['gpa']
	sat = request_data['sat']
	colleges = request_data['colleges']
	# call ml methods
	response = {}
	for college in colleges:
		response[college] = random.randint(0,100)
		model = college_model_data[college]["model"]
		prediction = model.predict([[sat, gpa]])
		response[college] = prediction
	return_json = {"data": {"colleges": response}}
	return json.dumps(return_json)

if __name__ == '__main__':
	app.run(host= '0.0.0.0', port=9000, debug=False)
