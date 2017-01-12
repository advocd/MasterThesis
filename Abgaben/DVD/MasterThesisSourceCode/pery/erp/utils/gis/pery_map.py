from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.conf import settings
import datetime


def get_pery_map_color(color_name):
    '''
    Get the defined rgb codes by color name
    :param color_name: String
    :return: String
    '''
    if not color_name.startswith('#'):
            if not settings.PERY_MAP_COLOR.get(color_name):
                raise Exception('PERY_MAP_COLOR not found')

            return settings.PERY_MAP_COLOR.get(color_name)
    else:
        return color_name


class PERYMapPoint():
    '''
    This class describes the Map Points (e.g. Partner) which should be
    placed on the map
    '''
    ICON_LIST = ['point']
    COLOR_CHOICES = (
        ('default', _('default')),
        ('blue', _('blue')),
        ('red', _('red')),
    )

    def __init__(self, lon, lat, id, popup=None, number=0, icon='point', color='default', rank=None, rank_value=None, ):
        self.lon = lon
        self.lat = lat
        self.popup = popup
        self.number = number
        self.icon = icon
        self.id = id
        self.is_many = False
        self.rank = rank
        self.rank_value = rank_value
        self.set_color(color)

    def set_color(self, color):
        self.color = get_pery_map_color(color)

    def change_icon_to_many(self):
        self.icon += '_many'

    def get_path(self):
        '''
        Get the svg path for the map icon
        :return: String e.g. '/static/erp/img/map/%s/%s.png' % (self.icon, self.color)
        '''
        if self.is_many:
            return '<path fill="%s" d="M 320,160 A 160,160 0 0 1 160,320 160,160 0 0 1 0,160 160,160 0 0 1 160,0 160,160 0 0 1 320,160 Z" id="pin"/><path fill="#fefefe" d="M 151.98528,255.21335 C 136.44585,253.93918 120.38405,248.19276 106.78081,239.04058 63.485992,209.91209 51.642102,151.56256 80.123342,107.71127 94.127862,86.14914 116.4676,71.02018 141.8294,65.92256 c 8.34982,-1.67827 23.16289,-2.06608 31.60587,-0.82744 21.18466,3.10793 39.12975,12.03981 54.22606,26.99012 14.22323,14.08569 23.6131,32.09175 27.09557,51.95857 1.14285,6.51975 1.27309,24.42238 0.221,30.37932 -4.82976,27.34609 -19.24437,49.9644 -41.3006,64.80573 -13.49969,9.08376 -29.43353,14.63522 -45.92887,16.00192 -7.06324,0.58523 -8.43179,0.58371 -15.76315,-0.0175 l 0,3e-5 z" id="hole"/>' %self.color

        return '<path fill="%s" d="M 160.26597,0.21528105 C 71.906969,0.21528105 0.26596625,71.840284 0.26596625,160.21528 c 0,24.75 5.62487475,48.219 15.67187575,69.125 0.562,1.188 144.328128,282.875 144.328128,282.875 l 142.59375,-279.375 c 11.125,-21.781 17.40625,-46.469 17.40625,-72.625 0,-88.374996 -71.625,-159.99999895 -160,-159.99999895 z m 0,63.99999895 c 53,0 96,43 96,96 0,53 -43,96 -96,96 -53.016,0 -96.000003,-43 -96.000003,-96 0,-53 42.984003,-96 96.000003,-96 z" id="pin"/><path fill="#fefefe" d="M 151.25026,255.6425 C 129.20265,253.34766 109.55451,244.24267 93.811453,229.02523 77.523856,213.28144 67.399325,192.7037 64.980166,170.42671 c -0.988415,-9.1019 -0.265456,-21.93923 1.743508,-30.95887 3.053447,-13.70906 10.340697,-28.80504 19.05025,-39.46375 12.793461,-15.656593 30.581956,-27.260377 49.448136,-32.255996 17.26962,-4.572861 34.93737,-4.398419 51.91821,0.512613 22.33044,6.458192 42.02011,21.468997 54.63402,41.651313 5.12285,8.19657 9.85697,19.8311 12.01611,29.53069 2.04206,9.17357 2.75567,21.77089 1.75517,30.984 -2.41968,22.28186 -12.54314,42.85421 -28.83987,58.60682 -7.99095,7.72415 -15.14542,12.68825 -25.40667,17.62829 -8.75958,4.21711 -17.58726,6.92542 -27.42136,8.41281 -4.75329,0.71893 -17.98562,1.05102 -22.62741,0.56787 z" id="hole"/>' %self.color

    def get_html_for_svg_icon(self):
        svg_tag  = '<svg viewBox="0 0 320 512" height="42">%s</svg>' %self.get_path()
        if self.number:
            num  = self.number
        else:
            num = ""
        number_tag = '<div class="number" id="number-%s">%s</div>' %(self.id, num)
        return svg_tag + number_tag


