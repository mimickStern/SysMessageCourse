from django.shortcuts import render
#from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import Message
from .serializers import MessageSerializer
# Create your views here.


#Login/SignIn
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        # ...

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer



# register/signup
@api_view(['GET','POST'])
def signUp(request):
    user=User.objects.create_user(
        username= request.data["username"],
        email=request.data["email"],
        password=request.data["password"]
    )
    token = RefreshToken.for_user(user)
    return Response({
        'access': str(token.access_token),
        'refresh': str(token),
        'username': user.username,
        'email': user.email
    })


# first step
@api_view(['GET'])
def getRoutes(request):
    routes = [
        {
            'Endpoint': '/received-messages/',
            'method': 'GET',
            'body': None,
            'description': 'Returns an array of received messages'
        },
        {
            'Endpoint': '/add-message/',
            'method': 'POST',
            'body': {'body': ""},
            'description': 'Creates new message with data sent in post request'
        },
        {
            'Endpoint': '/delete-message/id/',
            'method': 'DELETE',
            'body': None,
            'description': 'Deletes and exiting message'
        },
    ]
    #return JsonResponse(routes , safe=False)
    return Response (routes)


# get all messages
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getReceivedMessages(request):
    messages = Message.objects.all()
    serializer = MessageSerializer(messages, many=True)
    return Response (serializer.data) 

# get a message
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getReceivedMessage(request, id):
    message = Message.objects.get(id=id)
    serializer = MessageSerializer(message, many=False)
    return Response (serializer.data) 