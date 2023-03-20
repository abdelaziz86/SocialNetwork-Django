from email import message
from msilib.schema import tables
from queue import Empty
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Preaccount, Profile, Pub, Notification, Connection, Reaction, PostComment, Verification, WorkExperience, Location, Message, RoomMember
from django.contrib.auth.decorators import login_required
import requests
from datetime import date, datetime
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from agora_token_builder import RtcTokenBuilder
import random
import time
import json
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


def get_ip():
    response = requests.get('https://api64.ipify.org?format=json').json()
    return response["ip"]


def get_location():
    ip_address = get_ip()
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    location_data = {
        "ip": ip_address,
        "city": response.get("city"),
        "region": response.get("region"),
        "country": response.get("country_name"),
        "latitude" : response.get("latitude"),
        "longitude" : response.get("longitude"), 

    }
    return location_data

def get_friends(pk):
    user = User.objects.get(username = pk)
    user_profile = Profile.objects.get(user= user)
    
    connections = []
    total1 =  Connection.objects.filter( connected=user_profile.user.username, verified=2)  ## eli b3ath howa lconnecté
    for t in total1:
        connections.append(t.connecter)

    total2 =  Connection.objects.filter( connecter=user_profile, verified = 2)  ## eli b3ath howa lconnecté
    for t in total2:
        user_object = User.objects.get(username=t.connected)
        prof = Profile.objects.get(user=user_object)  
        connections.append(prof)
    return connections

def get_Notifications(pk): 
    notifications = Notification.objects.filter(profile = pk).order_by('-created_at')   
    nots = []
    for n in notifications:
        nots.append(n)
    return nots





@login_required(login_url='signin')
def index(request):
    ####### POSTS
    user_profile = Profile.objects.get(user=request.user)
    posts = []
    connections = []
    total1 =  Connection.objects.filter( connected=user_profile.user.username, verified=2)  ## eli b3ath howa lconnecté
    for t in total1:
        connections.append(t.connecter)

    total2 =  Connection.objects.filter( connecter=user_profile, verified = 2)  ## eli b3ath howa lconnecté
    for t in total2:
        user_object = User.objects.get(username=t.connected)
        prof = Profile.objects.get(user=user_object)  
        connections.append(prof)
    
    connections.append(user_profile)
    posts = Pub.objects.filter(id_Profile__in=connections).order_by('-created_at') 
    
    ######## Connections
    ############## connections
    connection = Connection.objects.filter(connected=request.user.username, verified=1)
    if len(connection)==0:
        connection = "empty"

    ##### companies
    companies = Profile.objects.filter(type=2)[:3]
 

    ### friends 
    friends = get_friends(request.user.username)
    return render(request, 'feed/home.html', {'user_profile' : user_profile, 'posts' : posts, 'connection' : connection, 'companies' : companies , 'friends' : friends  })   

@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    prof = Profile.objects.get(user=user_object)

    user_profile = Profile.objects.get(user=request.user)
    username = request.user.username
    user_model = User.objects.get(username=username)
    fileType=0

    ############## POSTS
    if request.method == 'POST':
        caption = request.POST['message']

        if request.FILES.get('image')!=None: 
            image = request.FILES.get('image') 
            print(request.FILES['image'].name)
            if request.FILES['image'].name.endswith('.mp4'):
                fileType = 2
            else:
                fileType = 1
            post = Pub.objects.create(id_User=user_model, id_Profile = user_profile , caption=caption, image=image, fileType=fileType)
        else :
            post = Pub.objects.create(id_User=user_model, id_Profile = user_profile , caption=caption, image="null" ,fileType=fileType)
        post.save()
        if request.POST.get('home'):
            return redirect('index')
         
    posts = Pub.objects.filter(id_User=user_object).order_by('-created_at')
    
    ############## connections
    cas = 1 
    connection = Connection.objects.filter(connecter=user_profile, connected=prof.user.username) ## eli b3ath howa lconnecté
    if len(connection)==0:
        connection = Connection.objects.filter(connected=user_profile.user.username, connecter=prof) ## eli b3ath howa profile
        if len(connection)==0:
            connection = "empty"
        else:
            cas= 2

    ########### total connections 
    total1 = len(Connection.objects.filter( connected=prof.user.username, verified=2)) ## eli b3ath howa lconnecté
    total2 = len(Connection.objects.filter( connecter=prof, verified = 2)) ## eli b3ath howa lconnecté
    total = total1 + total2

    ########### Work exp
    workExp = WorkExperience.objects.filter(worker = prof)
    empty = 0
    if len(workExp)==0:
        empty = 1
    ### friends 
    friends = get_friends(request.user.username)
    return render(request, 'user/user-page.html', {'user_profile' : user_profile, 'posts' : posts, 'prof' : prof, 'connection' : connection, 'cas' : cas , 'total' : total, 'workExp' : workExp, 'friends' : friends, 'empty' : empty })



