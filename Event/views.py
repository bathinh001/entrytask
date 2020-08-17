# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.apps import apps
from django.http import JsonResponse
import json
from django.http import HttpResponse
from jsonschema import validate
import sys
from utils.utils_authentication import authorization
from utils.utils_database import *
from django.shortcuts import render
import time
from django.views.decorators.csrf import csrf_exempt
from home.forms import CreateEventForm
from django.core.cache import cache
# Create your views here.
############################################GET########################################################


def view_event(request):
    # Authorization
    auth = authorization(request)
    if auth['status'] >= 400:
        return HttpResponse(content=auth['message'], status=auth['status'])


    # validate the request body
    schema = {
        "type": "object",
        "description": "Structure of a body request to view event by ID",
        "properties": {
            "event_id": {
                "description": "The unique identifier for event",
                "type": "number",
                "exclusiveMinimum": 0
            }
        },
        "maxProperties": 1,
        "required": ["event_id"]
    }
    try:
        validate(instance=json.loads(request.body), schema=schema)
    except:
        return HttpResponse("Validation Error in JSON schema", status=400)


    # load model
    event = apps.get_model('Database', 'EventTab')
    event_channel = apps.get_model('Database', 'EventChannelTab')
    like = apps.get_model('Database', 'LikeTab')
    participation = apps.get_model('Database', 'ParticipantTab')


    # query
    res = {'status': 0, 'result': {}}
    event_id = json.loads(request.body)['event_id']
    data = list(event.objects.filter(event_id=event_id).values())
    if not data:
        res['status'] = 1
        return JsonResponse(res, status=200)
    channel = list(event_channel.objects.filter(event_id=event_id).values_list('channel_id', flat=True))
    user_id = auth.get('user_id', None)

    like = list(like.objects.filter(event_id=event_id, user_id=user_id).values_list('status', flat=True))
    like_status = 1
    if not like or like[0]==0:
        like_status = 0

    participation = list(participation.objects.filter(event_id=event_id, user_id=user_id).values_list('status', flat=True))
    participation_status = 1
    if not participation or participation[0] == 0:
        participation_status = 0
    # save result
    data[0]['channel'] = channel
    data[0]['like_status'] = like_status
    data[0]['participation_status'] = participation_status
    res['result'] = data[0]
    return JsonResponse(res, status=200)
#######################################################################################################


def view_list_event(request):
    # Authorization
    auth = authorization(request)
    if auth['status'] >= 400:
        return HttpResponse(content=auth['message'], status=auth['status'])

    schema = {
        "type": "object",
        "description": "Structure of a body request to view list of event by certain fields",
        "minProperties": 2,
        "maxProperties": 5,
        "properties": {
            "start_date": {
                "type": "number",
                "exclusiveMinimum" : 0
            },
            "end_date": {
                "type": "number",
                "exclusiveMinimum": 0
            },
            "channel": {
                "description": "The unique identifier for event",
                "type": "array",
                "items": {
                    "type": "number",
                    "exclusiveMinimum": 0,
                    "uniqueItems": True
                },
            },
            "limit": {
                "type": "number",
                "exclusiveMinimum": 0
            },
            "page": {
                "type": "number",
                "exclusiveMinimum": 0
            },
        },
        "required": ["limit", "page"]
    }
    # validate the request body
    try:
        validate(instance=json.loads(request.body), schema=schema)
    except:
        return HttpResponse("Validation Error in JSON schema", status=400)
    # load model
    event = apps.get_model('Database', 'EventTab')
    event_channel = apps.get_model('Database', 'EventChannelTab')
    # load parameters
    res = {'status': 0, 'result': []}
    data = json.loads(request.body)
    limit = int(data['limit'])
    page = int(data['page'])
    end_date = data.get('end_date', 0)
    start_date = data.get('start_date', sys.maxint)
    channel = data.get('channel', [])
    # query
    start = (page - 1) * limit
    list_event_id_final = []
    if not channel:
        list_event_id_final.extend(
            list(event.objects.filter(end_date__gte=end_date, start_date__lte=start_date).only('event_id').values_list(flat=True)[start:start+limit])
        )
    else:
        while True:
            list_event_id = list(event.objects.filter(end_date__gte=end_date, start_date__lte=start_date).only('event_id').values_list(flat=True)[start:start+limit])
            if not len(list_event_id):
                break
            list_event_id_final.extend(
                list(event_channel.objects.filter(event_id__in=list_event_id, channel_id__in=channel).only('event_id').values_list(flat=True).distinct())
            )
            if len(list_event_id_final) >= limit:
                break
            start += limit
    if not list_event_id_final:
        res['status']=1
    else:
        list_event_id_final = list_event_id_final[:limit]
        result = list(event.objects.filter(event_id__in=list_event_id_final).values('event_id', 'name', 'start_date', 'end_date'))
        res['result'] = result
    return JsonResponse(res, status=200)
