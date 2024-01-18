import base64
import string
from .util import Provider

import soco
from soco.data_structures import DidlResource, DidlObject

class Player(Provider):
    def __init__(self, name):
        Provider.__init__(self, name)
    def _prefix(self):
        return 'Player'
    def queueAudio(self, audio):
        raise NotImplementedError()

class SonosSpeaker(Player):
    def __init__(self, name, handle):
        Player.__init__(self, name)
        self.handle = handle
    def _kind(self):
        return 'Sonos'

    def queueAudio(self, segments, play=True, clearQueue=False):

        if clearQueue:
            self.handle.stop()
            self.handle.clear_queue()

        pos = len(self.handle.get_queue())

        for seg in segments:
            # add_uri_to_queue doesn't accept an alternate title argument, though sonos doesn't seem to make use of this anyway
            # spkr.add_uri_to_queue(seg.uri)
            uri = seg.uri
            if not seg.uri.startswith('http'):
                try:
                    uri = str(base64.urlsafe_b64decode(seg.uri), 'utf-8')
                    print("Alternative URI: %s (type %s" % (uri, type(uri)))
                except:
                    pass
            if not uri.startswith('http'):
                print("Could not decode URI %s" % seg.uri)
                continue

            try:
                res = [DidlResource(uri=uri, protocol_info="x-rincon-playlist:*:*:*")]
                item = DidlObject(resources=res, title=seg.title, parent_id="", item_id="")
                self.handle.add_to_queue(item, position=0, as_next=False)
            except:
                print('Failed to queue story "%s" @ %s' % (seg.title, seg.uri))
                continue

        if play:
            self.handle.play_from_queue(pos)

def discover():
    names = set()
    resources = {}
    speakers = soco.discovery.discover()
    for spkr in speakers:
        name = spkr.player_name
        if name in resources:
            raise ValueError('Non-unique player name: "%s"' % name)
        obj = SonosSpeaker(name, spkr)
        resources[obj.key] = obj
    return resources

def getAvailable():
    resources = discover()
    return sorted(resources.values(), key=lambda x: x.name)

def isAvailable(name):
    return name in resources

def queueAudio(name, segments, playNow, clearQueue):
    resources[name].queueAudio(segments, playNow, clearQueue)

resources = discover()
