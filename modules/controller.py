from conf.constants import shell
from modules.error import Error
from modules.io import CSV, File, JSON, Neo4j, YAML
from modules.model import ActiveDirectory, Query, Result
from modules.view import Terminal as vTerminal
from os import path, walk
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from pygments.lexers.graph import CypherLexer
from sys import exit as sexit


class Controller:


    def __init__(self, args):

        self.ql = []
        self.error = Error()

        if args.op_mode == 'execute':
            self.op_mode = args.execute_mode
        else:
            self.op_mode = args.op_mode

        self.persistence = None


    def add(self, data, op_mode):
        q = Query(op_mode, data)
        if q.error:
            self.viewer.print(q)
        else:
            self.ql.append(q)


    def check(self):
        for query in self.ql:
            query.diff()

            self.viewer.print(query)

            if not query.error and self.persistence:
                self.dump(query)
                self.error_exists(self.persistence.error)


    def clean(self):
        self.ql.clear()


    def connect(self, args):

        # Neo4j
        self.neo = Neo4j(
                args.neo4j_host,
                args.neo4j_port,
                args.neo4j_username,
                args.neo4j_password,
                args.neo4j_encrypted
        )
        self.error_exists(self.neo.error)


    def dump(self, query = None):
        if query:
            for rtype in query.result:
                if rtype != 'graph':
                    result = query.result[rtype]
                    name, _ = path.splitext(path.basename(query.filename))
                    filename = f'{name}-{rtype}'
                    if rtype in ['table', 'count']:
                        result = result.data
                    elif rtype in ['built_query', 'diff']:
                        if rtype == 'built_query':
                            if not query.result['diff']:
                                break
                        elif not query.result[rtype]:
                            break
                    self.persistence.dump(result, filename)

        else:
            for q in self.ql:
                self.dump(q)


    def error_exists(self, error, _exit = True):
        if error:
            self.viewer.print(error)
            if _exit:
                sexit()
            return True
        return False


    def execute(self, query = None):
        if query:
            # Execute query
            query.compile(
                self.ad.get('domain'),
                self.ad.get('lang_vars')
            )
            if not query.error:
                for stype, csentence in query.csentence.items():
                    if stype != 'graph':
                        result = Result()
                        self.neo.execute(csentence)
                        if self.neo.error:
                            query.error.add(self.neo.error.get())
                            break
                        result.add(self.neo.result)
                        query.result[stype] = result
                    else:
                        query.result[stype] = csentence
        else:
            # Execute each query
            for q in self.ql:
                if q.state == 'enabled':
                    try:
                        self.execute(q)
                        self.viewer.print(q)
                        if not q.error and self.persistence:
                            self.dump(q)
                            self.error_exists(self.persistence.error)
                    except KeyboardInterrupt:
                        # ctrl+c
                        continue
                    except EOFError:
                        # ctrl+d
                        self.viewer.print()
                        break


    def load(self, data, op_mode):
        # Dictionary
        if isinstance(data, dict):
            self.add(data, op_mode)

        # Is a file
        elif path.isfile(data):
            filename = data
            _, extension = path.splitext(filename)
            if op_mode == 'raw':
                sentences = File().read(filename)
                if File.error:
                    self.error.add(File.error.get())
                else:
                    for sentence in sentences:
                        data = {
                            'filename': filename,
                            'sentence': {
                                'table': sentence
                            }
                        }
                        self.add(data, op_mode)
            elif extension == '.yaml':
                data = YAML().read(filename)
                if YAML.error:
                    self.error.add(YAML.error.get())
                else:
                    data['filename'] = filename
                    self.add(data, op_mode)

        # Is a directory
        else:
            directory = data
            for root, _, files in sorted(walk(directory)):
                if root[-1] == '/':
                    root = root[:-1]
                for filename in sorted(files):
                    self.load(f'{root}/{filename}', self.op_mode)


