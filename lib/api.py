import base64
import socket
import urllib
import urllib2
import sys
from config.config import skip,top,accountKey

try:
    import json
except ImportError:
    import simplejson as json


def BingSearch(domain):
    if domain.startswith("http://"):
        query = domain.replace("http://","")
    elif domain.startswith("https://"):
        query = domain.replace("https://","")
    else:
        query = domain
    ip = socket.gethostbyname(query)
    query = "ip:" + ip
    payload = {}
    payload['$top'] = top
    payload['$skip'] = skip
    payload['$format'] = 'json'
    payload['Query'] = "'" + query + "'"
    url = 'https://api.datamarket.azure.com/Bing/Search/Web?' + urllib.urlencode(payload)
    if accountKey != "":
        sAuth = 'Basic ' + base64.b64encode(':' + accountKey)
    else:
        sys.exit(0)

    headers = {}
    headers['Authorization'] = sAuth
    try:
        req = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(req)
        the_page = response.read()
        data = json.loads(the_page)
        return data
    except Exception as e:
        print e

