from erp.admin import MainAdmin, PERYAdmin,  PERYAction
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from erp.admin.main import PERYActionCBV
from erp.utils.trip.models import Trip
from erp.utils.trip.views import TripBase

class PlanningTripAction(PERYActionCBV):
    title = _('edit trip')

    def action(self, request, object):
        print 'call trip action'

        # .as_view returns the view ...
        # redirect to the view
        return TripBase.as_view()(request, obj=object)


class TripAdmin(MainAdmin, PERYAdmin):
    '''
    Create an Admin Interface in Pery
    '''
    list_display = ['title', 'user']

    # Button on the interface to open the view which is
    # defined into the Action
    pery_actions = [PlanningTripAction, ]

admin.site.register(Trip, TripAdmin)