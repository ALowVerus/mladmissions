import json 
import requests
import time
import urllib

# TOKEN = "708703702:AAG1Kkk4R2h_ePrillz-5ADIoCoGEiIMSE0"
TOKEN = "750446084:AAGWgtASCQwgiVNB5ZpbqOvR64uVtO2fuJ0"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

def get_url(url):
	response = requests.get(url)
	content = response.content.decode("utf8")
	return content

def get_json_from_url(url):
	content = get_url(url)
	js = json.loads(content)
	return js

# postData - sends student data in JSON request to python server
def postData(gpa, score, schoolList):
	print("\t\tReached the post request")
	# data to be sent to api as JSON
	jData = {
		"data":{
				"sat":score, # int in range 0-36 or 0-1600
				"gpa":gpa, # float between 0.0 and 4.0
				"colleges":schoolList
			}
		} # list of school names as strings
	print("\t\tMade JSON")
	# storing post request response (DON'T KNOW WHAT I'M DOING WITH LOADING)
	# import ipdb;ipdb.set_trace()
	rawResponse = requests.post("http://127.0.0.1:5000/predict", jData) # 10.142.0.2
	print("\t\tPost request done")
	# response = {
	# 		'data': {
	# 			'colleges': {
	# 				'Dartmouth': 0.80,
	# 				'Northeastern': 0.35
	# 			}
	# 		}
	# 	}
	print("\t\tMade JSON response")
	response = json.loads( rawResponse )
	print("\t\tResponse: ", response)
	# return post response data
	return response

# getEachChance - iterates over returned JSON object and returns list of chances
def getEachChance(schoolData):
	# create blank list to hold probabilities
	probList = []
	for data in schoolData:
		for school in schoolData[data]:
			for chance in schoolData[data][school]:
				# append each probability from JSON dict to probList
				probList.append( schoolData[data][school][chance] )
	# return simple list of all probabilities
	return probList

# noneChance - calculate likelihood of getting into none of the schools
def noneChance(schoolData):
	# start probability at 1
	probNone = 1
	# call getEachChance to get simple list of probabilities and store in probList
	probList = getEachChance(schoolData)
	# iterate over probability for every school given
	for u in range(len(probList)):
		# multiply one minus probability of acceptance for each school for all schools
		probNone = probNone * (1 - probList[u])
	# return probability that user gets into none of their chosen schools
	return probNone

# totalChance - calculates likelihood of getting into a given number of schools
def totalChance(numCurious, schoolData):
	# calculate probability that no acceptances happen
	probNone = noneChance(schoolData)
	# numCurious (one by default) minus probability of none happening
	totProb = numCurious - probNone
	# return chance of getting into given number of schools out of chosen schools
	return totProb

# sendGivenStats - builds and sends a message with the results the user has given
def sendGivenStats(updates, gpaVal, actChoice, stdVal, chosenSchools):
	theirStats = "Here are the stats you gave me:\n\n"
	# message about gpa
	gpaMsg = "    GPA: " + str(gpaVal) + "\n"
	theirStats += gpaMsg
	# message about test choice
	testMsg = "    Test Choice: "
	if actChoice:
		testMsg = testMsg + "ACT" + "\n"
	else:
		testMsg = testMsg + "SAT" + "\n"
	theirStats += testMsg
	# message about test score
	stdMsg = "    Test Score: " + str(stdVal) + "\n"
	theirStats += stdMsg
	# message about school choices
	schoolMsg = "    School Choices: "
	for n in range(len(chosenSchools)):
		if (n == 0):
			schoolMsg = schoolMsg + chosenSchools[n]
		if (n > 0):
			schoolMsg = schoolMsg + ", " + chosenSchools[n]
	schoolMsg += "\n"
	theirStats += schoolMsg
	replyMessage(updates, theirStats)

# sendResultsMessage - sends a formatted results message
def sendResultsMessage(updates, schoolData, getOne, getNone):
	global curStep # Current step in the interaction process
	# initialize results string
	resMsg = "Here is some info about your chances:\n\n"
	resMsg += "    Chance of getting into each school:\n"
	data = schoolData['data']
	colleges = data['colleges']
	school_list = colleges.keys()
	# i know this is terrible progamming, go away
	count = 0
	for x in school_list:
		count += 1
		resMsg += "        " + str(x) + ": "
		resMsg += str(colleges[x])
		if ( count != len(colleges) ):
			resMsg += "%\n"
		# end of college prob results
		else:
			resMsg += "%\n\n"
	# import ipdb;ipdb.set_trace()
	resMsg += "    Chance of getting into at least one of the schools: " + str(int(getOne * 100)) + "%\n\n"
	resMsg += "    Chance of not getting into any of the schools: " + str(int(getNone * 100)) + "%\n\n"
	# send the completed message
	replyMessage(updates, resMsg)

