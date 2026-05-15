from rest_framework.generics import ListCreateAPIView
from .serializers import MessageSerializer,RoomSerializer
from .models import Message,Room


class MessageView(ListCreateAPIView):   
    serializer_class=MessageSerializer

    def get_queryset(self):
        room_id=self.kwargs['room_id']
        return Message.objects.filter(room=room_id)

class RoomListCreateAPiView(ListCreateAPIView):
    queryset=Room.objects.all()
    serializer_class=RoomSerializer

