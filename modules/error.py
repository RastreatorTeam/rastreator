class Error:


    def __init__(self):
        self.data = []


    def __bool__(self):
        return bool(self.data)


    def __iter__(self):
        el = self.data
        self.data = []
        return iter(el)


    def add(self, error):
        if isinstance(error, str):
            self.data.append(error)
        elif isinstance(error, list):
            self.data += error


    def clean(self):
        self.data = []


    def get(self):
        el = self.data
        self.clean()
        return el