# resultsHandler - handles (through delegation) all results related stuff
def resultsHandler(updates):
	global curStep # Current step in the interaction process
	global actChoice # whether or not the user has chosen to use ACT (if false, SAT)
	global gpaVal # container for gpa
	global stdVal # container for test scores
	global chosenSchools # container for chosen schools
	global returnData # container for returned JSON
	print("\tHandling results...")
	# store returned insights in global returnData variable
	returnData = postData(gpaVal, stdVal, chosenSchools)
	print("\t\tPosted data successfully")
	# store chance of getting into at least 1 of chosen schools in getOne
	getOne = totalChance(1, returnData)
	print("\t\tGot the chance of getting into one school successfully")
	# store chance of getting into none of chosen schools in getNone
	getNone = noneChance(returnData)
	print("\t\tGot the chance of getting into no schools successfully")
	# send message with given data
	sendGivenStats(updates, gpaVal, actChoice, stdVal, chosenSchools)
	print("\t\tSent given stats successfully")
	# send message with calculated data
	sendResultsMessage(updates, returnData, getOne, getNone)
	print("\t\tSent results message successfully")
	print("\tFinished handling results")

def get_updates(offset=None):
	url = URL + "getUpdates?timeout=100"
	if offset:
		url += "&offset={}".format(offset)
	js = get_json_from_url(url)
	return js

def get_last_update_id(updates):
	update_ids = []
	for update in updates["result"]:
		update_ids.append(int(update["update_id"]))
	return max(update_ids)

def get_last_chat_id_and_text(updates):
	num_updates = len(updates["result"])
	last_update = num_updates - 1
	text = updates["result"][last_update]["message"]["text"]
	chat_id = updates["result"][last_update]["message"]["chat"]["id"]
	return (text, chat_id)

def send_message(text, chat_id):
	text = urllib.parse.quote_plus(text)
	url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
	get_url(url)

def echo_all(updates):
	for update in updates["result"]:
		try:
			text = update["message"]["text"]
			chat = update["message"]["chat"]["id"]
			send_message(text, chat)
		except Exception as e:
			print(e)

# replyMessage - send the given message to the most recent person
def replyMessage(updates, msg):
	# for each new message since last checking (though not built to support more than one)
	for update in updates["result"]:
		try:
			# the id of the person who sent the most recent chat
			person = update["message"]["chat"]["id"]
			# send a message to that person with the given string argument
			send_message(msg, person)
		except Exception as e:
			print(e)

# greet - sent greeting messages and ask for GPA
def greet(updates):
	msg = ["Hey! Let's get started.", "What's your GPA (on an unweighted 4.0 scale)?"]
	replyMessage(updates, msg[0])
	replyMessage(updates, msg[1])
	# update step value to gpa recorder
	global curStep
	curStep = 1

# gpa - interprets gpa and prompts for choosing a standardized test
def gpa(updates):
	global gpaVal
	global curStep
	for update in updates["result"]:
		try:
			# parse reply message as a float value
			result = float( update["message"]["text"] )
			# ensure that gpa is in proper range
			if (0.0 <= result <= 4.0):
				# set gpaVal to given GPA
				gpaVal = result
				# send message prompting for standardized testing choice
				replyMessage(updates, "And will you be submitting SAT or ACT scores?")
				# update step value to standardized testing choice interpreter
				curStep = 2
			# if it's not in the proper range
			else:
				# send message letting user know they've given an invalid GPA
				replyMessage(updates, "Sorry! Please give me a valid, unweighted GPA on a 4.0 scale.")
				# ensure that step value stays set to gpa recorder
				curStep = 1
		except ValueError as e:
			# send message letting user know they've given an invalid GPA
			replyMessage(updates, "Sorry! Please give me a valid, unweighted GPA on a 4.0 scale.")
			# ensure that step value stays set to gpa recorder
			curStep = 1

