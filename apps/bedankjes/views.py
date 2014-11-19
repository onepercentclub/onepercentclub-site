from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import json

@api_view(['GET', 'POST'])
def donation_trigger(request):
    """
        Test view to trigger the sending of a dummy donation
    """

    if request.method == "GET":
        return Response("Request must be POST")

    if request.method == 'POST':

        payload = {}
        payload['identifier'] = "Test identifier"
        payload['first_name'] = "Test first name"
        payload['last_name'] = "Test last name"
        payload['name'] = "Test name"
        payload['city'] = "Test Amsterdam"
        payload['email'] = "test@testing.com"
        payload['project'] = "Test project title"
        payload['amount'] = "280"

        url = "http://stage-onepercentclub.campaignapps.nl/api/donations/new"
                
        r = requests.post(url, data=json.dumps(payload))

        if r.status_code == 200:
            result = "success"
        else:
            result = "error"

        return Response(result)

