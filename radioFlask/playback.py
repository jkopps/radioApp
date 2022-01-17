import soco
from soco.data_structures import DidlResource, DidlObject

def queueAudio(segments, play=True, clearQueue=False):
    speakers = soco.discovery.discover()
    spkr = speakers.pop()

    if clearQueue:
        spkr.stop()
        spkr.clear_queue()

    pos = len(spkr.get_queue())

    for seg in segments:
        # add_uri_to_queue doesn't accept an alternate title argument, though sonos doesn't seem to make use of this anyway
        # spkr.add_uri_to_queue(seg.uri)
        res = [DidlResource(uri=seg.uri, protocol_info="x-rincon-playlist:*:*:*")]
        item = DidlObject(resources=res, title=seg.title, parent_id="", item_id="")
        spkr.add_to_queue(item, position=0, as_next=False)
        print('Queued story "%s"' % seg.title)

    if play:
        spkr.play_from_queue(pos)
