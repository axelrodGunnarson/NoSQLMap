#!/usr/bin/python
#NoSQLMap Copyright 2013 Russell Butturini Maurizio Abba'
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


def checkIP(ip):
    '''check if ip is valid'''
    pass

def checkPort(port):
    '''check if port is valid'''
    pass

def checkUri(uri):
    '''check if uri is valid'''
    pass

def checkHTTPMethod(method):
    '''check if method is 1-GET or 2-POST'''
    pass

def checkVictim(victim):
    '''check if victim is valid, can be a url or an IP'''
    pass

checkInput = {
        "victim":checkVictim,
        "port":checkPort,
        "uri":checkUri,
        "httpMethod":checkHTTPMethod,
        "ip":checkIP,
        }
