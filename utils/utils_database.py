from Database.models import UserTab, EventTab, EventChannelTab
from django.apps import apps

def is_valid_event(event_id):
    check_event = list(EventTab.objects.filter(pk=event_id).values_list(flat=True))
    if not check_event:
        return False
    return True

def is_valid_user(user_id):
    check_user = list(UserTab.objects.filter(pk=user_id).values_list(flat=True))
    if not check_user:
        return False
    return True

def create_event_from_data(form):
    start_date = form.cleaned_data['start_date']
    end_date = form.cleaned_data['end_date']
    name = form.cleaned_data['name']
    description = form.cleaned_data['description']
    location = form.cleaned_data['location']
    status = form.cleaned_data['status']
    channel = form.cleaned_data['channel']
    # load database to update
    new_event = EventTab.objects.create(name=name, start_date=start_date,
                                        end_date=end_date, description=description,
                                        location=location, status=status)
    new_event.save()
    list_channel = set([int(x) for x in channel.split(',')])
    for item_id in list_channel:
        EventChannelTab.objects.create(channel_id=item_id, event_id=new_event.event_id)
    return True