def signup(request,pk):
    if request.method == "POST":
        type = request.POST['type']
        if type == "expert":
            name = request.POST['name']
            surname = request.POST['surname']
            birth = request.POST['birth']
            phone=request.POST['phone']
            d1 = datetime.strptime(birth, "%Y-%m-%d")
            if ((datetime.today() - d1).days /360) < 20:
                messages.info(request,'Only experts with 20 years old or above are allowed.')
                return redirect('signup', pk=pk) 
            degree = request.POST['degree']
            sector = request.POST['sector']
            field = request.POST['field']

            cv=""
            if request.FILES.get('image')==None:
                messages.info(request,'Make sure to upload your CV.')
                return redirect('signup', pk=pk)
            else:
                cv = request.FILES.get('image')

            ### creating user
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            password2 = request.POST['password2']     

            if password == password2:
                if User.objects.filter(email = email).exists():
                    messages.info(request,'Email taken')
                    return redirect('signup', pk=pk)
                elif User.objects.filter(username = username).exists():
                    messages.info(request,'Username taken')
                    return redirect('signup', pk=pk)
                else:
                    user = User.objects.create_user(username=username, email=email, password=password )
                    user.save()
                    preaccount = Preaccount.objects.create(user=user, name=name, surname = surname, birth = birth, phone=phone, email=email, degree= degree, sector=sector, field=field, cv=cv, type=type)
                    preaccount.save()
            else:
                messages.info(request,'Passwords Not matching')
                return redirect('signup', pk=pk)




            
            return redirect('info')


        elif type == "company":
            name = request.POST['name'] 
            birth = request.POST['birth']
            phone=request.POST['phone']
            d1 = datetime.strptime(birth, "%Y-%m-%d")
            if (datetime.today() < d1 ):
                messages.info(request,'Please enter a valid establishment date.')
                return redirect('signup', pk=pk) 
            sector = request.POST['sector']
            field = request.POST['field']

            cv=""
            if request.FILES.get('image')==None:
                messages.info(request,'Make sure to upload your company paper.')
                return redirect('signup', pk=pk)
            else:
                cv = request.FILES.get('image')

            ### creating user
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            password2 = request.POST['password2']     

            if password == password2:
                if User.objects.filter(email = email).exists():
                    messages.info(request,'Email taken')
                    return redirect('signup', pk=pk)
                elif User.objects.filter(username = username).exists():
                    messages.info(request,'Username taken')
                    return redirect('signup', pk=pk)
                else:
                    user = User.objects.create_user(username=username, email=email, password=password )
                    user.save()
                    preaccount = Preaccount.objects.create(user=user, name=name,   birth = birth, phone=phone, email=email,   sector=sector, field=field, cv=cv, type=type)
                    preaccount.save()
            else:
                messages.info(request,'Passwords Not matching')
                return redirect('signup', pk=pk)   
             
            
            return redirect('info')
    return render(request, 'user/register.html', {'type' : pk })

