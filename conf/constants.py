banner = f'Rastreator\n > Tool with a collection of query files to explore Microsoft Active Directory\n > Developed by @interh4ck and @t0-n1'


error = {
    'compile': {
        'pattern': 'Compiling {type} query: Wrong regex "{pattern}" - {e}'
    },
    'csv': {
        'dump': 'Dumping CSV to: {e}',
        'save': 'Saving CSV to {filename}: {e}'
    },
    'file': {
        'open': 'Opening {filename} in {mode} mode: {e}',
        'read': 'Reading {filename}: {e}'
    },
    'json': {
        'dump': 'Dumping JSON: {e}',
        'save': 'Saving JSON to {filename}: {e}'
    },
    'neo4j': {
        'connect': 'Connecting to Neo4j: {e}',
        'execute': 'Executing cstatement: {statement} - {e}',
        'interrupted': 'Interrupted (ctrl+c) cstatement: {statement}'
    },
    'parse': {
        'key': 'Parsing query format: "{key}" key is not set',
        'object': 'Parsing query format: "{bad}" is not a good object value for "{key}" key. Expected a "{good}" object',
        'value': 'Parsing query format: "{value}" value is not valid for "{key}" key'
    },
    'yaml': {
        'dump': 'Dumping YAML: {e}',
        'read': 'Reading YAML {filename}: {e}',
        'save': 'Saving YAML to {filename}: {e}'
    }
}


parser = {
    'choices': {
        'ad': {
            'lang': ['en', 'es', 'fr']
        },
        'audit': {
            'persistence': {
                'format': ['csv', 'json', 'none', 'yaml']
            }
        },
        'check': {
            'persistence': {
                'format': ['none', 'yaml']
            }
        },
        'neo4j': {
            'encrypted': ['false', 'true']
        },
        'output': {
            'format': ['csv', 'json', 'table', 'yaml']
        },
        'path': {
            'has_session': ['false', 'true'],
            'persistence': {
                'format': ['csv', 'json', 'none', 'yaml']
            }
        },
        'query': {
            'mode': ['raw', 'test', 'default']
        },
        'verbose': {
            'mode': ['quiet', 'default', 'debug']
        }
    },
    'help': {
        'ad': {
            'domain': 'Active Directory domain name',
            'lang': 'Active Directory language'
        },
        'execute': {
            'command': 'Semicolon separated commands inside single/double quotes'
        },
        'input': {
            'directory_or_file': 'Input directory or specific query file'
        },
        'neo4j': {
            'encrypted': 'Neo4j encrypted communication',
            'host': 'Neo4j host to connect',
            'password': 'Neo4j password', 
            'port': 'Neo4j port to connect',
            'username': 'Neo4j username'
        },
        'output': {
            'format': 'Output format to show executed query results on screen',
            'directory': 'Output directory to save results'
        },
        'path': {
            'has_session': 'Accept paths with HasSession',
            'start_node': 'Start node of the path',
            'end_node': 'End node of the path'
        },
        'query': {
            'mode': 'Query submode'
        },
        'persistence': {
            'format': 'File format to save executed query results'
        },
        'verbose': {
            'mode': 'Verbose mode'
        }
    }
}


shell = {
    'help': {
        'clean': 'base nodes',
        'exit': 'this program (ctrl+d)',
        'help': 'shows this help',
        'set': 'the environment variables',
        'query': 'Example: > match (u:User{enabled:true}) return u.name limit 10'
    },
    'history': '.shell_history',
    'menu': {
        'clean': None,
        'exit': None,
        'help': None,
        'set': {
            'domain': None,
            'lang': {},
            'multiline': {
                'false': None,
                'true': None
            },
            'output': {},
        }
    }
}


for e in parser['choices']['ad']['lang']:
    shell['menu']['set']['lang'][e] = None

for e in parser['choices']['output']['format']:
    shell['menu']['set']['output'][e] = None
