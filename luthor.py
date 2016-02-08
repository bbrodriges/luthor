# -*- coding: UTF-8 -*-

import os
import re

from collections import Counter

from lxml import etree
from lxml.etree import XMLSyntaxError
from threading import Thread, Lock

from urllib import request
from urllib import parse

__version__ = '1.2.6'


class Luthor:

    """ Luthor - simple XML parse library """

    _settings = {
        'source': None,
        'tag': None,
        'threads': 1,
        'with_lock': True,
        'strip_namespaces': False,
        'start_line': 0,
    }

    _last_line = 0

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
                'strip_namespaces': self._settings['strip_namespaces'],
                'last_line_fn': self.__set_last_line,
                'start_line': self._settings['start_line']
            })
            thread.start()
            active_threads.append(thread)

        for thread in active_threads:
            thread.join()

    def __set_last_line(self, lineno):

        """
        Sets last line no.
        """

        self._last_line = lineno

    def last_line(self):

        """
        Gets last line no.
        """

        return self._last_line


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
        self._strip_namespaces = settings['strip_namespaces']
        self._last_line_fn = settings['last_line_fn']
        self._start_line = settings['start_line']

        self._strip_ns_re = re.compile(r'({.*?})')

    def run(self):

        """
        Runs content fetch and parse
        """

        try:
            for event, element in etree.iterparse(self._content, tag=self._tag):
                if element.sourceline >= self._start_line and not self._storage.is_parsed(element.sourceline):
                    # saving sourceline
                    with self._lock:
                        self._storage.add(element.sourceline)
                        self._last_line_fn(element.sourceline)
                    # passing data to callback
                    self._callback(self.__get_result(element))
                # removing element from memory
                element.clear()
        except XMLSyntaxError:
            pass

    def __get_result(self, element):

        """
        Converts XML element to dict
        """

        children_elements = list(element)

        children = dict()
        for child in children_elements:
            tag = self.__strip_namespaces(child.tag)
            if tag not in children:
                children[tag] = Tags()
            children[tag].append(self.__get_result(child))

        attributes = {}
        for key, value in element.attrib.items():
            name = self.__strip_namespaces(key)
            attributes[name] = value

        result = Result()
        result.update({
            "_attrs": attributes,
            "_content": element.text.strip() if element.text else '',
        })
        result.update(children)

        return result

    def __strip_namespaces(self, text):

        """
        Strips namespaces
        """

        return text if not self._strip_namespaces else re.sub(self._strip_ns_re, '', text)


class Result(dict):

    """ Dict-like object with special methods """

    def content(self):

        """
        Get content
        """

        return self.__getitem__('_content')

    def attrs(self):

        """
        Get attrs
        """

        return self.__getitem__('_attrs')

    def attr(self, key):

        """
        Get attr
        """

        return self.__getitem__('_attrs')[key]

    def __iter__(self):
        for key in self.keys():
            yield key

    def keys(self):
        return [key for key in super().keys() if key not in ['_attrs', '_content']]

    def items(self):
        return [(key, value) for key, value in super().items() if key not in ['_attrs', '_content']]


class Tags(list):

    """ List-like object with special methods """

    def content(self):

        """
        Get content
        """

        return super().__getitem__(0).content()

    def attrs(self):

        """
        Get attrs
        """

        return super().__getitem__(0).attrs()

    def attr(self, key):

        """
        Get attr
        """

        return super().__getitem__(0).attr(key)

    def children(self, key):

        """
        Get children of first tag
        """

        return super().__getitem__(0)[key]

    def child(self, key):

        """
        Alias to children
        """

        return self.children(key)


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
