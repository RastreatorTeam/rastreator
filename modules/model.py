from conf.constants import error
from copy import deepcopy
from datetime import timedelta
from modules.error import Error
from modules.io import YAML
from re import sub
from time import time


class ActiveDirectory():


    def __init__(self, domain = 'RASTREATOR.LOCAL', lang = 'en'):
        self.error = Error()
        self.load()
        self.set('domain', domain)
        self.set('lang', lang)


    def get(self, attribute = None):
        if attribute:
            if attribute == 'lang_vars':
                return self.languages[self.lang]
            elif attribute in self.__dict__:
                return self.__dict__[attribute]
            else:
                return None
        else:
            attributes = deepcopy(self.__dict__)
            attributes.pop('error')
            attributes.pop('languages')
            return attributes


    def load(self):
        self.languages = YAML().read('conf/languages.yaml')
        if YAML.error:
            self.error.add(YAML.error.get())


    def set(self, key, value):
        if key in ['domain', 'lang']:
            self.__dict__[key] = value


class Path():


    def __init__(self, start = '', end = ''):
        self.error = Error()
        self.set('start', start)
        self.set('end', end)


    def get(self, attribute = None):
        if attribute:
            if attribute in self.__dict__:
                return self.__dict__[attribute]
            else:
                return None
        else:
            attributes = deepcopy(self.__dict__)
            attributes.pop('error')
            return attributes


    def set(self, key, value):
        if key in ['start', 'end']:
            node_type = node_name = ''
            if value:
                kv = value.split(':')
                if len(kv) > 1:
                    node_type = f':{kv[0]}'
                    node_name = kv[1]
                else:
                    node_name = kv[0]
                node_name = f'{{name:"{node_name}"}}'
            self.__dict__[f'{key}_type'] = node_type
            self.__dict__[f'{key}_name'] = node_name


class BaseQuery():


    def __init__(self, data):

        self.attribute = {
            'core': {},
            'optional': {}
        }
        self.error = Error()
        self.state = 'enabled'

        if data:
            self.normalize(data)
            self.check_data(self.__dict__, data, self.attribute)


    def check_data(self, internal, data, check):
        if 'core' in check:
            for ckey, cvalue in check['core'].items():
                if ckey in data:
                    self.check_key_value(internal, data, ckey, cvalue)
                else:
                    self.error.add(error['parse']['key'].format(key = ckey))
        if 'optional' in check:
            for key, _ in data.items():
                if not ('core' in check and key in check['core']):
                    if key in check['optional']:
                        ovalue = check['optional'][key]
                        self.check_key_value(internal, data, key, ovalue)


    def check_key_value(self, internal, data, key, value):
        if isinstance(value, dict):
            if key in data:
                if isinstance(data[key], dict):
                    internal[key] = {}
                    self.check_data(internal[key], data[key], value)
                    if not internal[key]:
                        internal.pop(key)
                else:
                    self.error.add(error['parse']['value'].format(
                        value = data[key],
                        key = key
                    ))
            else:
                self.error.add(error['parse']['key'].format(key = key))
        else:
            if isinstance(value, list):
                if key in data:
                    if data[key]:
                        if value:
                            if data[key] not in value:
                                self.error.add(error['parse']['value'].format(
                                    value = data[key],
                                    key = key
                                ))
                                return
                        else:
                            if not isinstance(data[key], list):
                                self.error.add(error['parse']['object'].format(
                                    bad = type(data[key]).__name__,
                                    good = 'list',
                                    key = key
                                ))
                                return

                    else:
                        self.error.add(error['parse']['value'].format(
                            value = data[key],
                            key = key
                        ))
                        return
                else:
                    self.error.add(error['parse']['key'].format(key = key))
                    return
            internal[key] = data[key]


    def get(self, attribute, exclude = True):
        sd = self.__dict__
        qa = deepcopy(sd)

        # Remove internal attributes
        qa.pop('attribute', None)

        # Get attributes
        for a in sd:
            if a in attribute:
                # Value != None
                if attribute[a]:
                    for sa in sd[a]:
                        if sa in attribute[a]:
                            if exclude:
                                qa[a].pop(sa, None)
                        else:
                            if not exclude:
                                qa[a].pop(sa, None)
                elif exclude:
                    qa.pop(a, None)
            elif not exclude:
                qa.pop(a, None)

        # Sort attributes
        attributes = \
            list(self.attribute['core'].keys()) + \
            list(self.attribute['optional'].keys()) + \
            ['cstatement', 'result', 'error']

        return dict(sorted(qa.items(), key = lambda x: attributes.index(x[0])))


    def normalize(self, data):
        for key in list(data):
            value = data[key]
            if isinstance(value, dict):
                value = data.pop(key)
                key = key.lower()
                data[key] = value
                self.normalize(value)
            else:
                value = data.pop(key)
                key = key.lower()
                if key in ['tactic', 'tag']:
                    value = value.lower()
                data[key] = value


    def update(self, key, value):
        value.update(self.attribute[key])
        self.attribute[key] = value


