from conf.constants import error
from csv import DictWriter, QUOTE_ALL
from datetime import datetime
from json import dump as jdump, dumps as jdumps
from modules.error import Error
from neo4j import GraphDatabase
from os import makedirs, path
from yaml import dump as ydump, load, SafeLoader


class File:


    error = Error()
    fd = None
    name = None


    def __init__(self, directory = None):
        if directory:
            timestamp = datetime.now().strftime('%Y.%m.%d-%H.%M.%S')
            self.directory = f'{directory}/{timestamp}'
            if not path.exists(self.directory):
                makedirs(self.directory)


    def __del__(self):
        if File.fd:
            File.fd.close()
            File.name = None


    def read(self, filename):
        self.open(filename)
        if not self.error:
            try:
                return File.fd.read().splitlines()
            except Exception as e:
                File.error.add(error['file']['read'].format(
                    e = e,
                    filename = filename
                ))
        return None


    def open(self, filename, mode = 'read'):
        try:
            if mode == 'write':
                m = 'w'
                File.name = f'{self.directory}/{filename}'
            else:
                m = 'r'
                File.name = filename
            File.fd = open(File.name, mode = m, encoding = 'utf-8')
        except Exception as e:
            File.error.add(error['file']['open'].format(
                e = e,
                filename = File.name,
                mode = mode
            ))


class CSV(File):


    def __init__(self, directory = None):
        File.__init__(self, directory)


    def dump(self, data, filename = None):
        if data:
            fieldnames = data[0].keys()

            # Dump to file
            if filename:
                filename = f'{filename}.csv'
                self.open(filename, 'write')
                if not self.error:
                    try:
                        writer = DictWriter(
                            self.fd,
                            delimiter = ';',
                            quoting = QUOTE_ALL,
                            fieldnames = fieldnames
                        )
                        writer.writeheader()
                        writer.writerows(data)
                    except Exception as e:
                        CSV.error.add(error['csv']['dump'].format(
                            e = e,
                            filename = self.name
                        ))
                data = None

            # Return dump
            else:
                output = f'{";".join(fieldnames)}\n'
                for row in data:
                    output += f'{";".join(list(row.values()))}\n'
                data = output[:-1]

        return data


class JSON(File):


    def __init__(self, directory = None):
        File.__init__(self, directory)


    def dump(self, data, filename = None):

        # Dump to file
        if filename:
            filename = f'{filename}.json'
            self.open(filename, 'write')
            if not self.error:
                try:
                    jdump(data, self.fd)
                    self.fd.write('\n')
                except Exception as e:
                    JSON.error.add(error['json']['save'].format(
                        e = e,
                        filename = self.name
                    ))
            data = None

        # Return dump
        else:
            try:
                data = jdumps(data)
            except Exception as e:
                YAML.error.add(error['json']['dump'].format(e = e))

        return data


class YAML(File):


    def __init__(self, directory = None):
        File.__init__(self, directory)


    def dump(self, data, filename = None):

        # Dump to file
        if filename:
            filename = f'{filename}.yaml'
            self.open(filename, 'write')
            if not self.error:
                try:
                    ydump(
                        data,
                        default_flow_style = False,
                        sort_keys = False,
                        stream = self.fd
                    )
                except Exception as e:
                    YAML.error.add(error['yaml']['save'].format(
                        e = e,
                        filename = self.name
                    ))
            data = None

        # Return dump
        else:
            try:
                data = ydump(
                    data,
                    default_flow_style = False,
                    sort_keys = False
                )
                data = data[:-1]
            except Exception as e:
                YAML.error.add(error['yaml']['dump'].format(e = e))

        return data


    def read(self, filename):
        data = None
        self.open(filename)
        if not self.error:
            try:
                data = load(self.fd, Loader = SafeLoader)
            except Exception as e:
                YAML.error.add(error['yaml']['read'].format(
                    e = e,
                    filename = filename
                ))
        return data


class Neo4j:


    def __init__(self, host, port, username, password, encrypted):
        self.error = Error()
        self.uri = f'bolt://{host}:{port}'
        self.user = username
        self.password = password
        self.encrypted = bool(encrypted == 'on')
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth = (self.user, self.password),
                encrypted = self.encrypted
            )
        except Exception as e:
            self.error.add(error['neo4j']['connect'].format(e = e))
        self.clean()


    def __del__(self):
        if 'driver' in self.__dict__:
            self.driver.close()


    def clean(self):
        self.result = {
            'key': None,
            'record': None
        }


    def execute(self, sentence):
        self.clean()
        with self.driver.session() as session:
            try:
                result = session.run(sentence)
                self.result = self.normalize(result.data())
            except Exception as e:
                self.error.add(error['neo4j']['execute'].format(
                    e = e,
                    sentence = sentence
                ))
            except KeyboardInterrupt:
                # ctrl+c
                self.error.add(
                    error['neo4j']['interrupted'].format(sentence = sentence)
                )
                self.driver.close()


    def normalize(self, results):
        for row in results:
            for k, v in row.items():
                row[k] = str(v)
        return results
