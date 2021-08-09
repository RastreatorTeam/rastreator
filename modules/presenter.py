from modules.error import Error
from modules.io import CSV, JSON, YAML
from modules.model import Result
from prettytable import PrettyTable


class Presenter:


    def __init__(self, verbose, op_mode):
        self.verbose = verbose
        self.op_mode = op_mode


    def filter(self, data):

        verbose = self.verbose

        if 'Query' in type(data).__name__:

            exclude = True

            # If there is an error
            if data.error:
                attribute = {
                    'filename': None,
                    'error': None
                }
                exclude = False
            else:
                # If verbose is quiet
                if verbose == 'quiet':
                    if self.op_mode == 'execute':
                        # Remove execution time
                        data.result['table'].time = None
                        return data.result['table']
                    elif self.op_mode == 'shell':
                        verbose = 'default'
                    else:
                        # Remove query
                        return None
                # If verbose is default
                if verbose == 'default':
                    # Check mode
                    if self.op_mode == 'check':
                        attribute = {
                            'filename': None,
                            'result': {
                                'built_query': None,
                                'diff': None
                            }
                        }
                        if not data.result['diff']:
                            return None
                        exclude = False
                    # Shell mode
                    elif self.op_mode in ['execute', 'shell']:
                        # With query results
                        if 'table' in data.result:
                            attribute = {
                                'result': {
                                    'table': None
                                }
                            }
                            exclude = False
                            # Remove execution time
                            data.result['table'].time = None
                        # No query results
                        else:
                            # Remove query
                            return None
                    # Audit mode
                    else:
                        # With query results
                        if data.result['table'].data:
                            attribute = {
                                'author': None,
                                'cstatement': None,
                                'error': None,
                                'name': None,
                                'reference': None,
                                'result': {
                                    'table': None
                                },
                                'statement': None,
                                'state': None
                            }
                            # Remove empty attributes
                            self.filter_empty(
                                data.result,
                                attribute,
                                'result',
                                ['table']
                            )
                            if 'nextsteps' in data.__dict__:
                                self.filter_empty(
                                    data.nextsteps,
                                    attribute,
                                    'nextsteps'
                                )
                            # Remove execution time
                            for stype in ['count', 'table']:
                                if stype in data.result:
                                    data.result[stype].time = None
                        # No query results
                        else:
                            # Remove query
                            return None
                # If verbose is debug
                elif verbose == 'debug':
                    # Check mode
                    if self.op_mode == 'check':
                        attribute = {
                            'filename': None,
                            'result': {
                                'built_query': None,
                                'diff': None
                            }
                        }
                        exclude = False
                    # Shell mode
                    elif self.op_mode in ['execute', 'shell']:
                        attribute = {
                            'cstatement': {
                                'table': None
                            },
                            'result': {
                                'table': None
                            }
                        }
                        exclude = False
                    # Audit mode
                    else:
                        attribute = {
                            'error': None
                        }

            qa = data.get(attribute, exclude)

            # Return the filtered query
            return qa

        # Format a string
        elif isinstance(data, str):
            if verbose != 'quiet':
                return data
            return None


    def filter_empty(self, data, attribute, key, exceptions = []):
        d = {}
        e = {}
        if data:
            for k, v in data.items():
                if k not in exceptions:
                    if v:
                        d[k] = None
                    else:
                        e[k] = None
        if d:
            if e:
                if key in attribute:
                    attribute[key].update(e)
                else:
                    attribute[key] = e
        else:
            attribute[key] = None


class Terminal(Presenter):


    def __init__(self, verbose, op_mode):
        Presenter.__init__(self, verbose, op_mode)

        self.built_query_sep = '·' * 64
        self.diff_sep = '-' * 8


    def diff(self, result):
        lines = ''
        for e in result:
            lines += f'{e["line"]}\n'
            lines += f'< {e["<"]}\n'
            lines += f'> {e[">"]}\n'
            lines += f'{self.diff_sep}\n'

        return lines


    def format(self, data, indent = ''):
        output = ''

        # Format an error
        if isinstance(data, Error):
            for error in data:
                output += f'{indent}- {error}\n'
            output += '\n'

        # Format a dict
        elif isinstance(data, dict):
            for key, value in data.items():
                output += f'{indent}- {key}:\n'
                if isinstance(value, str):
                    output = f'{output[:-1]} {self.format(value)}'
                elif key == 'result':
                    for k, v in value.items():
                        output += f'{indent}  - {k}:\n'
                        if k == 'built_query':
                            output += self.built_query_sep + '\n'
                            output += YAML().dump(v) + '\n'
                            output += self.built_query_sep + '\n'
                        elif k == 'diff':
                            output += self.diff(v)
                        elif k in ['table', 'count']:
                            output += self.fresult(v, f'{indent}    ')
                        elif k == 'graph':
                            output = f'{output[:-1]} {self.format(v)}'
                else:
                    output += f'{self.format(value, f"{indent}  ")}'

        # Format a Result
        elif isinstance(data, Result):
            output = self.fresult(data)

        # Format a list
        elif isinstance(data, list):
            for e in data:
                output += f'{indent}- {e}\n'

        # Format a string
        elif isinstance(data, str):
            if indent:
                indent = f'{indent}  '
            output = f'{indent}{data}\n'

        return output


    def fresult(self, result, indent = ''):
        if self.output_format == 'csv':
            output = CSV().dump(result.data)
        elif self.output_format == 'json':
            output = JSON().dump(result.data)
        elif self.output_format == 'yaml':
            output = YAML().dump(result.data)
        else:
            output = self.tablify(result.data, indent)
        output += '\n'
        if result.time:
            output += f'{indent}- execution time: {result.time}\n'
        return output


    def tablify(self, result, indent = ''):
        table = ''
        if result:
            key = result[0].keys()
            record = [list(row.values()) for row in result]
            tlp = PrettyTable()
            tlp.field_names = key
            for row in record:
                tlp.add_row(row)
            tlp.align = 'l'
            for line in tlp.get_string().split('\n'):
                table += f'{indent}{line}\n'
        return table[:-1]