class RawQuery(BaseQuery):


    def __init__(self, data):

        # Parent init
        BaseQuery.__init__(self, data)

        if not self.error:
            # Core attributes definition
            self.update('core', {
                'filename': None,
                'statement': {
                    'core': {
                        'table': None
                    },
                    'optional': {
                        'count': [],
                        'graph': []
                    }
                }
            })

            # Set data
            if data:
                self.check_data(self.__dict__, data, self.attribute)

            # Execution result
            self.result = {}


    def compile(self, ad, path):

        self.cstatement = {}

        define = self.preprocess(ad, path)

        if 'table' in self.statement:
            self.cstatement['table'] = self.statement['table']
            for e in define:
                pattern = e['pattern']
                replace = e['replace']
                try:
                    self.cstatement['table'] = sub(
                        pattern,
                        replace,
                        self.cstatement['table']
                    )
                except Exception as e:
                    self.error.add(error['compile']['pattern'].format(
                        e = e,
                        pattern = pattern,
                        type = 'table'
                    ))

            for stype in ['graph', 'count']:
                if stype in self.statement:
                    self.cstatement[stype] = self.cstatement['table']
                    for regex in self.statement[stype]:
                        for e in define:
                            pattern = e['pattern']
                            replace = e['replace']
                            try:
                                regex = sub(pattern, replace, regex)
                            except Exception as e:
                                self.error.add(
                                    error['compile']['pattern'].format(
                                        e = e,
                                        pattern = pattern,
                                        type = stype
                                    )
                                )
                        field = regex.split('/')
                        try:
                            self.cstatement[stype] = sub(
                                field[0],
                                field[1],
                                self.cstatement[stype]
                            )
                        except Exception as e:
                            self.error.add(error['compile']['pattern'].format(
                                e = e,
                                pattern = field[0],
                                type = stype
                            ))


    def preprocess(self, ad, path):
        define = []

        # AD domain
        define.append({
            'pattern': 'RAS-DOMAIN',
            'replace': ad.get('domain')
        })

        # AD language
        for key, value in ad.get('lang_vars').items():
            define.append({
                'pattern': key,
                'replace': value
            })

        # Path from type
        define.append({
            'pattern': ':RAS-STARTING_NODE_TYPE',
            'replace': path.get('start_type')
        })

        # Path from name
        define.append({
            'pattern': '{RAS-STARTING_NODE_NAME}',
            'replace': path.get('start_name')
        })

        # Path to type
        define.append({
            'pattern': ':RAS-ENDING_NODE_TYPE',
            'replace': path.get('end_type')
        })

        # Path to name
        define.append({
            'pattern': '{RAS-ENDING_NODE_NAME}',
            'replace': path.get('end_name')
        })

        return define


class TestQuery(RawQuery):


    def __init__(self, data):

        # Parent init
        RawQuery.__init__(self, data)

        if not self.error:
            # Core attributes definition
            self.update('core', {
                'filename': None,
                'name': None
            })

            # Set data
            if data:
                self.check_data(self.__dict__, data, self.attribute)


class DefaultQuery(TestQuery):


    def __init__(self, data):

        # Parent init
        TestQuery.__init__(self, data)

        if not self.error:
            # Core/optional attributes definition
            self.update('core', {
                'filename': None,
                'author': None,
                'name': None,
                'state': None,
                'tactic': [
                    'collection',
                    'command and control',
                    'credential access',
                    'defense evasion',
                    'discovery',
                    'execution',
                    'exfiltration',
                    'impact',
                    'initial access',
                    'lateral movement',
                    'persistence',
                    'privilege escalation'
                ],
                'tag': ['analysis', 'attack', 'issue'],
                'description': None
            })

            # Optional attributes definition
            self.update('optional', {
                'reference': [],
                'nextsteps': {
                    'optional': {
                        'rt': [],
                        'bt': []
                    }
                }
            })

            # Set data
            if data:
                self.check_data(self.__dict__, data, self.attribute)


class CheckQuery(DefaultQuery):


    def __init__(self, data):

        # Parent init
        DefaultQuery.__init__(self, deepcopy(data))

        if not self.error:
            data.pop('filename', None)
            self.disk_query = data


    def diff(self):
        # Transform Dump to string to compare.

        ex = {
            'filename': None,
            'cstatement': None,
            'result': None,
            'disk_query': None
        }


        query = self.get(ex)

        query.pop('error')

        diff = []

        count_lines = 1

        disk_query_lines = YAML().dump(self.disk_query).splitlines()
        query_lines = YAML().dump(query).splitlines()


        for disk_lines, q_lines in zip(disk_query_lines, query_lines):
            if disk_lines != q_lines:
                diff.append({
                    'line': count_lines,
                    '<': disk_lines,
                    '>': q_lines
                })
            count_lines += 1

        if len(disk_query_lines) > len(query_lines):
            for lines in disk_query_lines[len(query_lines):]:
                diff.append({
                    'line': count_lines,
                    '<': lines,
                    '>': ''
                })
                count_lines += 1
        else:
            for lines in query_lines[len(disk_query_lines):]:
                diff.append({
                    'line': count_lines,
                    '<': '',
                    '>': lines
                })
                count_lines += 1

        self.result = {
            'built_query': query,
            'diff': diff
        }


class Query:


    def __new__(cls, op_mode, data):
        if op_mode == 'raw':
            return RawQuery(data)
        if op_mode == 'test':
            return TestQuery(data)
        if op_mode == 'check':
            return CheckQuery(data)
        # Default Query
        return DefaultQuery(data)


class Result():


    def __init__(self):
        self.data = None
        self.time = time()


    def add(self, data):
        self.data = data
        self.time = timedelta(seconds = time() - self.time)
