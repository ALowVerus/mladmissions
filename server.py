from flask import Flask
import json
from flask import request
from navianceScraper.admittance_predictor import main_admittance_predictor

app=Flask(__name__)
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
		model = college_model_data[college]
		prediction = model.predict_proba([[sat, gpa]])[0][1]
		print(prediction)
		response[college] = prediction
	return_json = {"data": {"colleges": response}}
	return json.dumps(return_json)


if __name__ == '__main__':
	app.run(host= '0.0.0.0', port=9000, debug=False)
