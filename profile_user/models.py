from django.db import models
from django.contrib.auth import get_user_model
import uuid
from  datetime import datetime   
User = get_user_model()
 
# Create your models here.
class Location(models.Model): 
    user = models.CharField(max_length=100, blank=True)
    ip = models.TextField(blank=True)
    city = models.TextField(blank=True)
    region = models.TextField(blank=True)
    country = models.TextField(blank=True)
    latitude = models.FloatField(blank=True)
    longitude = models.FloatField(blank=True) 
     


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='blank_prof_pic.png')
    name = models.TextField(blank=True)
    surname = models.TextField(blank=True) 
    domaine = models.TextField(blank=True)

    
    phone = models.TextField(default="")
    sector = models.TextField(blank=True)
    birth = models.DateField(default=datetime.now)  
    degree = models.TextField(default="")  
    cv = models.ImageField(upload_to='verify_images', blank=True)

    verified = models.IntegerField(blank=True, default=0)
    type = models.IntegerField(default = 1)
    no_of_followers = models.IntegerField(default=0)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, default= 5, blank=True)
    def __str__(self):
        return self.user.username

class Pub(models.Model): 
    id_User = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    id_Profile = models.ForeignKey(Profile, on_delete=models.CASCADE, default=1)
    image = models.ImageField(upload_to='post_images', blank=True)
    caption = models.TextField()
    created_at =  models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)
    no_of_comments = models.IntegerField(default=0)  
    tag = models.TextField(blank=True)
    fileType = models.IntegerField(default=0)
    
    def __str__(self):
        return self.id_User.username

class Connection(models.Model):
    connecter = models.ForeignKey(Profile, on_delete=models.CASCADE, default=1)
    connected = models.CharField(max_length=100)
    verified = models.IntegerField(blank=True, default=0)
    def __str__(self):
        return self.connected 
 
class Reaction(models.Model):
    reacter = models.ForeignKey(Profile, on_delete=models.CASCADE, default=1)
    pub = models.ForeignKey(Pub, on_delete=models.CASCADE, default=1)
    created_at =  models.DateTimeField(default=datetime.now)
    def __str__(self):
        return self.reacter.name 

class PostComment(models.Model):
    commenter = models.ForeignKey(Profile, on_delete=models.CASCADE, default=1)
    pub = models.ForeignKey(Pub, on_delete=models.CASCADE, default=1)
    desc = models.TextField()
    created_at =  models.DateTimeField(default=datetime.now)
    def __str__(self):
        return self.commenter.name 


class WorkExperience(models.Model):
    worker = models.ForeignKey(Profile, on_delete=models.CASCADE, default=1, blank=True)
    company = models.CharField(max_length=100)
    companyName = models.TextField(blank=True)
    companyImage = models.ImageField(upload_to='post_images', blank=True)
    task = models.TextField()
    start =  models.DateField()
    end =  models.DateField()
    

    def __str__(self):
        return self.worker


 
class Message(models.Model):
    sender  = models.ForeignKey(Profile, on_delete=models.CASCADE, default=1)
    receiver = models.CharField(max_length=100)
    desc = models.TextField(default="")
    created_at =  models.DateTimeField(default=datetime.now)
    def __str__(self):
        return self.receiver 

class Verification(models.Model):
    profile  = models.ForeignKey(Profile, on_delete=models.CASCADE, default=1)
    card = models.ImageField(upload_to='verify_images', blank=True)
    read = models.IntegerField(default=0)
    created_at =  models.DateTimeField(default=datetime.now)
    def __str__(self):
        return self.profile.user.username 

class Preaccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    name = models.TextField(default="")
    surname = models.TextField(default="")
    birth = models.DateField(default=datetime.now, blank=True)
    email = models.TextField(default="")
    phone = models.TextField(default="")
    degree = models.TextField(default="")
    sector = models.TextField(default="")
    field = models.TextField(default="")
    cv = models.ImageField(upload_to='verify_images', blank=True)
    type = models.TextField(default="expert")

    created_at =  models.DateTimeField(default=datetime.now)
    def __str__(self):
        return self.name 

class RoomMember(models.Model):
    name = models.CharField(max_length=200)
    uid = models.CharField(max_length=1000)
    room_name = models.CharField(max_length=200)
    insession = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Notification(models.Model):
    sender  = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True)
    profile = models.CharField(max_length=100)
    desc = models.TextField(default="")
    created_at =  models.DateTimeField(default=datetime.now)
    def __str__(self):
        return self.profile 