#######################################################################################################


def view_list_participant(request):
    # Authorization
    auth = authorization(request)
    if auth['status'] >= 400:
        return HttpResponse(content=auth['message'], status=auth['status'])

    schema = {
        "type": "object",
        "description": "Structure of a body request to view list of participants in an event",
        "maxProperties": 3,
        "properties": {
            "event_id": {
                "description": "The unique identifier for event",
                "type": "number",
                "exclusiveMinimum": 0
            },
            "limit": {
                "type": "number",
                "exclusiveMinimum": 0
            },
            "page": {
                "type": "number",
                "exclusiveMinimum": 0
            },
        },
        "required": ["event_id", "limit", "page"]
    }
    # validate the request body
    try:
        validate(instance=json.loads(request.body), schema=schema)
    except:
        return HttpResponse("Validation Error in JSON schema", status=400)
    # load model
    user = apps.get_model('Database', 'UserTab')
    participant = apps.get_model('Database', 'ParticipantTab')
    data = json.loads(request.body)

    res = {'status': 0, 'result': {}}
    event_id = data['event_id']

    # get parameter
    limit = data['limit']
    page = data['page']
    start = (page-1)*limit

    # query
    list_user_id = list(participant.objects.filter(event_id=event_id, status=1).values_list('user_id', flat=True)[start:start + limit])
    if not list_user_id:
        res['status']=1
    else:
        result = {}
        result['count_participant'] = len(list_user_id)
        list_username = list(user.objects.filter(user_id__in=list_user_id).values_list('username', flat=True))
        result['username'] = list_username
        res['result'] = result
    return JsonResponse(res, status=200)
#######################################################################################################


def view_list_like(request):
    # Authorization
    auth = authorization(request)
    if auth['status'] >= 400:
        return HttpResponse(content=auth['message'], status=auth['status'])

    schema = {
        "type": "object",
        "description": "Structure of a body request to view list of participants in an event",
        "maxProperties": 3,
        "properties": {
            "event_id": {
                "description": "The unique identifier for event",
                "type": "number",
                "exclusiveMinimum": 0
            },
            "limit": {
                "type": "number",
                "exclusiveMinimum": 0
            },
            "page": {
                "type": "number",
                "exclusiveMinimum": 0
            },
        },
        "required": ["event_id", "limit", "page"]
    }
    # validate the request body
    try:
        validate(instance=json.loads(request.body), schema=schema)
    except:
        return HttpResponse("Validation Error in JSON schema", status=400)
    # load model
    user = apps.get_model('Database', 'UserTab')
    like = apps.get_model('Database', 'LikeTab')

    res = {'status': 0, 'result': {}}
    data = json.loads(request.body)

    # get parameter
    event_id = data['event_id']
    limit = data['limit']
    page = data['page']
    start = (page-1)*limit

    # query
    list_user_id = list(like.objects.filter(event_id=event_id, status=1).values_list('user_id', flat=True)[start:start+limit])
    if not list_user_id:
        res['status']=1
    else:
        result = {}
        result['count_like'] = len(list_user_id)
        list_username = list(user.objects.filter(user_id__in=list_user_id).values_list('username', flat=True))
        result['username'] = list_username
        res['result'] = result
    return JsonResponse(res, status=200)
#######################################################################################################


def view_list_comment(request):
    # Authorization
    auth = authorization(request)
    if auth['status'] >= 400:
        return HttpResponse(content=auth['message'], status=auth['status'])


    schema = {
        "type": "object",
        "description": "Structure of a body request to view list of participants in an event",
        "maxProperties": 3,
        "properties": {
            "event_id": {
                "description": "The unique identifier for event",
                "type": "number",
                "exclusiveMinimum": 0
            },
            "limit": {
                "type": "number",
                "exclusiveMinimum": 0
            },
            "page": {
                "type": "number",
                "exclusiveMinimum": 0
            },
        },
        "required": ["event_id", "limit", "page"]
    }
    # validate the request body
    try:
        validate(instance=json.loads(request.body), schema=schema)
    except:
        return HttpResponse("Validation Error in JSON schema", status=400)
    # load model
    user = apps.get_model('Database', 'UserTab')
    comment = apps.get_model('Database', 'CommentTab')

    res = {'status': 0, 'result': {}}
    data = json.loads(request.body)

    # get parameter
    event_id = data['event_id']
    limit = data['limit']
    page = data['page']
    start = (page-1)*limit

    # query
    list_comment_result = list(comment.objects.filter(event_id=event_id).values('comment_id', 'user_id', 'content')[start: start+limit])
    if not list_comment_result:
        res['status'] = 1
    else:
        list_user_id = [data['user_id'] for data in list_comment_result]
        result = {}
        result['count_comment'] = len(list_comment_result)
        list_username = list(user.objects.filter(user_id__in=list_user_id).values_list('username',flat=True))
        for i in range(len(list_comment_result)):
            list_comment_result[i].pop('user_id', None)
            list_comment_result[i]['username'] = list_username[i]

        result['comment'] = list_comment_result
        res['result']= result
    return JsonResponse(res, status=200)
