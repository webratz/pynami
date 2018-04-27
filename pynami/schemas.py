from datetime import datetime
from collections import OrderedDict
from marshmallow import Schema, fields, post_load # pylint: disable=E0401

class NamiDateTimeField(fields.DateTime):
    def _deserialize(self, value, attr, data):
        if value == '':
            return None
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')

    def _serialize(self, value, attr, data):
        if not value:
            return ''
        return value.strftime('%Y-%m-%d %H:%M:%S')


class SearchMitglied(object):
    def __init__(self, **kwargs):
        self.data = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return '<SearchMitglied({self.descriptor!r})>'.format(self=self)


    def table_view(self):
        field_blacklist = ['representedClass', 'mglType', 'staatsangehoerigkeit', 'status', 'geschlecht', 'eintrittsdatum', 'id', 'wiederverwendenFlag', 'descriptor', 'version', 'lastUpdated', 'id_id']
        return {k: v for k, v in self.data.items() if v is not None and v != '' and k not in field_blacklist}

    def tabulate(self, elements=None):
        d = OrderedDict()
        if not elements:
            elements = ['mitgliedsNummer', 'vorname', 'nachname', 'geburtsDatum']
        for k in elements :
            d[k] = self.data[k]
        return d

    def get_mitglied(self, nami):
        m = nami.mitglied(self.id_id, 'GET', stammesnummer=nami.config['stammesnummer'])
        l = MitgliedSchema().load(data=m)
        return l.data


class SearchMitgliedSchema(Schema):
    descriptor = fields.String()
    entries_austrittsDatum = NamiDateTimeField(attribute='austrittsDatum')
    entries_beitragsarten = fields.String(attribute='beitragsarten')
    entries_eintrittsdatum = NamiDateTimeField(attribute='eintrittsdatum')
    entries_email = fields.String(attribute="email")
    entries_emailVertretungsberechtigter = fields.String(attribute="emailVertretungsberechtigter", allow_none=True)
    entries_ersteTaetigkeitId = fields.Integer(attribute='ersteTaetigkeitId', allow_none=True)
    entries_ersteUntergliederungId = fields.Integer(attribute='ersteUntergliederungId', allow_none=True)
    entries_fixBeitrag = fields.String(attribute="fixBeitrag", allow_none=True)
    entries_geburtsDatum = NamiDateTimeField(attribute='geburtsDatum')
    entries_genericField1 = fields.String(attribute="genericField1", allow_none=True)
    entries_genericField2 = fields.String(attribute="genericField2", allow_none=True)
    entries_geschlecht = fields.String(attribute='geschlecht') # TODO check allowed values
    entries_id = fields.Integer(attribute='id')
    entries_jungpfadfinder = fields.String(attribute='jungpfadfinder')
    entries_konfession = fields.String(attribute='konfession')
    entries_kontoverbindung = fields.String(attribute='kontoverbindung')
    entries_lastUpdated = NamiDateTimeField(attribute='lastUpdated')
    entries_mglType = fields.String(attribute='mglType')
    entries_mitgliedsNummer = fields.Integer(attribute='mitgliedsNummer')
    entries_nachname = fields.String(attribute='nachname')
    entries_pfadfinder = fields.String(attribute='pfadfinder')
    entries_rover = fields.String(attribute='rover')
    entries_rowCssClass = fields.String(attribute='rowCssClass')
    entries_spitzname = fields.String(attribute='spitzname')
    entries_staatangehoerigkeitText = fields.String(attribute='staatangehoerigkeitText')
    entries_staatsangehoerigkeit = fields.String(attribute='staatsangehoerigkeit')
    entries_status = fields.String(attribute='status')
    entries_stufe = fields.String(attribute='stufe')
    entries_pfadfinder = fields.String(attribute='pfadfinder')
    entries_telefax = fields.String(attribute='telefax')
    entries_telefon1 = fields.String(attribute='telefon1')
    entries_telefon2 = fields.String(attribute='telefon2')
    entries_telefon3 = fields.String(attribute='telefon3')
    entries_version = fields.Integer(attribute='version')
    entries_vorname = fields.String(attribute='vorname')
    entries_pfadfinder = fields.String(attribute='pfadfinder')
    entries_wiederverwendenFlag = fields.Boolean(attribute='wiederverwendenFlag')
    entries_woelfling = fields.String(attribute='woelfling')
    id = fields.Integer(attribute='id_id')
    representedClass = fields.String(attribute='representedClass')

    @post_load
    def make_user(self, data):
        return SearchMitglied(**data)


