# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import EventTab, UserTab, EventChannelTab
# Register your models here.
admin.site.register(EventTab)
admin.site.register(EventChannelTab)
admin.site.register(UserTab)
