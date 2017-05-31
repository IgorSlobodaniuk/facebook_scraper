import re
import random
import requests
import csv
from pyexcel_xlsx import get_data
from time import sleep
from xlsxwriter.workbook import Workbook

import sys

reload(sys)
sys.setdefaultencoding('utf8')


CREDENTIALS_LIST = ['1318151578265722|8af8c5e756731c09ebcfaf8829103fc0']


PID_API = 'https://graph.facebook.com/%s?' \
          'access_token=1318151578265722|8af8c5e756731c09ebcfaf8829103fc0'

LIKES_API = 'https://graph.facebook.com/{}/feed?' \
            'access_token={}&' \
            'since={}&' \
            'fields=likes{link},link,created_time&' \
            'limit=100'

F_ID_RE = re.compile('"page_id":(\d+),')


class LikesScrapes():
    def __init__(self, input_file_name, i_f_number, since):
        self.input_file = './input_files/{}'.format(input_file_name)
        self.output_scv = './output_files/{}.csv'.format(input_file_name.split('.')[0])
        self.output_file = './output_files/output_{}'.format(input_file_name)
        self.input_url_number_in_file = i_f_number
        self.since = since

    def main(self):
        print 'Started'
        input_data = get_data(self.input_file)
        self._write_to_csv(input_data)
        self._write_to_output_file(self.output_scv, self.output_file)

    def _write_to_csv(self, input_data):
        with open(self.output_scv, 'w') as otput_scv:
            titles = input_data['Sheet1'][0]
            otput_scv.write(','.join(titles) + '\n')
            print 'found {} input URLs'.format(input_data['Sheet1'][1:])
            for n, i in enumerate(input_data['Sheet1'][1:]):
                print '{}  URL: {}'.format(n, i[self.input_url_number_in_file])
                fid = self._get_f_id(i[self.input_url_number_in_file])
                if not fid:
                    otput_scv.write('{},{}\n'.format(','.join(i), 'Problematic source'))
                    print 'input URL {} is problematic'.format(i[self.input_url_number_in_file])
                    continue
                token = random.choice(CREDENTIALS_LIST)
                api_data = requests.get(LIKES_API.format(fid, self.since, token) % fid).json()
                if api_data.get('error'):
                    otput_scv.write('{},{}\n'.format(','.join(i), 'Problematic source'))
                    print 'input URL {} is problematic'.format(i[self.input_url_number_in_file])
                    continue
                sleep(random.choice(range(0, 1)))

                for r in self._get_posts_data(api_data, i):
                    otput_scv.write(r + '\n')
            print 'Finished'

    def _get_posts_data(self, data, input_url_data, all_data=None):
        all_data = [] if all_data is None else all_data

        if data.get('data'):
            for p in data['data']:
                all_data.append(p)

        next_page = data['paging'].get('next') if data.get('paging') else None

        if not next_page:
            links = []
            attrs = {}
            for i in all_data:
                attrs['post_url'] = i.get('link', i['id'])
                attrs['post_time'] = i['created_time'].split('T')[0]
                post_likes = self._collect_likers(i, input_url_data, **attrs)
                links.extend(post_likes)
            return links
        else:
            sleep(random.choice(range(0, 1)))
            next_data = requests.get(next_page.replace('limit=25', 'limit=100')).json()
            return self._get_posts_data(next_data, input_url_data, all_data)

    def _collect_likers(self, data, input_url_data, all_links=None, **attrs):

        if all_links is None:
            all_links = []
        likers = data['likes']['data'] if data.get('likes') else []
        for i in likers:
            if 'scoped_user_id' not in i['link']:
                continue
            s = ','.join(input_url_data)
            print s + ',{}'.format(i['link'])
            all_links.append(s + ',{}'.format(i['link']))

        next_page = data['paging'].get('next') if data.get('paging') else None
        if not next_page:
            return all_links
        else:
            sleep(random.choice(range(0, 1)))
            next_data = requests.get(next_page.replace('limit=25', 'limit=100')).json()
            return self._collect_likers(next_data, input_url_data, all_links, **attrs)

    def _write_to_output_file(self, output_csv, output_file):
        with open(output_csv, 'r') as otput_scv:
            workbook = Workbook(output_file, {'strings_to_urls': False})
            worksheet = workbook.add_worksheet()
            reader = csv.reader(otput_scv)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    worksheet.write(r, c, col.encode('utf-8'))
            workbook.close()

    def _get_f_id(self, url):

        if '/groups/' in url:
            return url.split('/groups/')[-1].split('/')[0]
        try:
            data = requests.get(PID_API % url.strip().strip('?ref=br_rs')).json()
            pid = data.get('id')
            return pid
        except:
            return

    def _get_input_links(self, data):
        links = []
        for l in data:
            links.extend([i for i in l if i and 'https:' in i])

        return tuple(set(links))


a = LikesScrapes('Part ALL.xlsx', 4, '2017-04-18')
a.main()