# chooseTest - interprets test choice and prompts for testing scores
def chooseTest(updates):
	global actChoice
	global curStep
	for update in updates["result"]:
		try:
			# set result to lowercase reply message
			result = ( update["message"]["text"] ).lower()
			# make sure they didn't give both tests
			if ( ( result.find('sat') != -1 ) and ( result.find('act') != -1 ) ):
				# tell them they have to choose one or the other
				# send message letting user know they've given an invalid test choice
				replyMessage(updates, "Sorry! Please choose one or the other.")
				# ensure that step value stays set to standardized testing choice interpreter
				curStep = 2
			# search for 'sat' in string
			elif ( result.find('sat') != -1 ):
				# if it finds it, set actChoice to False
				actChoice = False
				# send message prompting for SAT score choice
				replyMessage(updates, "And what was your composite score on the SAT?")
				# update step value to standardized testing score recorder
				curStep = 3
			elif ( result.find('act') != -1 ):
				# if it doesn't find SAT, but it does find ACT, set actChoice to True
				actChoice = True
				# send message prompting for ACT score choice
				replyMessage(updates, "And what was your cumulative score on the ACT?")
				# update step value to standardized testing score recorder
				curStep = 3
			else:
				# send message letting user know they've given an invalid test choice
				replyMessage(updates, "Sorry! Please choose either SAT or ACT.")
				# ensure that step value stays set to standardized testing choice interpreter
				curStep = 2
		except Exception as e:
			# send message letting user know they've given an invalid test choice
			replyMessage(updates, "Sorry! Please give me a proper answer.")
			# ensure that step value stays set to standardized testing choice interpreter
			curStep = 2

# testScore - interprets and records test score and prompts for choosing schools
def testScore(updates):
	global actChoice
	global stdVal
	global curStep
	maxRange = 0
	# set range based on chosen test
	if (actChoice == False):
		maxRange = 1600
	else:
		maxRange = 36
	for update in updates["result"]:
		try:
			# parse reply message as an int value
			result = int( update["message"]["text"] )
			# ensure that score is in proper range
			if (0 <= result <= maxRange):
				# set stdVal to given test score
				stdVal = result
				# send messages prompting for school choices
				replyMessage(updates, "And which schools do you want to go to?")
				replyMessage(updates, "(Please send them as individual messages, and say 'done' when you are finished.)")
				# update step value to school choice interpreter
				curStep = 4
			# if it's not in the proper range
			else:
				# send message letting user know they've given an invalid test score
				replyMessage(updates, "Sorry! Please give me a valid test score.")
				# ensure that step value stays set to test score recorder
				curStep = 3
		except ValueError as e:
			# send message letting user know they've given an invalid test score
			replyMessage(updates, "Sorry! Please give me a valid test score.")
			# ensure that step value stays set to test score recorder
			curStep = 3

# collegeChoices - interprets school choices and processes results
def collegeChoices(updates):
	global chosenSchools
	global curStep
	global actChoice
	global gpaVal
	global stdVal
	for update in updates["result"]:
		try:
			# set result to lowercase reply message
			result = ( update["message"]["text"] ).lower()
			# list of colleges we are allowing users to choose from
			collegeOptions = ["Dartmouth", "Columbia", "Northeastern", "Princeton"]
			# search for each school in the list
			for i in range(len(collegeOptions)):
				# if we find one of the schools in the response
				if ( result.find(collegeOptions[i].lower()) != -1 ):
					# add it to the list of chosen schools
					toAppend = collegeOptions[i]
					if (i <= 0):
						toAppend += " College"
					else:
						toAppend += " University"
					chosenSchools.append(toAppend)
					return
				# else if we find the word "done" in the response
				elif ( result.find("done") != -1 ):
					# send message letting user know you've gotten their choices
					replyMessage(updates,
						"Thanks! Please give me a moment to do some calculations.")
					resultsHandler(updates)
					print("Finished resultsHandler")
					curStep = 5
					# giveResults()
					return
			# send message letting user know they've given an invalid school choice
			replyMessage(updates,
				"Sorry! Please type either a valid school name or the word 'done'")
			# ensure that step value stays set to school choice interpreter
			curStep = 4
		except Exception as e:
			# send message letting user know they've given an invalid school choice
			replyMessage(updates,
				"Sorry! Please type either a valid school name or the word 'done'")
			# ensure that step value stays set to school choice interpreter
			curStep = 4
	
def main():
	last_update_id = None
	global curStep # Current step in the interaction process
	curStep = 0
	global actChoice # whether or not the user has chosen to use ACT (if false, SAT)
	actChoice = False
	global gpaVal # container for gpa
	gpaVal = 0.0
	global stdVal # container for test scores
	stdVal = 0
	global chosenSchools # container for chosen schools
	chosenSchools = []
	global returnData # container for returned JSON
	returnData = None
	while True:
		updates = get_updates(last_update_id)
		if len(updates["result"]) > 0:
			last_update_id = get_last_update_id(updates) + 1
			# since python doesn't have a switch statement, I'm using if/elif, sorry
			# user has not sent any info yet
			if (curStep == 0):
				greet(updates)
			# user sends gpa
			elif (curStep == 1):
				gpa(updates)
			# user chooses standardized test
			elif (curStep == 2):
				chooseTest(updates)
			# user sends standardized testing score
			elif (curStep == 3):
				testScore(updates)
			# user sends college choices
			elif (curStep == 4):
				collegeChoices(updates)
		time.sleep(0.5)

if __name__ == '__main__':
	main()