from .util import Provider, Resource

import json
from html.parser import HTMLParser
from urllib.request import urlopen

class Segment:
    def __init__(self, title, uri):
        self.title = title
        self.uri = uri

    def __str__(self):
        return "%s: %s" % (self.title, self.uri)

class MediaProvider(Provider):
    def __init__(self, name):
        Provider.__init__(self, name)
        
    def _prefix(self):
        return u'media'

    def getSegments(self):
        raise NotImplementedError()

class LiveStream(MediaProvider):
    def _kind(self):
        return 'Radio live stream'
    def __init__(self, program, uri, protocol_info):
        MediaProvider.__init__(self, program)
        self.protocol_info = protocol_info
        self.uri = uri
    def getSegments(self):
        return [Resource(self.name, self.uri, self.protocol_info)]

class NprProgram(MediaProvider):
    def _kind(self):
        return 'NPR on-demand program'

    @classmethod
    def _protocol_info(self):
        return 'x-rincon-playlist:*:*:*'
    
    def __init__(self, program, uri):
        MediaProvider.__init__(self, program)
        self.uri = uri
        self.protocol_info = self._protocol_info()

    class NprHTMLParser(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.inFullShow = False
            self.segments = []

        def handle_starttag(self, tag, attrs):

            if len(attrs) != 1:
                return
            (k, v) = attrs[0]

            if k == 'id' and v == 'full-show':
                self.inFullShow = True
                return

            if self.inFullShow == False or k != 'data-play-all':
                return

            j = json.loads(v)
            if 'audioData' not in j:
                raise KeyError

            for s in j['audioData']:
                self.segments.append((s['title'],s['audioUrl']))

        def handle_endtag(self, tag):
            self.inFullShow = False

        def handle_data(self, data):
            pass

    def getSegments(self):
        page = urlopen(self.uri)
        html = page.read().decode("utf-8")
        parser = self.NprHTMLParser()
        parser.feed(html)
        return [Resource(title, uri, self.protocol_info) 
                for (title, uri) in parser.segments]

resources = dict((obj.key, obj) for obj in (
    NprProgram('All Things Considered',
               'https://www.npr.org/programs/all-things-considered/'),
    NprProgram('Morning Edition',
               'https://www.npr.org/programs/morning-edition/'),
    LiveStream('WAMU',
               'aac://https://hd1.wamu.org/wamu-1.aac',
               'aac:*:application/octet-stream:*'),
))

def getAvailable():
    return sorted(resources.values(), key=lambda x: x.name)

def isAvailable(program):
    return program in resources

def getSegments(program):
    return resources[program].getSegments()

def getName(program):
    return resources[program].name
