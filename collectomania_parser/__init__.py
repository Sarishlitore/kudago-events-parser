import app
from collectomania_parser.collectomania_vinyl_parser import CollectomaniaVinylParser
from fstream import file


def main():
    coll_parser = CollectomaniaVinylParser(app.headers)
    coll_parser.parse()
    file.json_dump(coll_parser.get_vinyls(), 'vinyls')


if __name__ == '__main__':
    main()
