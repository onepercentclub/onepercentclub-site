from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import json

@api_view(['GET', 'POST'])
def donation_trigger(request):
    """
        Test view to trigger the sending of a dummy donation
    """

    if request.method == 'POST':

        payload = {}
        payload['identifier'] = "Test identifier"
        payload['name'] = "Test name"
        payload['email'] = "test@testing.com"
        payload['project'] = "Test project title"
        payload['amount'] = "280"

        url = "http://31.3.103.106"
        
        print "Payload", json.dumps(payload)
        
        r = requests.post(url, data=json.dumps(payload))

        if r.status_code == 200:
            result = "success"
        else:
            result = "error"

        return Response(result)