def signin(request):  
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            ##profile = Profile.objects.filter(user = user)
            if  Profile.objects.filter(user = user).exists():
                auth.login(request,user) 
                return redirect('/')
            else:
                return redirect('/info') 
        else:
            messages.info(request,'User not found.')
            return redirect('signin')
 
    else:
        return render(request, 'user/login.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    ### friends 
    friends = get_friends(request.user.username)
    return render(request, 'user/default-settings.html', {'user_profile' : user_profile , 'friends' : friends})

@login_required(login_url='signin')
def profileEdit(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method=='POST':
        image=""
        if request.FILES.get('image')==None:
            image = user_profile.profileimg
        else:
            image = request.FILES.get('image')

        bio = request.POST['bio'] ; 
        name = request.POST['name'] ; 
        surname = request.POST['surname'] ; 
        domaine = request.POST['domaine'] ; 
        sector = request.POST['sector'] ;  
        phone = request.POST['phone'] ; 
        birth = request.POST['birth'] ; 
        country = request.POST['country']
        region = request.POST['region']
        city = request.POST['city']
        latitude = request.POST['latitude']
        longitude = request.POST['longitude']
        

        user_profile.profileimg = image 
        user_profile.bio = bio
        user_profile.name = name
        user_profile.surname = surname 
        user_profile.domaine = domaine
        user_profile.sector = sector
        if user_profile.type==1:
            degree = request.POST['degree'] ;
            user_profile.degree = degree
        user_profile.phone = phone
        user_profile.birth = birth
        
        lo = Location.objects.filter(user=user_profile.user.username)

        if len(lo) == 0:
            l = Location.objects.create(
                user = user_profile.user.username,
                city = city,
                region=region,
                country = country,
                latitude = latitude,
                longitude = longitude
            )
            user_profile.location = l
            l.save()
        else:
            loc = Location.objects.get(user=user_profile.user.username)  
            loc.city = city
            loc.region = region 
            loc.country = country 
            user_profile.location = loc

            loc.save()

        user_profile.save()
        return redirect('profileEdit')
    
    ### friends 
    friends = get_friends(request.user.username)
    return render(request, 'user/account-information.html', {'user_profile' : user_profile , 'friends' : friends})

@login_required(login_url='signin')
def profileLocation(request):
    user_profile = Profile.objects.get(user=request.user)
    
    location = get_location()
        

    lo = Location.objects.filter(user=user_profile.user.username)

    if len(lo) == 0:
        l = Location.objects.create(
            user = user_profile.user.username,
            city = location["city"],
            region= location["region"],
            country = location["country"],
            latitude = location["latitude"],
            longitude = location["longitude"]
        )
        user_profile.location = l 
        user_profile.save()
        l.save()
    else:
        loc = Location.objects.get(user=user_profile.user.username)      
        loc.city = location["city"]
        loc.region= location["region"]
        loc.country = location["country"]
        loc.latitude = location["latitude"]
        loc.longitude = location["longitude"]
        loc.save()
    ### friends 
    friends = get_friends(request.user.username)
    return render(request, 'user/account-information.html', {'user_profile' : user_profile , 'friends' : friends})







@login_required(login_url='signin')
def connect(request): 
    if request.method == 'POST':
        connecter = request.POST['connecter']
        connected = request.POST['connected']
        if request.POST.get('cancel'):
            if request.POST['cas']=="1":
                user_object = User.objects.get(username=connecter)
                prof = Profile.objects.get(user=user_object)  

                connection = Connection.objects.get(connecter=prof, connected=connected, verified=1) 
                connection.delete() 
            
                print("dadadd")
                return redirect('profile', pk=connected)
            elif request.POST['cas']=="2":
                user_object = User.objects.get(username=connecter)
                prof = Profile.objects.get(user=user_object)  

                connection = Connection.objects.get(connecter=prof, connected=connected, verified=2)
                connection.delete() 
                return redirect('profile', pk=connecter)


        elif request.POST.get('deleteReq'):
            user_object = User.objects.get(username=connecter)
            prof = Profile.objects.get(user=user_object)  

            connection = Connection.objects.get(connecter=prof, connected=connected, verified=1) 
            connection.delete() 
        
            print("dadadd")
            return redirect('profile', pk=connecter)        
        elif request.POST.get('delete'):
            user_object = User.objects.get(username=connecter)
            prof = Profile.objects.get(user=user_object)  

            connection = Connection.objects.get(connecter=prof, connected=connected, verified=2) 
            connection.delete() 
        
            print("dadadd")
            return redirect('profile', pk=connected)
        elif request.POST.get('accept'):
            user_object = User.objects.get(username=connecter)
            prof = Profile.objects.get(user=user_object)  

            connection = Connection.objects.get(connecter=prof, connected=connected, verified=1)
            connection.verified = 2
            connection.save()
            return redirect('profile', pk=connecter)

        elif request.POST.get('add'): 
            user_object = User.objects.get(username=connecter)
            prof = Profile.objects.get(user=user_object)  

            new_connection = Connection.objects.create(connecter=prof, connected=connected, verified=1 )
            new_connection.save()
            return redirect('profile', pk=connected)



######### REACTIONS
@login_required(login_url='signin')
def react(request, pk):
    pub = Pub.objects.get(id=pk)
    profile = Profile.objects.get(user=request.user) 
    if Reaction.objects.filter(pub = pub, reacter = profile).exists():  
        pub.no_of_likes -= 1
        pub.save()
 
        reaction = Reaction.objects.get( reacter=profile, pub=pub )
        reaction.delete()
    else:
        pub.no_of_likes += 1
        pub.save()

        
        reaction = Reaction.objects.create(reacter=profile, pub=pub )
        reaction.save() 
    #return render(request, 'feed/home.html', {'user_profile' : profile, 'posts' : posts, 'connection' : connection, 'companies' : companies , 'friends' : friends  })   

    #return redirect('post', pk=pk)

def checkReact(request, pk):
    pub = Pub.objects.get(id=pk) 
    return JsonResponse({"check": pub.no_of_likes}) 







############ POSTS

@login_required(login_url='signin')
def post(request, pk):
    pub = Pub.objects.filter(id=pk)
    user_profile = Profile.objects.get(user=request.user) 
    list = PostComment.objects.filter(pub=pk).order_by('-created_at')
    ##d = PostComment.objects.filter(pub=pub).order_by('-created_at')


    ### friends 
    friends = get_friends(request.user.username)
    return render(request, 'feed/post.html' , {'posts' : pub, 'comments' : list, 'user_profile' : user_profile, 'friends' : friends  })


@login_required(login_url='signin')
def delete_post(request, pk):
    pub = Pub.objects.get(id=pk)
    if pub.id_User == request.user:
        pub.delete()
    return redirect('index')


@login_required(login_url='signin')
def post_comment(request, pk):
    pub = Pub.objects.get(id=pk)
    
    user_profile = Profile.objects.get(user=request.user)
    if request.method=='POST':
        caption = request.POST['caption']
        comment = PostComment.objects.create(commenter=user_profile, pub=pub, desc = caption )
        comment.save()

        notification = Notification.objects.create(sender = user_profile, profile=pub.id_Profile.user.username, desc=" has commented on your post.")
        notification.save()
        pub.no_of_comments += 1
        pub.save()
    return redirect('post', pk=pk)










################ WORK
@login_required(login_url='signin')
def addWorkExp(request):
    user_profile = Profile.objects.get(user=request.user)
    

    if request.method == 'POST':
        id_company = request.POST['company'] 
        if Profile.objects.filter(name = id_company).exists():
            c = Profile.objects.get(name=id_company) 
            company = c.user.username
            companyName = c.name
            companyImage = c.profileimg
        else:
            company = ""
            companyName = id_company
            companyImage = 'blank_company_pic.jpg'
            
        start = request.POST['start']
        end = request.POST['end']
        task = request.POST['tasks']
        if start>end:
            messages.info(request,'Verify the start and end dates.')
            
        else:    
            workExp = WorkExperience.objects.create(worker=user_profile , company=company, task = task, start = start, end=end, companyName=companyName , companyImage =  companyImage)
            workExp.save()
            return redirect('allWorks')
    
    ### friends 
    friends = get_friends(request.user.username)
    return render(request, 'work/add_work_exp.html', {'user_profile' : user_profile, 'friends' : friends})
    

@login_required(login_url='signin')
def searchWorker(request):
    user_profile = Profile.objects.get(user=request.user)

    workers = Profile.objects.filter(type=1)

    ### friends 
    friends = get_friends(request.user.username)
    return render(request, 'job/default-job.html', {'user_profile' : user_profile, 'workers' : workers , 'friends' : friends})


@login_required(login_url='signin')
def allWorks(request):
    user_profile = Profile.objects.get(user=request.user) 
    ########### Work exp
    workExp = WorkExperience.objects.filter(worker = user_profile)

    ### friends 
    friends = get_friends(request.user.username)
    return render(request, 'work/all-works.html', {'user_profile' : user_profile , 'workExp' : workExp , 'friends' : friends})


@login_required(login_url='signin')
def editWork(request, pk):
    user_profile = Profile.objects.get(user=request.user)
    workExp = WorkExperience.objects.get(id = pk)    

    if request.method == 'POST':
        id_company = request.POST['company'] 
        if Profile.objects.filter(name = id_company).exists():
            c = Profile.objects.get(name=id_company) 
            company = c.user.username
            companyName = c.name
            companyImage = c.profileimg
        else:
            company = ""
            companyName = id_company
            companyImage = 'blank_company_pic.jpg'
            
        start = request.POST['start']
        end = request.POST['end']
        task = request.POST['tasks']
        if start>end:
            messages.info(request,'Verify the start and end dates.')
            
        else:    
            #workExp = WorkExperience.objects.create(worker=user_profile , company=company, task = task, start = start, end=end, companyName=companyName , companyImage =  companyImage)
            workExp.company = company
            workExp.task = task
            workExp.start = start
            workExp.end = end
            workExp.companyName = companyName
            workExp.companyImage = companyImage
            workExp.save()
            return redirect('allWorks')

    ### friends 
    friends = get_friends(request.user.username)
    return render(request, 'work/editWork.html', {'user_profile' : user_profile, 'work' : workExp , 'friends' : friends})


@login_required(login_url='signin')
def deleteWork(request, pk): 
    workExp = WorkExperience.objects.get(id = pk)    
    if workExp is not None:
        workExp.delete()
    return redirect('allWorks')


@login_required(login_url='signin')
def followCompany(request, pk):
    connecter = Profile.objects.get(user=request.user)
    connected = User.objects.get(username=pk)

    con = Connection.objects.filter(connecter=connecter, connected = pk, verified = 2)
    if len(con)==0:   
        connection = Connection.objects.create(connecter = connecter , connected = pk, verified=2)
        connection.save()
        company = Profile.objects.get(user=connected)
        company.no_of_followers += 1
        company.save() 
    else:
        connection = Connection.objects.get(connecter = connecter , connected = pk, verified=2)
        connection.delete()
        company = Profile.objects.get(user=connected)
        company.no_of_followers -= 1
        company.save() 
    return redirect('profile', pk = pk )











############# MESSAGES

@login_required(login_url='signin')
def inbox(request): 
    ### friends 
    friends = get_friends(request.user.username)
    user_profile = Profile.objects.get(user=request.user)
    messages = []
    for f in friends: 
        message = Message.objects.filter(Q(sender = f, receiver = request.user.username) | Q(sender = user_profile, receiver = f.user.username)).order_by('-created_at')[:2]
        messages.append(message)


    return render(request, 'message/inbox.html', {'user_profile' : user_profile,   'friends' : friends, 'messages' : messages})

@login_required(login_url='signin')
def message(request, pk):
    #receiver
    user_object = User.objects.get(username=pk)
    prof = Profile.objects.get(user=user_object)

    #connected user
    user_profile = Profile.objects.get(user=request.user)


    if request.method=="POST":
        message = Message.objects.create(sender = user_profile , receiver = pk, desc= request.POST['desc'])
        message.save()
    ### friends 
    friends = get_friends(request.user.username)

    
    messages = []
    messages1 = Message.objects.filter(sender = user_profile ,receiver = pk ) 
    messages2 = Message.objects.filter(sender = prof ,receiver = user_profile.user.username ) 
    for m in messages1:
        messages.append(m)
    for m in messages2:
        messages.append(m)  
    messages.sort(key=lambda x: x.created_at )
     
    return render(request, 'message/default-message.html', {'user_profile' : user_profile,   'friends' : friends, 'prof' : prof, 'messages' : messages})


@login_required(login_url='signin')
def verifyAccount(request): 
    ### friends 
    friends = get_friends(request.user.username)

    user_profile = Profile.objects.get(user=request.user)

    if request.method=="POST":
        if request.FILES.get('image')!=None: 
            image = request.FILES.get('image')
            verification =  Verification.objects.create(profile = user_profile , card=image )
            verification.save()
            messages.info(request,'Your verification request has been sumitted.')
        else:
           messages.info(request,'Make sure to submit an identity card.')
           return render(request, 'user/verify-account.html', {'user_profile' : user_profile,   'friends' : friends})
    return render(request, 'user/verify-account.html', {'user_profile' : user_profile,   'friends' : friends})


@login_required(login_url='signin')
def adminVerify(request): 
    ### friends 
    friends = get_friends(request.user.username)

    user_profile = Profile.objects.get(user=request.user)

    ###verifications
    preaccounts = Preaccount.objects.filter()

    return render(request, 'user/adminVerify.html', {'user_profile' : user_profile,   'friends' : friends, 'preaccounts' : preaccounts})


@login_required(login_url='signin')
def verifyRequest(request, pk): 
    ### friends 
    friends = get_friends(request.user.username)

    user_profile = Profile.objects.get(user=request.user)

    ###verifications
    preaccount = Preaccount.objects.get(id=pk)
    type = 1 
    profileimg ='blank_prof_pic.png'
    if preaccount.type=="company":
        type=2
        profileimg ='blank_company_pic.jpg'

    if request.method=="POST":
        
        profile = Profile.objects.create(
            user=preaccount.user,
            name=preaccount.name,
            surname=preaccount.surname,
            domaine=preaccount.field,
            sector=preaccount.sector,
            degree = preaccount.degree,
            cv = preaccount.cv,
            verified = 1,
            type=type,
            phone=preaccount.phone,
            birth=preaccount.birth,
            profileimg=profileimg
        )
        profile.save()
        preaccount.delete()
        return redirect('adminVerify')
    preaccount = Preaccount.objects.filter(id=pk)
    return render(request, 'user/verifyRequest.html', {'user_profile' : user_profile,   'friends' : friends, 'preaccount' : preaccount})

 
def become(request):  
    return render(request, 'user/become.html')

def info(request):  
    return render(request, 'user/info.html')

def getMessages(request, pk):
    #receiver
    user_object = User.objects.get(username=pk)
    prof = Profile.objects.get(user=user_object)

    #connected user
    user_profile = Profile.objects.get(user=request.user) 
    messages = []
    messages1 = Message.objects.filter(Q(sender = user_profile ,receiver = pk) | Q(sender = prof ,receiver = user_profile.user.username) ).order_by('created_at')
     
    return JsonResponse({"messages":list(messages1.values())})






## =========== VIDEO CHAT =================
def room(request, pk ):  
    ### friends 
    friends = get_friends(request.user.username)

    user_profile = Profile.objects.get(user=request.user)

    return render(request, 'meet/room.html' , {'user_profile' : user_profile,   'friends' : friends,   'chat' : 1, 'pk' : pk, 'notfications' : get_Notifications})

def meet(request):  
    ### friends 
    friends = get_friends(request.user.username)

    user_profile = Profile.objects.get(user=request.user)
 
    return render(request, 'meet/meet.html', {'user_profile' : user_profile,   'friends' : friends, 'notifications' : get_Notifications(request.user.username) })

def getToken(request):
    appId = "2d3c3684419e4f299f1f904f8181e3d9"
    appCertificate = "450fa743703a4116b1fe0bdaf5bf179d"
    channelName = request.GET.get('channel')
    uid = random.randint(1, 230)
    expirationTimeInSeconds = 3600
    currentTimeStamp = int(time.time())
    privilegeExpiredTs = currentTimeStamp + expirationTimeInSeconds
    role = 1

    token = RtcTokenBuilder.buildTokenWithUid(appId, appCertificate, channelName, uid, role, privilegeExpiredTs)

    return JsonResponse({'token': token, 'uid': uid}, safe=False)

@csrf_exempt
def createMember(request):
    data = json.loads(request.body)
    member, created = RoomMember.objects.get_or_create(
        name=data['name'],
        uid=data['UID'],
        room_name=data['room_name']
    )

    return JsonResponse({'name':data['name']}, safe=False)


def getMember(request):
    uid = request.GET.get('UID')
    room_name = request.GET.get('room_name')

    member = RoomMember.objects.get(
        uid=uid,
        room_name=room_name,
    )
    name = member.name
    return JsonResponse({'name':member.name}, safe=False)

@csrf_exempt
def deleteMember(request):
    data = json.loads(request.body)
    member = RoomMember.objects.get(
        name=data['name'],
        uid=data['UID'],
        room_name=data['room_name']
    )
    member.delete()
    return JsonResponse('Member deleted', safe=False)


def getFriend(request, pk): 
    user_profile = Profile.objects.get(user=request.user) 
    friends = Connection.objects.filter(Q(connecter = user_profile ) | Q(connected = request.user.username) ) 
     
    return JsonResponse({"friends":list(friends.values())})



@login_required(login_url='signin')
def inviteToMeet(request, pk):
    #receiver
    user_object = User.objects.get(username=pk)
    prof = Profile.objects.get(user=user_object)

    #connected user
    user_profile = Profile.objects.get(user=request.user)
    friends = Connection.objects.filter(Q(connecter = user_profile ) | Q(connected = request.user.username) ) 
    
    
    if request.method=="POST":
        desc = "Hello, join my meet : " +request.POST['meetName'] 
        message = Message.objects.create(sender = user_profile , receiver = pk, desc= desc)
        message.save()

        desc = " has invited you to his meeting room : " + request.POST['meetName'] + ""
        notification = Notification.objects.create(sender = user_profile , profile = pk , desc=desc  )
        notification.save()
    return render(request, 'meet/meet.html' , {'user_profile' : user_profile,   'friends' : friends, 'notfications' : get_Notifications})
    


######## JOB FILTERING 
@login_required(login_url='signin')
def jobFilter(request, pk): 
    ### friends 
    friends = get_friends(request.user.username)
    user_profile = Profile.objects.get(user=request.user)
    countries = Location.objects.order_by().values('country').distinct()


    if request.method=="POST":
        field = request.POST['field']
        sector = request.POST['sector']
        degree = request.POST['degree']
        country = request.POST['country']


        if pk == "experts":
            workers = Profile.objects.filter(domaine__contains=field, sector__contains = sector , degree__contains = degree, type = 1 )
        elif pk == "companies":
            workers = Profile.objects.filter(domaine__contains=field, sector__contains = sector , degree__contains = degree, type = 2 )

        return render(request, 'job/default-job.html', {'user_profile' : user_profile, 'workers' : workers , 'friends' : friends, 'country' : country , 'type' : pk})


    return render(request, 'job/jobFilter.html', {'user_profile' : user_profile,   'friends' : friends, 'countries' : countries , 'type' : pk })


@login_required(login_url='signin')
def search(request): 
    ### friends 
    friends = get_friends(request.user.username)
    user_profile = Profile.objects.get(user=request.user) 
 

    return render(request, 'job/search.html', {'user_profile' : user_profile,   'friends' : friends  })

@login_required(login_url='signin')
def allCompanies(request): 
    ### friends 
    friends = get_friends(request.user.username)
    user_profile = Profile.objects.get(user=request.user) 
 
    ##### companies
    companies = Profile.objects.filter(type=2)

    if request.method == "POST":
        search = request.POST["search"]
        
        companies = Profile.objects.filter(name__icontains=search, type=2)

    length = 0
    if len(companies) != 0:
        length = len(companies)
    return render(request, 'feed/all-companies.html', {'user_profile' : user_profile,   'friends' : friends, 'companies' : companies , 'len' : length })



        


############ Notification

# from django.shortcuts import render
# import tensorflow as tf
# import numpy as np
# from PIL import Image
# import io

# # Load your trained model
# model = tf.keras.models.load_model("vgg16_weights_tf_dim_ordering_tf_kernels_notop.h5")

# def predict_animal(request):
#     image = "animal.jpg"
#     image = Image.open(io.BytesIO(image.read()))
#     image = np.array(image) / 255.0
#     prediction = model.predict(image[np.newaxis, ...])
#     return render(request, 'predict.html', {'prediction': prediction})
 

from os.path import join
import numpy as np
from tensorflow.python.keras.applications.resnet50 import preprocess_input
from tensorflow.python.keras.preprocessing.image import load_img, img_to_array
from tensorflow.python.keras.applications import ResNet50

def predict_animal(request):
    return render(request, 'predict.html', {'prediction': 'dd'})



