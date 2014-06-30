from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authentication import get_authorization_header
from rest_framework import parsers, renderers
from rest_framework import status
from social.apps.django_app.utils import strategy
#from social_auth.decorators import


class GetAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer
    model = Token

    # Accept backend as a parameter and 'auth' for a login / pass
    def post(self, request, backend):
        serializer = self.serializer_class(data=request.DATA)

        # Here we call PSA to authenticate like we would if we used PSA on server side.
        jwt_token = register_by_access_token(request, backend)

        # If user is active we get or create the REST token and send it back with user data
        if jwt_token:
            return Response({'token': jwt_token})
        return Response({'error': "Ai caramba!"})

@strategy()
def register_by_access_token(request, backend):
    backend = request.strategy.backend

    access_token = request.DATA.get('accessToken', None)

    if access_token:
        user = backend.do_auth(access_token)
        return user.get_jwt_token()
    return None
