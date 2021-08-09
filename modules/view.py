from conf.constants import banner
from modules.error import Error
from modules.presenter import Terminal as pTerminal


class Terminal:


    def __init__(self, verbose, op_mode):
        self.op_mode = op_mode
        self.output = ''
        self.presenter = pTerminal(verbose, op_mode)
        self.query_sep = '\n' * 5
        self.verbose = verbose

        self.print(f'{banner}')
        self.print('')


    def print(self, data = ''):
        sep = False
        if isinstance(data, list):
            for query in data:
                self.print(query)
            return
        # Query or str
        if not isinstance(data, Error):
            if 'Query' in type(data).__name__:
                sep = True
            data = self.presenter.filter(data)
        self.output += self.presenter.format(data)
        if self.verbose != 'quiet' and self.op_mode != 'shell':
            if sep and self.output:
                self.output += self.query_sep

        print(self.output, end = '', flush = True)
        self.output = ''
