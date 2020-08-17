# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.apps import apps
from django.http import JsonResponse
import json
from django.http import HttpResponse
from jsonschema import validate
from utils.utils_authentication import authorization
# Create your views here.

def view_user_activity(request):
    # Authorization
    auth = authorization(request)
    if auth['status'] >= 400:
        return HttpResponse(content=auth['message'], status=auth['status'])

    # schema request body
    schema = {
        "type": "object",
        "description": "Structure of a body request to view user activities by ID",
        "properties": {
            "user_id": {
                "description": "The unique identifier for user",
                "type": "number",
                "exclusiveMinimum": 0
            }
        },
        "maxProperties": 1,
        "required": ["user_id"]
    }

    # validate the request body
    try:
        validate(instance=json.loads(request.body), schema=schema)
    except:
        return HttpResponse("Error Validation of JSON schema in request body", status=400)

    # load data
    user_id = json.loads(request.body)['user_id']
    # load model
    user = apps.get_model('Database', 'UserTab')
    participation = apps.get_model('Database', 'ParticipantTab')
    like = apps.get_model('Database', 'LikeTab')
    cmt = apps.get_model('Database', 'CommentTab')
    event = apps.get_model('Database', 'EventTab')
    res = {'status': 0, 'result': {}}

    # query user information
    data_user = list(user.objects.filter(user_id=user_id).values('username', 'fullname'))
    if not data_user:
        res['status'] = 1
        return JsonResponse(res, status=200)
    res['result']['user'] = data_user[0]

    # query user like activity
    data_event_id_in_like = list(like.objects.filter(user_id=user_id, status=1).values_list('event_id', flat=True))
    data_event_name_in_like = list(event.objects.filter(event_id__in=data_event_id_in_like).values_list('name', flat=True))
    data_like=[]
    for i in range(len(data_event_id_in_like)):
        data = {'event_id': data_event_id_in_like[i], 'event_name': data_event_name_in_like[i]}
        data_like.append(data)
    res['result']['like'] = data_like

    # query user comment activity
    data_event_id_in_cmt = list(cmt.objects.filter(user_id=user_id).values_list('event_id', flat=True))
    data_event_name_in_cmt = list(event.objects.filter(event_id__in=data_event_id_in_cmt).values_list('name', flat=True))
    data_content_in_cmt = list(cmt.objects.filter(user_id=user_id).values_list('content', flat=True))
    data_cmt=[]
    for i in range(len(data_event_id_in_cmt)):
        data = {'event_id': data_event_id_in_cmt[i], 'event_name': data_event_name_in_cmt[i], 'content': data_content_in_cmt[i]}
        data_cmt.append(data)
    res['result']['comment'] = data_cmt

    # query user event activity
    data_event_id_in_participation = list(participation.objects.filter(user_id=user_id).values_list('event_id', flat=True))
    data_event_in_participation = list(event.objects.filter(event_id__in=data_event_id_in_participation).values('event_id', 'name', 'end_date', 'start_date'))
    res['result']['event'] = list(data_event_in_participation)

    return JsonResponse(res, status=200)

