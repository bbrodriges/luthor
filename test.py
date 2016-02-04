from luthor import Luthor


class MyParser(Luthor):

    def get_record(self, data):
        print(data, data['name'].content(), data['name'].attrs())

settings = {
    'source': 'http://www.w3schools.com/xml/simple.xml',
    'tag': 'food',
    'threads': 3,
}

parser = MyParser()
parser.extend(settings)
parser.start()
