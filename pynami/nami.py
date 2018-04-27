#!/usr/bin/env python
import os
import json
import requests
from tabulate import tabulate
from schemas import SearchMitgliedSchema, MitgliedSchema

# docs: https://doku.dpsg.de/display/NAMI/Service+Architektur


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
    def __init__(self):
        self.s = requests.Session()
        self.config = {
            'server': 'https://nami.dpsg.de',
            'stammesnummer': '131913',
            'auth_url': '/ica/rest/nami/auth/manual/sessionStartup',
            'search_url': '/ica/rest/api/1/2/service/nami/search/result-list'
        }

    def _check_response(self, response):
        if response.status_code != requests.codes.ok:
            raise NamiHTTPError('HTTP Error. Status Code: %s' % response.status_code)

        rjson = response.json()
        if not rjson['success']:
            raise NamiResponseSuccessError('succes state from NAMI was %s' % rjson['message'])
        # allowed response types are: OK, INFO, WARN, ERROR, EXCEPTION
        # if rjson['responseType'] not in ['OK', 'INFO']:
        #     raise NamiResponseTypeError('responseType from NAMI was %s' % rjson['responseType'])

        return rjson['data']


    def auth(self, username, password):
        """
        authenticate against the NAMI API. This stores the jsessionId cookie in the requests session
        therefore this needs to be called only once
        """
        payload = {
            'Login': 'API',
            'username': username,
            'password': password
        }
        url = "%s%s" % (self.config['server'], self.config['auth_url'])
        r = self.s.post(url, data=payload)
        if r.status_code != 200:
            raise ValueError('authentication failed')


    def search(self, search=None):
        """
        run a search and return all results as dict
        """
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
        return data

    def get_mitglied(self, id):
        url = "%s/ica/rest/nami/mitglied/filtered-for-navigation/gruppierung/gruppierung/%s/%s/" % (self.config['server'], self.config['stammesnummer'], id)
        r = self.s.get(url)
        return self._check_response(r)


    def put_mitglied(self, id, data):
        url = "%s/ica/rest/nami/mitglied/filtered-for-navigation/gruppierung/gruppierung/%s/%s/" % (self.config['server'], self.config['stammesnummer'], id)
        r = self.s.put(url, json=data)
        return self._check_response(r)



n = Nami()
n.auth('CHANGEME', 'CHANGEME')

# get a mitglied, change the spitzname and save
# m = n.get_mitglied(220695)
# mschema = MitgliedSchema()
# user = mschema.load(m).data
# user.spitzname = 'test123'
# userjson = mschema.dump(user).data
# n.put_mitglied(220695, userjson)

search = {
    'mglStatusId': 'AKTIV',
    'mglTypeId': 'MITGLIED',
    'untergliederungId': 2
}
# {
#   "alterBis": "",
#   "alterVon": "",
#   "bausteinIncludedId": [
#   ],
#   "ebeneId": null,
#   "funktion": "",
#   "grpName": "",
#   "grpNummer": "",
#   "gruppierung1Id": null,
#   "gruppierung2Id": [
#   ],
#   "gruppierung3Id": [
#   ],
#   "gruppierung4Id": [
#   ],
#   "gruppierung5Id": [
#   ],
#   "gruppierung6Id": [
#   ],
#   "inGrp": false,
#   "mglStatusId": null,
#   "mglTypeId": [
#   ],
#   "mglWohnort": "",
#   "mitAllenTaetigkeiten": false,
#   "mitgliedsNummber": "",
#   "nachname": "",
#   "organisation": "",
#   "privacy": "",
#   "searchName": "",
#   "searchType": "MITGLIEDER",
#   "spitzname": "",
#   "taetigkeitId": [
#   ],
#   "tagId": [
#   ],
#   "untergliederungId": [
#     2
#   ],
#   "unterhalbGrp": false,
#   "vorname": "",
#   "withEndedTaetigkeiten": false,
#   "zeitschriftenversand": false
# }
smschema = SearchMitgliedSchema()
rawusers = n.search(search)
users = []
for i in rawusers:
    user = smschema.load(i)
    users.append(user.data.table_view())

print(tabulate(users))
