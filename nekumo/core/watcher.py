import pyinotify as pyinotify

from nekumo.api.base import NekumoNodeEvent, API
from nekumo.utils.filesystem import path_split_unix

class EventHandler(pyinotify.ProcessEvent):
    def __init__(self, nekumo, directory):
        super().__init__()
        self.nekumo = nekumo
        self.directory = directory

    def process_default(self, event):
        path = event.pathname.replace(self.directory, '')
        directory = path_split_unix(path)[0]
        action = event.maskname.replace('IN_', '').lower()
        # node = API(self.nekumo, path, 'info').get_instance().execute()
        self.nekumo.pubsub.fire(directory, NekumoNodeEvent(self.nekumo, path, action))


def init_watcher(nekumo, directory):
    # The watch manager stores the watches and provides operations on watches
    wm = pyinotify.WatchManager()
    notifier = pyinotify.ThreadedNotifier(wm, EventHandler(nekumo, directory))
    notifier.daemon = True
    notifier.start()
    mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE  # watched events
    wdd = wm.add_watch(directory, mask, rec=True)
