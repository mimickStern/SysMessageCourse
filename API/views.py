from django.shortcuts import render
#from django.http import JsonResponse
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
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
    try:
        receiver = request.user.id
        messages = Message.objects.filter(receiver=receiver)

        if not messages:
            # Handle the case where no messages are found
            return Response({"message": "No messages found for this user."}, status=status.HTTP_404_NOT_FOUND)

        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    except Exception as e:
        # Handle any unexpected exceptions
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

# get a message
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getReceivedMessage(request, id):
    message = Message.objects.get(id=id)
    serializer = MessageSerializer(message, many=False)
    return Response (serializer.data) 

# create a message
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addMessage(request):
    try:
        sender = request.user
        receiver_username = request.data["receiver"]
        subject = request.data["subject"]
        content = request.data["content"]
        
        # check if receiver exists in DB
        try:
            receiver = User.objects.get(username = receiver_username)
        except User.DoesNotExist:
            return Response ({"message": "Receiver does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the message
        print(Message.objects.create(sender=sender, receiver=receiver, subject=subject, content=content, unread=True))
        return Response("Message added.")
    except Exception as e:
        return Response ({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
# deleting a message
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteMessage(request,id):
    user = request.user
    print(user)
    try:
        # message = Message.objects.get(id=id, receiver=user)
        message = Message.objects.filter(Q(id=id), Q(sender=user) | Q(receiver=user)).first()
        if not message:
            return Response({"message": "Message not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check for specific permissions (adjust 'app_name.delete_message' as needed)
        if not user.has_perm('delete'):
            raise PermissionDenied("You do not have permission to delete this message.")
        message.delete()
        # serializer = MessageSerializer(message)
        return Response("message deleted")
    except PermissionDenied as e:
        return Response({"message": str(e)}, status=status.HTTP_403_FORBIDDEN)  # Return custom error message for permissions
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)