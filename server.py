from flask import Flask
import json
from flask.ext.api import status
from flask import jsonify,request,Response
import uuid, random
from flask_cors import CORS

app=Flask(__name__)
CORS(app)

@app.route('/predict', methods=['post'])
def predict():
	request_data = request.json['data']
	gpa = request_data['gpa']
	sat = request_data['sat']
	colleges = request_data['colleges']
	# call ml methods
	response = dict()
	for x in colleges:
		response[x] = random.randint(0,100)
	return_json = {"data": {"colleges": response}}
	return json.dumps(return_json)

if __name__ == '__main__':
	app.run(host= '0.0.0.0', port=9000, debug=False)
