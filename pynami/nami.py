# NAMI library in python
# pylint: disable=C0301
import json
import requests
from schemas import SearchMitgliedSchema, MitgliedSchema
# docs: https://doku.dpsg.de/display/NAMI/Service+Architektur

# define some constants

# untergliederungId
UG_WOE = 1
UG_JUPFI = 2
UG_PFADI = 3
UG_ROVER = 4
UG_STAVO = 5

# taetigkeitId
TG_LEITER = 6
TG_KURAT = 1011


class NamiResponseTypeError(Exception):
    pass


class NamiResponseSuccessError(Exception):
    """
    This is being raised when the response 'success' field is not True
    """
    pass


class NamiHTTPError(Exception):
    pass


class Nami(object):
    """
    handles auth and basic tasks to use DPSG NAMI
    You can use the requests session to write your own things upon this
    """
    def __init__(self, config):
        self.s = requests.Session()
        self.config = {
            'server': 'https://nami.dpsg.de',
            'auth_url': '/ica/rest/nami/auth/manual/sessionStartup',
            'search_url': '/ica/rest/api/1/2/service/nami/search/result-list'
        }
        self.config.update(config)

    def _check_response(self, response):
        """
        check a requests response object if the NAMI response looks ok
        this currently checks some very basic things
        """
        if response.status_code != requests.codes.ok:   #pylint: disable=E1101
            raise NamiHTTPError('HTTP Error. Status Code: %s' % response.status_code)

        rjson = response.json()
        if not rjson['success']:
            raise NamiResponseSuccessError('succes state from NAMI was %s %s' % (rjson['message'], rjson))

        # allowed response types are: OK, INFO, WARN, ERROR, EXCEPTION
        # if rjson['responseType'] not in ['OK', 'INFO']:
        #     raise NamiResponseTypeError('responseType from NAMI was %s' % rjson['responseType'])

        return rjson['data']


    def auth(self, username=None, password=None):
        """
        authenticate against the NAMI API. This stores the jsessionId cookie in the requests session
        therefore this needs to be called only once

        Args:
            username (str): the NAMI username. Which is your Mitgliedsnummer (eg 31015)
            password (str): your NAMI password

        Returns:
            object: the requests session, including the auth cookie
        """
        if not username or not password:
            username = self.config['username']
            password = self.config['password']

        payload = {
            'Login': 'API',
            'username': username,
            'password': password
        }

        url = "%s%s" % (self.config['server'], self.config['auth_url'])
        r = self.s.post(url, data=payload)
        if r.status_code != 200:
            raise ValueError('authentication failed')

        return self.s


    def search(self, search=None):
        """
        run a search and return all results as dict
        """
        # this is just a default search
        if not search:
            search = {
                'mglStatusId': 'AKTIV',
                'mglTypeId': 'MITGLIED',
            }

        # this defaults should avoid pagination
        params = {
            'searchedValues': json.dumps(search),
            'page': 1,
            'start': 0,
            'limit': 999999
        }
        r = self.s.get("%s%s" % (self.config['server'], self.config['search_url']), params=params)
        data = self._check_response(r)

        # print(json.dumps(r.json(), indent=4, sort_keys=True))
        smschema = SearchMitgliedSchema()
        users = []
        for i in data:
            users.append(smschema.load(i).data)
        return users

    def mitglied(self, mglid, method='GET', stammesnummer=None, **kwargs):
        """
        gets or updates a mitglied

        Args:
            mglid (int) ID of the Mitglied. This is not the NAMI Mitgliedsnummer
            method (str): HTTP Method. Should be GET or PUT, defaults to GET
            stammesnummer (int): the DPSG stammesnummer. eg 131913

        Returns:
            dict: data of the Mitglied. This can be used to feed the schema and then get a Mitglied Object
        """
        if not stammesnummer:
            stammesnummer = self.config['stammesnummer']
        url = "%s/ica/rest/nami/mitglied/filtered-for-navigation/gruppierung/gruppierung/%s/%s/" % (self.config['server'], stammesnummer, mglid)
        r = self.s.request(method, url, **kwargs)
        return self._check_response(r)

    def get_mitglied_obj(self, mglid):
        mschema = MitgliedSchema()
        m = self.mitglied(mglid)
        user = mschema.load(m).data
        return user
