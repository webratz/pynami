#!/usr/bin/env python
# this is a sample tool that demonstrates some usage cases
import os
import json
from tabulate import tabulate # pylint: disable=E0401
import pytoml as toml
from nami import Nami
from nami import UG_JUPFI, UG_PFADI
from schemas import MitgliedSchema

# load config
with open(os.path.expanduser('~/.pynami.conf'), 'r') as cfg:
    config = toml.load(cfg)

nami = Nami(config['nami'])
nami.auth()


def update_mitglied(mglid):
    """
    sample: get a mitglied, change the spitzname and save
    """
    # fetch data and load into schema to get a Mitglied object
    user = nami.get_mitglied_obj(mglid)

    # update the spitzname field
    user.spitzname = 'foobar'

    # save the changes
    user.update(nami)


def sample_search():
    """
    searches for users and prints some infos in an unsorted table
    check the readme for all possible arguments
    """
    search = {
        'mglStatusId': 'AKTIV',
        'mglTypeId': 'MITGLIED',
    #    'nachname': 'Sieferlinger',
        'untergliederungId': UG_JUPFI
    }

    table = []
    for mgl in nami.search(search):
        # by default you should only show what the search returns
        table.append(mgl.tabulate())

        # but you can also fetch the actual user object with more data
        # beware to not kill the API with numerous requests
        # details = mgl.get_mitglied(nami)
        # table.append(details.tabulate())


    print(tabulate(table, headers="keys"))

# update_mitglied(220695)
sample_search()
