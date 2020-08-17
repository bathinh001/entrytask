from __future__ import unicode_literals
from .models import *
from random import randint

list_channel = ['Music',
                'Visual Arts',
                'Performing Arts',
                'Film',
                'Lectures & Books',
                'Fashion',
                'Food & Drink',
                'Festivals & Fairs',
                'Charities',
                'Sports & Active Life',
                'Nightlife',
                'Kids & Family',
                'Flower',
                'LGBT',
                'Health',
                'Fan meeting',
                'Competition',
                'Politics',
                'Election',
                'Other']

#done
def create_channel():
    for i in range(len(list_channel)):
        channel = ChannelTab()
        channel.channel_id=i+1
        channel.name = list_channel[i]
        channel.save()


def create_participant():
    BATCH=100
    participant=[0]*BATCH
    for i in range(1,1000000):
        participant[i%BATCH]=ParticipantTab()
        participant[i%BATCH].status=1
        participant[i%BATCH].user_id=randint(0,1000000)
        participant[i%BATCH].event_id=randint(0,1000000)
        check=list(ParticipantTab.objects.filter(event_id=participant[i%BATCH].event_id, user_id=participant[i%BATCH].user_id).values())
        if i%BATCH==0:
            for j in range(BATCH):
                participant[j].save()
        if i%10000==0:
            print(i)

#done
import hashlib, uuid
import names
def create_user():
    for i in range(500000):
        user = UserTab()
        user.salt = uuid.uuid4().hex
        user.username = names.get_first_name()+'_'*randint(0,2)+str(randint(0,1000000))+names.get_last_name()
        user.password=hashlib.sha512(user.username + user.salt).hexdigest()
        user.fullname=names.get_full_name()
        user.type=1
        user.save()
        if (i%20000==0):
            print(i)

import time
from datetime import date

list_place=['Privet Drive',
            'Little Whinging',
            'Hogwarts School of Witchcraft and Wizardry',
            'The Leaky Cauldron',
            'Diagon Alley',
            'Ollivanders',
            'Gringotts',
            'Eyelops Owl Emporium',
            'Flourish & Blotts',
            'Florean Fourtesque Ice-Cream Parlor',
            'Zonko\'s Joke Shop',
            'Quality Quittich Supplies',
            'Twilfit & Tattlings',
            'Madam Malkin\'s Robes for all occasions',
            'Weasley Wizard Wheezes'
            'Platform 9 3/4',
            'Knocturn Alley',
            'Borgin & Burkes',
            'Hogsmeade',
            'The Three Broomsticks',
            'Madam Puddifoots',
            'Honey Dukes',
            'The Hog\'s Head Inn',
            'Shriven Shaft Quills',
            'The Chamber Of Secrets',
            'The Shrieking Shack',
            'The Room of Requirement',
            'The Forbidden Forest',
            'The Forest Of Dean',
            'The Burrow',
            'Shell Cottage']

#done
def create_event():
    for i in range(1000000):
        event=EventTab()
        event.name=names.get_full_name() + list_channel[randint(0,len(list_channel)-1)]
        event.start_date = int(time.mktime(date(2019,1,1).timetuple()))+randint(0, 10e8)
        event.end_date = event.start_date+randint(0, 10e6)
        event.description='The quick brown fox jumps over the lazy dog'
        event.location=list_place[randint(0,len(list_place)-1)]
        event.status=randint(0,4)
        event.save()
        if (i%20000==0):
            print(i)


#done
def create_like():
    for i in range(1000000):
        like=LikeTab()
        like.user_id=randint(0,500000)
        like.event_id=randint(0,100000)
        check=list(LikeTab.objects.filter(event_id=like.event_id, user_id=like.user_id).values())
        if check:
            continue
        like.status=randint(0,1)
        date=EventTab.objects.filter(event_id=like.event_id).values_list('start_date',flat=True)
        if not date:
            continue
        like.date=date[0]+randint(0, 10e5)
        like.status=randint(0,1)
        if (i%10000==0):
            print(i)
        like.save()


def create_comment():
    for i in range(1000000):
        cmt=CommentTab()
        cmt.user_id=randint(0,1000000)
        cmt.event_id=randint(0,1000000)
        check=list(CommentTab.objects.filter(event_id=cmt.event_id, user_id=cmt.user_id).values())
        if check:
            continue
        cmt.status=randint(0,1)
        date=EventTab.objects.filter(event_id=cmt.event_id).values_list('start_date',flat=True)
        if not date:
            continue
        cmt.date=date[0]+randint(0, 10e5)
        cmt.content='The quick brown fox jumps over the lazy dog'
        if (i%20000==0):
            print(i)
        cmt.save()

#done
def create_event_channel():
    for i in range(1000000):
        ec=EventChannelTab()
        ec.channel_id=randint(1, len(list_channel))
        ec.event_id=i+1
        check=list(EventChannelTab.objects.filter(event_id=ec.event_id, channel_id=ec.channel_id).values())
        if check:
            continue
        if (i%20000==0):
            print(i)
        ec.save()


#from Database.insert_func_db import *
#from Database.models import *
def edit_event_channel():
    ec=EventChannelTab.objects.all()
    l=len(ec)
    i=0
    while (i<l):
        channel_id=randint(0,12)
        if list(ec.filter(event_id=ec[i].event_id, channel_id=channel_id).values()):
            continue
        ec[i].channel_id=channel_id
        ec[i].save()
        print(i,ec[i].channel_id)
        i+=1
import csv
def printcsv():
    with open('datauser.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(["username", "password"])
        for i in range(500, 10000):
            user = UserTab()
            type = list(UserTab.objects.filter(user_id=i).values_list('type', flat=True))[0]
            if not type:
                continue
            username = list(UserTab.objects.filter(user_id=i).values_list('username', flat=True))[0]
            salt = list(UserTab.objects.filter(user_id=i).values_list('salt', flat=True))[0]
            writer.writerow([username, username+salt])
