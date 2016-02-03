# -*- coding: UTF-8 -*-

import os

from lxml import etree
from lxml.etree import XMLSyntaxError
from threading import Thread, Lock

from urllib import request
from urllib import parse


class Luthor:

    """ Luthor - simple XML parse library """

    _settings = {
        'source': None,
        'tag': None,
        'threads': 1,
        'with_lock': True,
    }

    def extend(self, settings):

        """
        Extends default settings using given settings.
        """

        self._settings.update(settings)

    def start(self):

        """
        Starts Luthor.
        """

        self.__prepare()
        self.__fetch_records()

    def get_record(self, response):

        """
        You may override this method in a subclass.
        Use it to get record content and parse it as you want to.
        """

        pass

    def __prepare(self):

        """
        Prepares everything before start.
        """

        if not self._settings['source']:
            raise Exception('No source specified')
        if not self._settings['tag']:
            raise Exception('No root tag specified')

        # getting storage instance
        self._storage = SyncStorage()

        # getting content and its type
        if parse.urlparse(self._settings['source']).netloc:
            self._content = request.urlopen(self._settings['source'])
        else:
            self._content = os.path.abspath(self._settings['source'])

        # storing callback
        self._callback = self.get_record

    def __fetch_records(self):

        """ Main fetch function """

        # creating lock
        lock = Lock() if self._settings['with_lock'] else DummyLock()

        # threads collection
        active_threads = []

        for i in range(self._settings['threads']):
            thread = Fetcher()
            thread.setup({
                'content': self._content,
                'tag': self._settings['tag'],
                'storage': self._storage,
                'lock': lock,
                'callback': self._callback,
            })
            thread.start()
            active_threads.append(thread)

        for thread in active_threads:
            thread.join()


class Fetcher(Thread):

    """ Fetches record from XML """

    def __init__(self):
        Thread.__init__(self)

    def setup(self, settings):

        """
        Sets up thread
        """

        self._content = settings['content']
        self._tag = settings['tag']
        self._storage = settings['storage']
        self._lock = settings['lock']
        self._callback = settings['callback']

    def run(self):

        """
        Runs content fetch and parse
        """

        try:
            for event, element in etree.iterparse(self._content, tag=self._tag):
                if not self._storage.is_parsed(element.sourceline):
                    # saving sourceline
                    with self._lock:
                        self._storage.add(element.sourceline)
                    # passing data to callback
                    self._callback(self.__to_dict(element))
                # removing element from memory
                element.clear()
        except XMLSyntaxError:
            pass

    def __to_dict(self, element):

        """
        Converts XML element to dict
        """

        children = {}
        for child in list(element):
            if child.tag not in children:
                children[child.tag] = []
            children[child.tag].append(self.__to_dict(child))

        return {
            "attributes": element.attrib,
            "children": children,
            "content": element.text.strip() if element.text else '',
        }


class SyncStorage:

    """ Stores shared info """

    def __init__(self):
        self._set = set()

    def add(self, value):

        """
        Adds value to storage
        """

        self._set.add(value)

    def is_parsed(self, value):

        """
        Checks if value has been already parsed
        """

        return value in self._set


class DummyLock:

    """ Dummy lock object """

    def acquire(self):
        pass

    def release(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass