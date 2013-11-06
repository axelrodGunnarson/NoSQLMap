from utils import logging
from lib.utils.check import checkInput

#write check with checkInput dictionary->dic of funcs for check parameters
class Options():
    victim="127.0.0.1"
    webPort=80
    uri="/"
    httpMethod=1 #1-GET 2-POST
    myIP="127.0.0.1"
    myPort=8080

    def setInteractiveOptions(self):
        '''ask options to user interactively'''
        def askParameter(request, answer, paramName):
            '''ask parameter, check correctness and eventually log message'''
            ch=False
            while not ch:
                par = raw_input(request)
                ch=checkInput[paramName](par)
            logging(answer+" "+par)
            return par

        self.victim=askParameter("Enter the host IP/DNS name: ", "Target set to", "victim")
        self.webPort = askParameter("Enter the HTTP port for web apps: ", "HTTP port set to", "port")
        self.uri = askParameter("Enter URI Path (Press enter for no URI): ", "URI Path set to", "uri")
        self.httpMethod=askParameter("1-Send request as a GET"+"\n"+"2-Send request as a POST"+"\n"+"choose method: ", "method chosen: ", "httpMethod")
        self.myIP = askParameter("Enter host IP for my Mongo/Shells: ","local IP set to ","ip")
        self.myPort = askParameter("Enter TCP listener for shells: ","Shell TCP listener set to ", "port")

    def setFileOptions(self):
        '''read options from file'''
        pass

    def printPossibleOptions(self):
        '''log possible options'''
        logging("Options")
        logging("1-Set target host/IP (Current: " + str(self.victim) + ")")
        logging("2-Set web app port (Current: " + str(self.webPort) + ")" )
        logging("3-Set URI Path (Current: " + str(self.uri) + ")")
        logging("4-Set HTTP Request Method (1-GET/2-POST, current: "+str(self.httpMethod)+")")
        logging("5-Set my local Mongo/Shell IP (Current: " + str(self.myIP) + ")")
        logging("6-Set shell listener port (Current: " + str(self.myPort) + ")")
