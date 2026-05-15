from django.urls import path
from .views import MessageView,RoomListCreateAPiView

urlpatterns=[
   path('messages/<int:room_id>/',MessageView.as_view(),name='message_list'),   
   path('room/',RoomListCreateAPiView.as_view(),name='room')

]