#######################################################################################################


############################################POST#######################################################


def like_action(request):
    # Authorization
    auth = authorization(request)
    if auth['status'] >= 400:
        return HttpResponse(content=auth['message'], status=auth['status'])

    schema = {
        "type": "object",
        "description": "Structure of a body request to make like action",
        "maxProperties": 2,
        "properties": {
            "event_id": {
                "description": "The unique identifier for event",
                "type": "number",
                "exclusiveMinimum": 0,
            },
            "flag": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
            },
        },
        "required": ["event_id", "flag"]
    }
    # validate the request body
    try:
        validate(instance=json.loads(request.body), schema=schema)
    except:
        return HttpResponse("Validation Error in JSON schema", status=400)
    # load model
    like = apps.get_model('Database', 'LikeTab')
    event = apps.get_model('Database', 'EventTab')
    res = {'status': 0, 'result': {}}

    data = json.loads(request.body)

    # get parameter
    status = data.get('flag', None)
    event_id = data.get('event_id', None)
    user_id = auth.get('user_id', None)
    # query
    if not is_valid_event(event_id) or not is_valid_user(user_id):
        res['status']=1
        return JsonResponse(res, status=400)
    else:
        obj = like.objects.update_or_create(event_id=event_id, user_id=user_id, defaults={'date': int(time.time()), 'status': ((status+1) % 2)})
        like_id = list(like.objects.filter(event_id=event_id, user_id=user_id).values_list(flat=True))[0]
        count = len(like.objects.filter(event_id=event_id, status=1).values_list(flat=True))
        result = {'like_id': like_id, 'count_like': count}
        res['result'] = result
    return JsonResponse(res, status=201)


def comment_action(request):
    # Authorization
    auth = authorization(request)
    if auth['status'] >= 400:
        return HttpResponse(content=auth['message'], status=auth['status'])

    schema = {
        "type": "object",
        "description": "Structure of a body request to make comment action",
        "maxProperties": 2,
        "properties": {
            "event_id": {
                "description": "The unique identifier for event",
                "type": "number",
                "exclusiveMinimum": 0,
            },
            "content": {
                "type": "string",
                "maxLength": 1000
            },
        },
        "required": ["event_id", "content"]
    }
    # validate the request body
    try:
        validate(instance=json.loads(request.body), schema=schema)
    except:
        return HttpResponse("Validation Error in JSON schema", status=400)

    # load model
    comment = apps.get_model('Database', 'CommentTab')
    event = apps.get_model('Database', 'EventTab')
    res = {'status': 0, 'result': {}}

    data = json.loads(request.body)

    # get parameter
    event_id = data.get('event_id', None)
    user_id = auth.get('user_id', None)
    content = data.get('content', None)

    # query
    if not is_valid_event(event_id) or not is_valid_user(user_id):
        res['status'] = 1
        return JsonResponse(res, status=201)
    else:
        obj = comment.objects.update_or_create(event_id=event_id, user_id=user_id, defaults={'date': int(time.time()), 'content': content})
        cmt_id = list(comment.objects.filter(event_id=event_id, user_id=user_id).values_list(flat=True))[0]
        count = len(comment.objects.filter(event_id=event_id).values_list(flat=True))
        result = {'comment_id': cmt_id, 'count_comment': count}
        res['result'] = result
    return JsonResponse(res, status=201)


