parser = {
    'ad': {
        'lang': 'en'
    },
    'audit': {
        'start_node': '',
        'mode': 'default',
        'persistence': {
            'format': 'csv'
        },
        'end_node': '',
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
        'encrypted': 'on',
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
