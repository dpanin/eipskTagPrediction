import json
from math import ceil
from re import sub
from urllib.request import urlopen
from queue import Queue
from threading import Thread


keys = ['_id', 'description', 'isFree', 'name',
        'tags', 'ageRestriction', ['category', 'sysName']]
stop_words = []
processed_data = []


def get_data(link):
    json_data = urlopen(link)
    json_data = json_data.read().decode('utf-8')
    json_data = json.loads(json_data)
    return json_data


def data_processing(json_data):
    output_data = []
    for event in json_data['events']:
        if event['tags'] != []:
            output_data.append({})
            for key in keys:
                if key == 'tags':
                    # Добавляем теги в список tags
                    output_data[-1]['tags'] = []
                    for tag in event['tags']:
                        output_data[-1]['tags'].append(tag['name'])
                    # Добавляем латинские теги в список tags_system
                    output_data[-1]['tags_system'] = []
                    for tag in event['tags']:
                        output_data[-1]['tags_system'].append(tag['sysName'])
                elif key == 'description':
                    for i in stop_words:
                        if i in event[key]:
                            event[key] = event[key].replace(i, '')
                    output_data[-
                                1][key] = sub('[!@#$.,:;?\'"]', '', event[key])
                elif isinstance(key, list):
                    # Если более 1 вложенного ключа, то создаем внутри словарь.
                    if len(key) > 2:
                        # Если вложенный список, то значение ключа = словарь.
                        output_data[-1][key[0]] = {}
                        for index in range(1, len(key)):
                            # В словарь добавляем требуемые значения.
                            output_data[-1][key[0]][
                                key[index]] = event[key[0]][key[index]]
                    else:
                        output_data[-1][key[0]] = event[key[0]][key[1]]
                else:
                    output_data[-1][key] = event[key]
    return output_data


def save_data(data):
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


class DownloadWorker(Thread):

    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            number, link = self.queue.get()
            print(number+1)
            data = get_data(link)
            for i in data_processing(data):
                processed_data.append(i)
            self.queue.task_done()


def main():
    queue = Queue()
    for x in range(8):
        worker = DownloadWorker(queue)
        # Setting daemon to True will let the main thread exit even though the
        # workers are blocking
        worker.daemon = True
        worker.start()
    query = json.loads(urlopen(
        'https://all.culture.ru/api/2.2/events?limit=1&offset=0'
    ).read().decode('utf-8'))
    query = ceil(int(query['total'])/100)
    for i in range(query):
        queue.put(
            (i, 'https://all.culture.ru/api/2.2/events?limit=100&offset={0}'.format(i*100)))
    queue.join()
    save_data(processed_data)
    print('Done')


if __name__ == '__main__':
    main()
