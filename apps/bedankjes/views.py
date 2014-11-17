from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET', 'POST'])
def donation_trigger(requests):
	"""
		Test view to trigger a donation_trigger
	"""

	if request.method == 'POST':
		return Response("test")
