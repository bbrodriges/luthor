# luthor
A simple library to parse XML.

# About
Luthor utilizes all efficient tricks from [pholcidae](https://github.com/bbrodriges/pholcidae) to make XML parsing as simple as never before.
Luthor uses [lxml](https://github.com/lxml/lxml)'s iterable parsing mechanism to parse files of any size.

# Dependencies
* python 3
* lxml

# Basic example
```python
from luthor import Luthor


class MyParser(Luthor):

    def get_record(self, data):
        print(data)

settings = {
    'source': 'http://www.w3schools.com/xml/simple.xml',
    'tag': 'food',
    'threads': 3,
}

parser = MyParser()
parser.extend(settings)
parser.start()
```

# Allowed settings
Settings must be passed as dictionary to ```extend()``` method of the parser.

Params you can use:

**Required**

* **source** _string_ - a path to file or URL with XML content.
* **tag** _string_ - XML tag to start from.

**Additional**

* **threads** _int_ - number of threads of parser. Default: `1`
* **with_lock** _bool_ - wheither or not must parser use lock while data sync. It slightly decreases parsing speed but eliminates race conditions. Default: `True`
* **strip_namespaces** _bool_ - wheither or not must parser remove namespaces from tag names before return data. Default: `False`
* **start_line** _int_ - starting from which line parser will start to send results to callback function. Default: `1`

# Response attributes
While inherit Luthor class you can override built-in `get_record()` method to retrieve data gathered from tag.

* _attrs _dict_ - Attributes of tag. You can also use alias method ```attrs()```. Default: `{}`
* _content _str_ - Content of tag. You can also use alias method ```content()```. Default: `''`
* **child tags** - child tags includes into parent tag dict under corresponding keys. If there is only one child tag it will be dict, if there are multiple tags they would be list of dicts. 

# Tips and tricks
You can use ```last_line()``` parser method to get line number of last accessed tag as pass it again to new instance of parser in case of some fatal exception or error.