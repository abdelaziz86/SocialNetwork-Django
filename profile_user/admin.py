from django.contrib import admin
from .models import Message, Notification, Preaccount, Profile, Pub, Connection, Reaction, PostComment, RoomMember, Verification, WorkExperience, Location
# Register your models here. 

admin.site.register(Profile)
admin.site.register(Pub) 
admin.site.register(Connection) 
admin.site.register(Reaction) 
admin.site.register(PostComment)
admin.site.register(WorkExperience)
admin.site.register(Location)
admin.site.register(Message)
admin.site.register(Verification)
admin.site.register(Preaccount)
admin.site.register(RoomMember)
admin.site.register(Notification)