class PeryTripList():
    '''
    This class describes the Triplist which is used as
    a container for the selected point on Map- or List-View
    '''
    def __init__(self, request, trip_stations, **kwargs):

        self.request = request
        self.trip_stations = trip_stations

        for key, value in kwargs.iteritems():
            if "href_click_on_title" in key:
                self.href_click_on_title = value.get('link') + '&' + value.get('get_param') + '='
                self.href_click_on_title_obj_attr = 'station.' + value.get('obj_attr')
            elif "header" in key:
                self.header = value
            elif "body" in key:
                self.body = value

    def get_href(self):
        if self.href_click_on_title:
            pass


class PERYMapList():
    '''
    This class describes the List View
    '''
    def __init__(self, request, template):
        self.request = request
        self.table_data = []
        self.template = template
        self.trip_station_dict  = {}

    def render(self):
        return render_to_string(self.template, locals())

    def get_header(self):
        header_list = []
        for key, value in self.table_data[0].iteritems():
            header_list.append()


class PERYMap():
    '''
    This class describes the Map View
    '''

    # switches for config the map functionality
    SHOW_LEGEND = True
    SHOW_SCALE = True
    SHOW_RANK_SWITCH = True

    def __init__(self, request):
        self.request = request
        self.data_points = []       # container for the added points
        self.rank_dict = {}         # container for the ranks
        self.get_data()
        self.available_ranks = {}
        self.active_rank = None
        self.table_data_dict = []


    def set_rank_range(self, min, max, count_of_ranges=5):
        """
        Use this function to define the rank ranges. If you want use your own dict as rank ranges use
        the the function :func:<pery_map.PERYMap.set_rank>`

        :param min: could be a number, date or datetime
        :param max: could be a number, date or datetime
        :param count_of_ranges: this value is used to calculate the upper and lower borders of each range
        """
        rank_dict= {}
        self.count_of_ranks = count_of_ranges

        if max <= min:
            raise Exception('max parameter must be greater as min value')

        if not min:
            if not max:
                raise Exception("min and max parameter are needed")

        range_delta = (max-min) / count_of_ranges

        # needed for the labels in the legend
        rank_dict['undefined'] = {
            'color': get_pery_map_color('level0/%s' %count_of_ranges),
            'label': 'no values available'
        }

        for i in range(count_of_ranges):
            tmp_min = min + range_delta * i
            tmp_max = min + range_delta * (i+1)
            tmp_color = get_pery_map_color('level%s/%s' %(i+1, count_of_ranges))

            if self.available_ranks.get(self.active_rank).sort_inverse:
                tmp_color = get_pery_map_color('level%s/%s' %(count_of_ranges - i , count_of_ranges))

            rank_dict['level%s' %(i+1)] = {
                'min': tmp_min,
                'max': tmp_max,
                'count': 0,
                'color': tmp_color
            }

        self.rank_dict = rank_dict

    def set_rank(self, rank_dict):
        '''
        Use this if you have an proper rank dict already
        '''
        self.rank_dict = rank_dict

    def classify_point(self, rank_value):
        """
        This function classified a given value (e.g. point) and returns a the evaluated rank.
        Take care that you has set the rank ranges (set_rank or set_rank_range) before you use this
        function.
        If the given value is not in scope of any rank, an exception will raise.
        :param rank_value: the value which should be evaluated
        :return: the rank of the evaluated value
        """

        for key, value in self.rank_dict.iteritems():
            """
            value: range dict
            key: the name of the rank
            """

            if value.get('min') or value.get('max'):
                if value.get('min') <= rank_value <= value.get('max'):
                    value['count'] = value['count'] + 1
                    return key

        raise Exception('rank_value of point is not in range of any rank')

    def add_point(self, lon, lat, id=None, popup=None, number=0, icon='point', color='default', rank_value=None, table_data={}):
        '''
       Used to create an new point. The point will
        also be classified and added to the Map
       :param lon:
       :param lat:
       :param id: the id for this point
            default: None - will be added on creation
       :param popup: the html for the popup of this point
       :param number: the ordering number of this point
            default: None - no popup available
       :param icon: define as which shape it should be presented
       :param color:
       :param rank_value:
            default: None - will be classified from system
       :param table_data:
       '''

        if popup:
            popup = mark_safe(''.join(popup.splitlines()))

        tmp_point = PERYMapPoint(
            lon=lon,
            lat=lat,
            id=id,
            popup=popup,
            number=number,
            icon=icon,
            color=color
        )

        # classify the new point
        if self.rank_dict:
            if rank_value:
                rank = self.classify_point(rank_value)
                tmp_point.color = self.rank_dict.get(rank).get('color')
                tmp_point.rank = rank
                tmp_point.rank_value = rank_value

            else:
                tmp_point.set_color('level0/%s' %self.count_of_ranks)

        self.data_points.append(tmp_point)

    def place_points(self, points, loc_at_point, offset=0.0002):
        '''
        Is used to replace given points
        which have the same address
        :param points:
        :param loc_at_point:
        :param offset:
        :return:
        '''

        # define offset for shifting
        # (x: lon, y: lat)
        lookup_locs = {
            1: (-1.15, 0),
            2: (1.15, 0),
            3: (-1.15, 0.83),
            4: (0, 0.83),
            5: (1.15, 0.83),
            6: (-1.15, (2*0.83)),
            7: (0, (2*0.83)),
            8: (1.15, (2*0.83)),
        }


        if loc_at_point <= 8:
            # iterate over all points
            for n, seq in enumerate(points):
                if not n == 0:                  # there are points registered
                    points[n].is_many = True    # mark the current point that there are other point at the same address

                    # get offset from lookup table and shift point
                    locs_lon, locs_lat  = lookup_locs.get(n)
                    points[n].lat += locs_lat * offset
                    points[n].lon += locs_lon * offset

        return points

    def render(self):
        '''
        Will be used to handle the rendering of the map
        :return: the rendered map as HTML
        '''

        offset = 0.000135
        point_dict = {}

        # first iteration: aggregate points
        for point in self.data_points:

            # {'lat, lon':[data_points elem]}
            k = '%s|%s' %(point.lat, point.lon  )
            if k in point_dict:
                point_dict[k].append(point)
            else:
                point_dict[k] = [point]

        # second iteration: change coordinates if necessary
        # e.g. if many elements at one coordinate
        for latlon, points in point_dict.items():
            loc_at_point = len(points)
            if loc_at_point > 1:    # more than one elements at the same coordinate --> change
                self.place_points(points, loc_at_point, offset=offset)

        # write back to data_points
        for point in self.data_points:
            if point.is_many:
                point.change_icon_to_many()

        # get data from user history to restore map config from last visit
        if self.request.user.profile.pery_map_data:
            map_data = self.request.user.profile.pery_map_data
        else:
            map_data = settings.PERY_MAP_DATA

        for item in map_data.split('|'):
            if item.startswith('lat'):
                self.map_data_lat = item.split('lat')[-1]
            elif item.startswith('lng'):
                self.map_data_lng = item.split('lng')[-1]
            elif item.startswith('zoom'):
                self.map_data_zoom = item.split('zoom')[-1]

        return render_to_string('erp/map.html', locals())

    def render_legend(self):
        '''
        Will be used to handle the rendering of the rank legend
        :return: the rendered rank legend as HTML
        '''
        rank_list = []
        for key, rank in self.available_ranks.items():
            rank.name = key
            if key == self.active_rank:
                rank.is_active = True
            else:
                rank.is_active = False

            rank_list.append(rank)

        return render_to_string('admin/erp/trip/legend.html',
                                {
                                    'rank_dict': self.rank_dict,
                                    # 'active_filter': self.active_ranks

                                    'rank_list': rank_list
                                }).replace('\n', '')