def participate_action(request):
    # Authorization
    auth = authorization(request)
    if auth['status'] >= 400:
        return HttpResponse(content=auth['message'], status=auth['status'])

    schema = {
        "type": "object",
        "description": "Structure of a body request to make participate action",
        "maxProperties": 2,
        "properties": {
            "event_id": {
                "description": "The unique identifier for event",
                "type": "number",
                "exclusiveMinimum": 0,
            },
            "flag": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
            },
        },
        "required": ["event_id", "flag"]
    }
    # validate the request body
    try:
        validate(instance=json.loads(request.body), schema=schema)
    except:
        return HttpResponse("Validation Error in JSON schema", status=400)
    # load model
    participant = apps.get_model('Database', 'ParticipantTab')
    res = {'status': 0, 'result': {}}

    data = json.loads(request.body)

    # get parameter
    status = data.get('flag', None)
    event_id = data.get('event_id', None)
    user_id = auth.get('user_id', None)
    # query
    if not is_valid_event(event_id) or not is_valid_user(user_id):
        res['status'] = 1
        return JsonResponse(res, status=400)
    else:
        obj = participant.objects.update_or_create(event_id=event_id, user_id=user_id, defaults={'status': ((status+1) % 2)})
        participant_id = list(participant.objects.filter(event_id=event_id, user_id=user_id).values_list(flat=True))[0]
        count = len(participant.objects.filter(event_id=event_id, status=1).values_list(flat=True))
        result = {'participant_id': participant_id, 'count_participant': count}
        res['result'] = result
    return JsonResponse(res, status=201)


@csrf_exempt
def create_event(request):
    # Authorization
    auth = authorization(request)
    if auth['status'] >= 400:
        return HttpResponse(content=auth['message'], status=auth['status'])
    if auth['type'] == 1:
        return HttpResponse('You don\'t have permission to access', status=403)
    if request.method == "POST":
        form = CreateEventForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            location = form.cleaned_data['location']
            status = form.cleaned_data['status']
            channel = form.cleaned_data['channel']
            # load database to update
            event_channel = apps.get_model('Database', 'EventChannelTab')
            event = apps.get_model('Database', 'EventTab')
            new_event = event.objects.create(name=name, start_date=start_date,
                                             end_date=end_date, description=description,
                                             location=location, status=status)
            new_event.save()
            list_channel = set([int(x) for x in channel.split(',')])
            for item_id in list_channel:
                event_channel.objects.create(channel_id=item_id, event_id=new_event.event_id)
    form = CreateEventForm()
    return render(request, 'login.html', {'form': form})
'''
def update_event(request):
    # Authorization
    auth = authorization(request)
    if auth['status'] >= 400:
        return HttpResponse(content=auth['message'], status=auth['status'])
    user_id = auth['user_id']
    type = auth['type']
    if type!=0:
        
    schema = {
        "type": "object",
        "description": "Structure of a body request to update event",
        "maxProperties": 8,
        "properties": {
            "event_id": {
                "description": "The unique identifier for event",
                "type": "number",
                "exclusiveMinimum": 0,
            },
            "name": {
                "type": "string",
                "maxLength": 100
            },
            "start_date": {
                "type": "number",
                "exclusiveMinimum": 0
            },
            "end_date": {
                "type": "number",
                "exclusiveMinimum": 0
            },
            "channel": {
                "type": "array",
                "items": {
                    "type": "number",
                    "exclusiveMinimum": 0,
                    "uniqueItems": True
                },
            },
            "location": {
                "type": "string",
                "maxLength": 100
            },
            "description": {
                "type": "string",
                "maxLength": 1000
            },
            "status": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
            },
        },
        "required": ["event_id"]
    }
    # validate the request body
    try:
        validate(instance=json.loads(request.body), schema=schema)
    except:
        return HttpResponse("Validation Error in JSON schema", status=400)
    
    
    # load model
    event = apps.get_model('Database', 'EventTab')
    event_channel = apps.get_model('Database', 'EventChannelTab')
    

    # query
    res = {'status': 0, 'result': {}}
    event_id = json.loads(request.body)['event_id']
    data = list(event.objects.filter(event_id=event_id).values())
'''
#######################################################################################################


############################################COMBINE####################################################


@csrf_exempt
def event_like(request):
    if request.method == 'GET':
        return view_list_like(request)
    if request.method == 'POST':
        return like_action(request)
    else:
        return HttpResponse('Welcome', status=200)


@csrf_exempt
def event_comment(request):
    if request.method == 'GET':
        return view_list_comment(request)
    if request.method == 'POST':
        return comment_action(request)
    else:
        return HttpResponse('Welcome', status=200)


@csrf_exempt
def event_participant(request):
    if request.method == 'GET':
        return view_list_participant(request)
    if request.method == 'POST':
        return participate_action(request)
    else:
        return HttpResponse('Welcome', status=200)
