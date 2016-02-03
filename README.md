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
Settings must be passed as dictionary to ```extend``` method of the parser.

Params you can use:

**Required**

* **source** _string_ - a path to file or URL with XML content.
* **tag** _string_ - XML tag to start from.

**Additional**

* **threads** _int_ - number of threads of parser. Default: `1`
* **with_lock** _bool_ - wheither or not must parser use lock while data sync. It slightly decreases parsing speed but eliminates race conditions. Default: `True`
* **strip_namespaces** _bool_ - wheither or not must parser remove namespaces from tag names before return data. Default: `False`

# Response attributes
While inherit Luthor class you can override built-in `get_record()` method to retrieve data gathered from tag.

* **children** _dict_ - Dict with chilren tag names as keys and lists of tags response attributes as values. Default: `{}`
* **attributes** _dict_ - Attributes of tag. Default: `{}`
* **content** _str_ - Content of tag. Default: `''`
