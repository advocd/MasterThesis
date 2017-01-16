from django.http import HttpResponse, HttpResponseRedirect

from erp.models import PartnerAddress, Partner, Invoice
from erp.utils.gis.pery_map import PERYMap, PeryTripList, PERYMapList
from erp.utils.trip.models import TripStation, PeryDataRank

from erp.views import PERYMapTodo
from pery_interface.response import PERYAjaxResponse2
from pery_interface.views import PERYCBView
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
import json

class PERYMapTrip(PERYMap):
    '''
    This class inherits from the PERYMap. It could used to
    change or redesign the functionality of the default map class.
    '''
    def get_data(self):
        pass


class TripBase(PERYCBView):
    '''
    The TripBase is called from the Django admin at the moment if a
    user click on "edit map". Here will be gathered and prepared the
    needed data and also the visualisation will be defined.

    Procedure:
        Case I: come from admin:
            1. call: prepare()
            2. call: render_output()
                :return rendered html as response

        Case II: Action was called:
            1. call: the action
            2. call: prepare()
            3. call: render_output()
                :return rendered html as response
    '''

    # deactivate automatic http redirect afte execute a action
    redirect_after_action = False

    # define the available ranks and decide which models should be used
    available_ranks = {
        'total_turnover': PeryDataRank('total turnover', 'partner', 'sales_total_turnover'),
        'last_year_turnover': PeryDataRank('last year turnover', 'partner', 'sales_last_year_turnover'),
        'last_invoice': PeryDataRank('last invoice', 'partner', 'sales_last_invoice', sort_inverse=True),
        'last_visit': PeryDataRank('last visit', 'partner', 'sales_last_visit', sort_inverse=True)
    }

    def get_active_rank_from_user(self, request):
        parameters = json.loads(request.user.profile.parameters or '{}')
        user_rank = parameters.get('map_active_rank', '')

        if user_rank in self.available_ranks:
                return user_rank
        return None

    def prepare(self, request):
        # get the primary key of the Trip model
        self.obj = self.kwargs.get('obj')

        # activate ajax support
        self.ajax_refresh_list = []
        self.ajax_response = PERYAjaxResponse2(request)

    def ajax_refresh(self, name):
        # add new ajax action to the ajax queue
        if not name in self.ajax_refresh_list:
            self.ajax_refresh_list.append(name)

    def render_output(self, request):
        '''
        this function render the output for the given
        arguments of the request.
        :param request: user request
        :return: a response
        '''

        # switch for the presentation mode (e.g. map or list)
        presantation_mode = request.session.get('perymap_presentation_mode', 'peryMap')
        my_presantation = None
        my_map = None
        my_list = None
        trip_stations = TripStation.objects.filter(parent=self.obj)
        self.active_rank = request.session.get('pery_map_active_rank', 'total_turnover')
        trip_station_dict = {x.address.pk: x.ordering for x in trip_stations}

        if presantation_mode == 'peryMap':

            #prepare map view here
            my_map = PERYMapTrip(request)

            my_map.active_rank = self.active_rank
            my_map.available_ranks = self.available_ranks
            addresses = PartnerAddress.objects.select_related('partner').filter(geo_lat__isnull=False, geo_lon__isnull=False)

            # define ranks for partner data
            min_val, max_val = self.available_ranks.get(self.active_rank).get_aggregated_min_max(addresses)
            my_map.set_rank_range(min_val, max_val, 5)

            # add points to map
            for addr in addresses:
                num = trip_station_dict.get(addr.pk, None)
                my_map.add_point(
                    lon=addr.geo_lon,
                    lat=addr.geo_lat,
                    id=addr.pk,
                    number=num,
                    popup=render_to_string('admin/erp/trip/popup.html', {'addr': addr, 'number':num}),

                    # get rank value from active_rank
                    rank_value = self.available_ranks.get(self.active_rank).get_value_from_attr(addr.partner),
                )

                # set map as presentation
                my_presantation = my_map

        elif presantation_mode == 'peryMapList':

            #prepare list view here
            addresses = PartnerAddress.objects.select_related('partner').filter(geo_lat__isnull=False, geo_lon__isnull=False)
            my_list = PERYMapList(request, template="admin/erp/trip/list_view.html")

            # add points to list
            for address in addresses:
                address.pery_map_trip_number = trip_station_dict.get(address.pk, None)
                my_list.table_data.append(address)

            # set list as presentation
            my_presantation = my_list

        # check if something in the ajax queue
        if self.ajax_refresh_list:
            # render only parts (ajax)
            for item in self.ajax_refresh_list:
                # check which ajax job is in the queue and add the job result to the ajax response
                if item == 'planninglist':
                    self.ajax_response.refresh('#planninglist', self.render_to_string('admin/erp/trip/planning_list.html', locals()))

                elif item.startswith('popup-'):
                    item = int(item[6:])
                    popup_addr = addresses.get(pk=item)
                    popup_num = trip_station_dict.get(item, None)
                    self.ajax_response.refresh('#popup-content-%s' %item, self.render_to_string('admin/erp/trip/popup.html', {'addr': popup_addr, 'number': popup_num}))

                elif item == 'listview':
                    self.ajax_response.refresh('#display-content', my_list.render())

                elif item == 'changeRanks':
                    self.ajax_response.refresh('#display-content', my_map.render())


        if self.ajax_response.is_in_use():
            # render the done ajax job's and return it as response to the webserver
            return self.ajax_response.render()

        # render the base template and return it as response to the webserver
        return self.render_to_response('admin/erp/trip/planning2.html', locals())

    def action_change_rank(self, request):
        '''
        Is used for a action which is raised by the user in the web browser.
        This will change the active rank to the given value from the request
        '''
        new_rank = request.GET.get('name')
        if new_rank in self.available_ranks:
            request.session['pery_map_active_rank'] = new_rank
            self.active_rank = new_rank

        self.ajax_refresh_list.append('changeRanks')
        self.ajax_response.run_js_function('resizePeryMap')

    def action_add_to_list(self, request):
        '''
        Is used for a action which is raised by the user in the web browser.
        This will add an element to the Trip. Will be used in the map and list view
        '''

        pk = request.GET.get('pk')
        addr = PartnerAddress.objects.get(pk=pk)
        if not TripStation.objects.filter(address=addr, parent=self.obj).exists():
            obj = TripStation()
            obj.address = addr
            obj.partner = addr.partner
            obj.parent = self.obj
            obj.save()

        # update the "Trip List" via ajax
        self.ajax_refresh_list.append('planninglist')

        # get the current presantation_mode from the request
        presantation_mode = request.session.get('perymap_presentation_mode', None)

        # push the needed ajax job's to the queue
        if presantation_mode == 'peryMapList':
            self.ajax_refresh_list.append('listview')
        else:
            self.ajax_refresh_list.append('popup-%s' %pk )
            self.ajax_response.run_js_function('updateNumbers', self.obj.get_ordered_tripstations_pk())

    def action_remove_from_list(self, request):
        '''
        Is used for a action which is raised by the user in the web browser.
        This will remove an element to the Trip. Will be used in the map and list view
        '''
        pk = request.GET.get('pk')
        self.obj.remove_tripstation_by_addr(pk)
        self.ajax_refresh_list.append('planninglist')

        # get the current presantation_mode from the request
        presantation_mode = request.session.get('perymap_presentation_mode', None)

        # push the needed ajax job's to the queue
        if presantation_mode == 'peryMapList':
            self.ajax_refresh_list.append('listview')
        else:
            self.ajax_refresh_list.append('popup-%s' %pk)
            self.ajax_response.run_js_function('updateNumbers', self.obj.get_ordered_tripstations_pk())

    def action_save_map_data(self, request):
        '''
        Is used for a action which is raised by the user in the web browser.
        Is used to update the user profile with the new map data (e.g. position, zoom, etc.)
        '''
        map_state = request.GET.get('mapState')
        if 'lat' in map_state and 'lng' in map_state and 'zoom' in map_state:
            request.user.profile.pery_map_data = map_state
            request.user.profile.save()

    def action_get_map_view(self, request):
        '''
        Is used for a action which is raised by the user in the web browser.
        This action will switch the presentation mode to "map view"
        '''
        request.session['perymap_presentation_mode'] = 'peryMap'
        return HttpResponseRedirect(request.path)

    def action_get_list_view(self, request):
        '''
        Is used for a action which is raised by the user in the web browser.
        This action will switch the presentation mode to "list view"
        '''
        request.session['perymap_presentation_mode'] = 'peryMapList'
        return HttpResponseRedirect(request.path)