class Mitglied(object):
    def __init__(self, **kwargs):
        self.data = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return '<Mitglied({self.nachname!r}, {self.vorname!r})>'.format(self=self)


    def table_view(self):
        field_blacklist = ['genericField1']
        return {k: v for k, v in self.data.items() if v is not None and v != '' and k not in field_blacklist}

    def tabulate(self, elements=None):
        d = OrderedDict()
        if not elements:
            elements = ['mitgliedsNummer', 'vorname', 'nachname', 'geburtsDatum', 'strasse', 'stufe']
        for k in elements :
            d[k] = self.data[k]
        return d

    def update(self, nami):
        userjson = MitgliedSchema().dump(self).data
        nami.mitglied(self.id, 'PUT', stammesnummer=nami.config['stammesnummer'], json=userjson)

class MitgliedSchema(Schema):
    austrittsDatum = NamiDateTimeField()
    beitragsart = fields.String(allow_none=True)
    beitragsartId = fields.Integer(allow_none=True)
    eintrittsdatum = NamiDateTimeField()
    email = fields.String()
    emailVertretungsberechtigter = fields.String()
    ersteTaetigkeit = fields.String(allow_none=True)
    ersteTaetigkeitId = fields.Integer(allow_none=True)
    ersteUntergliederung = fields.String(allow_none=True)
    ersteUntergliederungId = fields.Integer(allow_none=True)
    fixBeitrag = fields.String(allow_none=True)
    geburtsDatum = NamiDateTimeField()
    genericField1 = fields.String(allow_none=True)
    genericField2 = fields.String(allow_none=True)
    geschlecht = fields.String()
    geschlechtId = fields.Integer(allow_none=True)
    gruppierung = fields.String()
    gruppierungId = fields.Integer(allow_none=True)
    id = fields.Integer()
    jungpfadfinder = fields.String(allow_none=True)
    konfession = fields.String(allow_none=True)
    konfessionId = fields.Integer(allow_none=True)
    kontoverbindung = fields.Dict()
    land = fields.String()
    landId = fields.Integer()
    lastUpdated = NamiDateTimeField()
    mglType = fields.String()
    mglTypeId = fields.String()
    mitgliedsNummer = fields.Integer()
    nachname = fields.String()
    nameZusatz = fields.String(allow_none=True)
    ort = fields.String(allow_none=True)
    pfadfinder = fields.String(allow_none=True)
    plz = fields.String(allow_none=True)
    region = fields.String(allow_none=True)
    regionId = fields.Integer(allow_none=True)
    rover = fields.String(allow_none=True)
    sonst01 = fields.Boolean(allow_none=True)
    sonst02 = fields.Boolean(allow_none=True)
    spitzname = fields.String(allow_none=True)
    staatsangehoerigkeit = fields.String(allow_none=True)
    staatsangehoerigkeitId = fields.Integer(allow_none=True)
    staatsangehoerigkeitText = fields.String(allow_none=True)
    status = fields.String(allow_none=True)
    strasse = fields.String(allow_none=True)
    stufe = fields.String(allow_none=True)
    telefax = fields.String(allow_none=True)
    telefon1 = fields.String(allow_none=True)
    telefon2 = fields.String(allow_none=True)
    telefon3 = fields.String(allow_none=True)
    staatsangehoerigkeitText = fields.String(allow_none=True)
    version = fields.Integer()
    vorname = fields.String(allow_none=True)
    wiederverwendenFlag = fields.Boolean()
    woelfling = fields.String(allow_none=True)
    zeitschriftenversand = fields.Boolean(allow_none=True)

    @post_load
    def make_user(self, data):
        return Mitglied(**data)
