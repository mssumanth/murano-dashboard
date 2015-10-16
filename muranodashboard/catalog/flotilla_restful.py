import traceback
import time
from time import mktime
from datetime import datetime
from requests.auth import HTTPBasicAuth

from django.template.defaultfilters import register
from django.utils.translation import ugettext_lazy as _
import requests, json

from horizon import exceptions

data = json.dumps({'name':'test', 'description':'some test repo'})
url = 'http://127.0.0.1:7007/connect_ipsec'

def deployApp(app):
    try:
        print "APP which is getting deployed is:",app
        payload = {'name': app.name,
                   'image' : app.fully_qualified_name}
        print 'payload: ',payload
        headers = {'content-type': 'application/json'}
        req = requests.post(url, data=json.dumps(payload), headers = headers)
    except:
        print "Exception occurred at deployApps"
        return False
