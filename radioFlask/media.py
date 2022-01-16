import json
from html.parser import HTMLParser
from urllib.request import urlopen

class Segment:
    def __init__(self, title, uri):
        self.title = title
        self.uri = uri

    def __str__(self):
        return "%s: %s" % (self.title, self.uri)

class Resource:
    def __init__(self, name, key):
        self.name = name
        self.key = key
    def getSegments(self):
        raise NotImplementedError()

class NprProgram(Resource):
    def __init__(self, program, key, url):
        Resource.__init__(self, program, key)
        self.url = url

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
                self.segments.append(Segment(s['title'], s['audioUrl']))

        def handle_endtag(self, tag):
            self.inFullShow = False

        def handle_data(self, data):
            pass

    def getSegments(self):
        page = urlopen(self.url)
        html = page.read().decode("utf-8")
        parser = self.NprHTMLParser()
        parser.feed(html)
        return parser.segments

resources = (
    NprProgram('NPR All Things Considered',
               'npr_atc',
               'https://www.npr.org/programs/all-things-considered/'),
    NprProgram('NPR Morning Edition',
               'npr_morning',
               'https://www.npr.org/programs/morning-edition/'),
)

resourcesMap = dict((obj.key, obj) for obj in resources)

def available():
    return resources

def isAvailable(program):
    return program in resourcesMap

def getSegments(program):
    return resourcesMap[program].getSegments()
