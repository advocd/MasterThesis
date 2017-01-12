import requests
from django.db import models


class PERYGis(models.Model):
    '''
    This class can be used as super class to extend the base class
    with possibility of geo information.
    '''

    # create DB fields
    geo_lat = models.FloatField(null=True, blank=True, editable=True)
    geo_lon = models.FloatField(null=True, blank=True, editable=True)
    geo_is_correct = models.BooleanField(blank=True)

    class Meta:
        abstract = True

    def get_coordinate_by_address(self, country, address=None, city=None):
        '''
        Used to get the coordinates for the object by an
        adress from a webservice.

        :return:
            lon: the longitude of the address
            lat: the latitude of the address
            geoquality: the accuracy of the data (e.g. city level, street level, ...)
        '''

        params = {
            'maxResults': 1,
            'street': address,
            'city': city,
            'country': country.iso_code
        }

        r = requests.get('http://open.mapquestapi.com/geocoding/v1/address', params=params)

        if r.status_code is not 200:
            raise Exception('PeryGIS: cant get geodata for new address from webservice')

        results = r.json().get('results')

        try:
            location = results[0].get('locations')[0]
            geoquality = location.get('geocodeQuality')

            if not location.get('street') and address:
                # street is unknown
                return None, None, geoquality

            if not location.get('adminArea5') and city:
                # city is unknown
                return None, None, geoquality

            lon = location.get('latLng').get('lng')
            lat = location.get('latLng').get('lat')

            return lon, lat, geoquality
        except:
            return None, None, geoquality