class Terminal(Controller):


    def __init__(self, args):
        Controller.__init__(self, args)

        # Terminal viewer
        self.viewer = vTerminal(args.verbose_mode, self.op_mode)

        # Connect to Neo4j database
        if self.op_mode != 'check':
            self.connect(args)

        # Shell mode
        if self.op_mode in ['command', 'interactive']:
            self.ad = ActiveDirectory()
            self.error_exists(self.ad.error)
            self.shell = Shell(self)
            # Command mode
            if self.op_mode == 'command':
                self.viewer.presenter.output_format = 'json'
                self.shell.execute(args.command)
            # Interactive mode
            elif self.op_mode == 'interactive':
                self.viewer.presenter.output_format = 'table'
                self.shell.interactive()

        # Non-shell mode (input from files)
        else:

            # Persistence
            if args.persistence_format == 'none':
                self.persistence = None
            else:
                if args.persistence_format == 'csv':
                    persistence = CSV
                elif args.persistence_format == 'json':
                    persistence = JSON
                elif args.persistence_format == 'yaml':
                    persistence = YAML
                self.persistence = persistence(args.output_directory)
                self.error_exists(self.persistence.error)

            # Load query list
            self.load(args.input_directory_or_file, self.op_mode)
            self.error_exists(self.error, False)

            # Check mode
            if self.op_mode == 'check':
                self.check()

            # Execution mode: test, raw or default (complete)
            else:
                self.ad = ActiveDirectory(args.ad_domain, args.ad_lang)
                self.error_exists(self.ad.error)
                self.viewer.presenter.output_format = args.output_format

                self.execute()


class Shell:


    def __init__(self, terminal):

        self.terminal = terminal

        self.commands = {
            'exit': {
                'help': shell['help']['exit']
            },
            'help': {
                'func': self.help,
                'help': shell['help']['help']
            },
            'match': {
                'func': self.match
            },
            'set': {
                'func': self.set,
                'help': shell['help']['set']
            }
        }

        self.query = {
            'filename': 'Interactive',
            'sentence': {
                'table': None
            }
        }


    def execute(self, command):
        if self.terminal.op_mode != 'interactive':
            self.commands.pop('exit')
            self.commands.pop('help')

        for c in command.split(';'):
            c = c.strip()
            if c:
                c = c.split()
                if c[0] in self.commands:
                    self.commands[c[0]]['func'](c)


    def get_input(self):

        multiline = bool(self.multiline == 'on')

        completer = NestedCompleter.from_nested_dict(self.menu)

        # ff0000 = red color
        style = Style.from_dict({'prompt': '#ff0000'})
        prompt = [('class:prompt', '> ')]

        session = PromptSession(history = FileHistory(self.history_file))
        return session.prompt(
            prompt,
            auto_suggest = AutoSuggestFromHistory(),
            complete_in_thread = True,
            completer = completer,
            lexer = PygmentsLexer(CypherLexer),
            multiline = multiline,
            style = style,
            vi_mode = True
        )


    def help(self, _):
        self.terminal.viewer.print('Commands:')
        for command in self.commands:
            if 'help' in self.commands[command]:
                h = self.commands[command]['help']
                self.terminal.viewer.print(f'- {command}: {h}')

        self.terminal.viewer.print('\nMatch Query:')
        self.terminal.viewer.print(f'  {shell["help"]["query"]}')
        self.terminal.viewer.print()


    def interactive(self):

        self.load()

        command = ''

        while command not in ['e', 'exit', 'q', 'quit']:
            try:
                self.execute(command)
                command = self.get_input().strip()
            except KeyboardInterrupt:
                # ctrl+c
                command = ''
                continue
            except EOFError:
                # ctrl+d
                break


    def load(self):

        self.menu = shell['menu']
        self.history_file = shell['history']
        self.multiline = 'off'
        self.terminal.viewer.presenter.output_format = 'table'


    def match(self, command):
        sentence = ' '.join(command)
        self.query['sentence']['table'] = sentence
        self.terminal.load(self.query, 'raw')
        self.terminal.error_exists(self.terminal.error, False)
        self.terminal.execute()
        self.terminal.clean()
        self.terminal.viewer.print()


    def set(self, command):

        if len(command) == 1:
            for k, v in self.terminal.ad.get().items():
                self.terminal.viewer.print(f'{k} = {v}')
            self.terminal.viewer.print(f'multiline = {self.multiline}')
            output_format = self.terminal.viewer.presenter.output_format
            self.terminal.viewer.print(f'output = {output_format}')
            self.terminal.viewer.print()

        elif len(command) == 3:

            if command[1] in ['domain', 'lang']:
                self.terminal.ad.set(command[1], command[2])

            elif command[1] == 'multiline':
                if command[2] in shell['menu']['set']['multiline']:
                    self.multiline = command[2]

            elif command[1] == 'output':
                if command[2] in shell['menu']['set']['output']:
                    self.terminal.viewer.presenter.output_format = command[2]
