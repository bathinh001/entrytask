from Database.models import UserTab, EventTab

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
