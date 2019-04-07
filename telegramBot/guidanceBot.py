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
	# temp stuff
	global actChoice
	global gpaVal
	global stdVal
	# end temp stuff
	for update in updates["result"]:
		try:
			# set result to lowercase reply message
			result = ( update["message"]["text"] ).lower()
			# list of colleges we are allowing users to choose from
			collegeOptions = ["Dartmouth", "Northeastern", "Colby"]
			# search for each school in the list
			for i in range(len(collegeOptions)):
				# if we find one of the schools in the response
				if ( result.find(collegeOptions[i].lower()) != -1 ):
					# add it to the list of chosen schools
					chosenSchools.append(collegeOptions[i])
					return
				# else if we find the word "done" in the response
				elif ( result.find("done") != -1 ):
					# send message letting user know you've gotten their choices
					replyMessage(updates,
						"Thanks! Please give me a moment to do some calculations.")
					# start temp stuff
					# send message reading out users choices
					replyMessage(updates, "Here's what I have for your stats:")
					# message about gpa
					gpaMsg = "GPA: " + str(gpaVal)
					replyMessage(updates, gpaMsg)
					# message about test choice
					testMsg = "Test Choice: "
					if actChoice:
						testMsg = testMsg + "ACT"
					else:
						testMsg = testMsg + "SAT"
					replyMessage(updates, testMsg)
					# message about test score
					stdMsg = "Test Score: " + str(stdVal)
					replyMessage(updates, stdMsg)
					# message about school choices
					schoolMsg = "School Choices: "
					for n in range(len(chosenSchools)):
						if (n == 0):
							schoolMsg = schoolMsg + chosenSchools[n]
						if (n > 0):
							schoolMsg = schoolMsg + ", " + chosenSchools[n]
					replyMessage(updates, schoolMsg)
					# end temp stuff
					# update step value to results
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