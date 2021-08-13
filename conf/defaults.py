parser = {
    'ad': {
        'lang': 'en'
    },
    'audit': {
        'end_node': '',
        'has_session': 'false',
        'mode': 'default',
        'persistence': {
            'format': 'csv'
        },
        'start_node': ''
    },
    'check': {
        'persistence': {
            'format': 'yaml'
        }
    },
    'input': {
        'directory_or_file': 'queries'
    },
    'neo4j': {
        'encrypted': 'true',
        'host': 'localhost',
        'password': 'neo4j', 
        'port': '7687',
        'username': 'neo4j'
    },
    'output': {
        'directory': 'output',
        'format': 'table'
    },
    'verbose': {
        'mode': 'default'
    }
}
