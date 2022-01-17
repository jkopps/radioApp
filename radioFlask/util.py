import string

class Resource:
    @staticmethod
    def remws(s):
        return ''.join(s.split())

    def _prefix(self):
        raise NotImplementedError()

    def _kind(self):
        raise NotImplementedError()

    def str(self):
        return '%s (%s)' % (self.name, self._kind())
    
    def __init__(self, name):
        self.name = name
        self.key = '%s_%s_%s' % (self.remws(self._prefix()),
                                 self.remws(name),
                                 self.remws(self._kind()))

