import json
from math import ceil
import re
import urllib.request

output_data = []
keys = ['_id', 'description', 'isFree', 'name',
        'tags', 'ageRestriction', ['category', 'sysName']]
query = json.loads(urllib.request.urlopen(
    'https://all.culture.ru/api/2.2/events?limit=1&offset=0'
    ).read().decode('utf-8'))
query = ceil(int(query['total'])/100)  # Округление в бОльшую сторону.
for i in range(query):
    print('Выполняю запрос {0} из {1}'.format(i+1, query))
    json_data = urllib.request.urlopen(
        'https://all.culture.ru/api/2.2/events?limit=100&offset={0}'.format(i))
    json_data = json_data.read().decode('utf-8')
    json_data = json.loads(json_data)
    for event in json_data['events']:
        if event['tags'] != []:
            output_data.append({})
            for key in keys:
                if key == 'tags':
                    # Добавляем имена тегов в список
                    output_data[-1]['tags'] = []
                    for tag in event['tags']:
                        output_data[-1]['tags'].append(tag['name'])
                elif key == 'description':
                    output_data[-1][key] = re.sub('[!@#$.,:;?\'"]', '', event[key])
                elif isinstance(key, list):
                    # Если вложенный список, то значение ключа = словарь.
                    output_data[-1][key[0]] = {}
                    for index in range(1, len(key)):
                        # В словарь добавляем требуемые значения.
                        output_data[-1][key[0]][key[index]
                                                ] = event[key[0]][key[index]]
                else:
                    output_data[-1][key] = event[key]
print('Записываю в файл.')
with open('output.json', 'w') as f:
    json_output = json.dump({'events': output_data}, f, ensure_ascii=False)
