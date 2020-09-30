parser = {
    'ad': {
        'lang': 'en'
    },
    'check': {
        'persistence': {
            'format': 'yaml'
        }
    },
    'execute': {
        'mode': 'default',
        'persistence': {
            'format': 'csv'
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
