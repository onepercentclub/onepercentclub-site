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
        user = register_by_access_token(request, backend)

        # If user is active we get or create the REST token and send it back with user data
        if user and user.is_active:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'id': user.id , 'name': user.username, 'userRole': 'user','token': token.key})



@strategy()
def register_by_access_token(request, backend):

    backend = request.strategy.backend
    # Split by spaces and get the array
    auth = get_authorization_header(request).split()

    #
    # if not auth or auth[0].lower() != b'token':
    #     msg = 'No token header provided.'
    #     return msg
    #
    # if len(auth) == 1:
    #     msg = 'Invalid token header. No credentials provided.'
    #     return msg
    #
    access_token=auth[0]
    # Real authentication takes place here
    user = backend.do_auth(access_token)

    return user