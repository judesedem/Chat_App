from django.db import models

class Room(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(null=False,max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Message(models.Model):
    id=models.AutoField(primary_key=True)
    room=models.ForeignKey(Room,on_delete=models.CASCADE,related_name='messages')
    username=models.CharField(null=False,max_length=30)
    content=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering=['created_at']

    def __str__(self):
        return f"{self.username}:{self.content[:50]}"

    




