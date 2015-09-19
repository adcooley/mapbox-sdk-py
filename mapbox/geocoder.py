import requests
from uritemplate import URITemplate

from mapbox.service import Service


class InvalidPlaceTypeError(KeyError):
    pass


class Geocoder(Service):
    """A very simple Geocoding API proxy"""

    def __init__(self, name='mapbox.places', access_token=None):
        self.name = name
        self.baseuri = 'https://api.mapbox.com/v4/geocode'
        self.session = self.get_session(access_token)

    def _validate_place_types(self, types):
        """Validate place types and return a mapping for use in requests"""
        for pt in types:
            if pt not in self.place_types:
                raise InvalidPlaceTypeError(pt)
        return {'types': ",".join(types)}

    def forward(self, address, types=None, lon=None, lat=None):
        """Returns a Requests response object that contains a GeoJSON
        collection of places matching the given address.

        `response.json()` returns the geocoding result as GeoJSON.
        `response.status_code` returns the HTTP API status code.

        Place results may be constrained to those of one or more types
        or be biased toward a given longitude and latitude.

        See: https://www.mapbox.com/developers/api/geocoding/#forward."""
        uri = URITemplate('%s/{dataset}/{query}.json' % self.baseuri).expand(
            dataset=self.name, query=address)
        params = {}
        if types:
            params.update(self._validate_place_types(types))
        if lon is not None and lat is not None:
            params.update(proximity='{0},{1}'.format(lon, lat))
        return self.session.get(uri, params=params)

    def reverse(self, lon=None, lat=None, types=None):
        """Returns a Requests response object that contains a GeoJSON
        collection of places near the given longitude and latitude.

        `response.json()` returns the geocoding result as GeoJSON.
        `response.status_code` returns the HTTP API status code.

        See: https://www.mapbox.com/developers/api/geocoding/#reverse."""
        uri = URITemplate(self.baseuri + '/{dataset}/{lon},{lat}.json').expand(
            dataset=self.name, lon=str(lon), lat=str(lat))
        params = {}
        if types:
            params.update(self._validate_place_types(types))
        return self.session.get(uri, params=params)

    @property
    def place_types(self):
        """A mapping of place type names to descriptions"""
        return {
            'address': "A street address with house number. Examples: 1600 Pennsylvania Ave NW, 1051 Market St, Oberbaumstrasse 7.",
            'country': "Sovereign states and other political entities. Examples: United States, France, China, Russia.",
            'place': "City, town, village or other municipality relevant to a country's address or postal system. Examples: Cleveland, Saratoga Springs, Berlin, Paris.",
            'poi': "Places of interest including commercial venues, major landmarks, parks, and other features. Examples: Yosemite National Park, Lake Superior.",
            'postcode': "Postal code, varies by a country's postal system. Examples: 20009, CR0 3RL.",
            'region': "First order administrative divisions within a country, usually provinces or states. Examples: California, Ontario, Essonne."}
