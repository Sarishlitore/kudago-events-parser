import json
import os.path

path = r'C:\Users\risha\PycharmProjects\parsing\results'


def save(data, file_name, encoding='utf-8'):
    with open(os.path.join(path, f'{file_name}.txt'), 'w', encoding=encoding) as file:
        for item in data:
            file.write(f'{item}\n')


def load(file_name):
    data = []
    with open(os.path.join(path, f'{file_name}.txt'), 'r') as file:
        lines = file.readlines()
        for line in lines:
            data.append(line.strip())
    return data


def json_dump(data, file_name):
    with open(os.path.join(path, f'{file_name}.json'), 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
