import json
import re
import random
import requests
import csv
from pyexcel_xlsx import get_data, save_data
from time import sleep
from collections import OrderedDict
from xlsxwriter.workbook import Workbook


FEED_URL = 'https://www.dropbox.com/s/1avucuy5zs2a7wc/Pages & Groups Analysis Quo Use V.2.xlsx?' \
       '_download_id=038177759136897694518006274979411474180122286806755418256791666272' \
       '&_notify_domain=www.dropbox.com&dl=1'

LIKES_API = 'https://graph.facebook.com/%s/feed?' \
            'access_token=1318151578265722|8af8c5e756731c09ebcfaf8829103fc0&' \
            'since=2017-01-01&' \
            'fields=likes{link},link,created_time&limit=100'

F_ID_RE = re.compile('"page_id":(\d+),')


class LikesScrapes():
    def main(self):
        self._save_feed_data()
        input_data = get_data('input_data.xlsx')
        with open('output_file.csv', 'w') as otput_scv:
            otput_scv.write('{},{},{},{}'.format('Groups or pages', 'Post links', 'Post date', 'Profile link') + '\n')
            for i in self._get_input_links(input_data['Sheet1'])[:5]:
                fid = self._get_f_id(i)
                if not fid:
                    otput_scv.write('{},null,null,null'.format(i) + '\n')
                    continue
                api_data = requests.get(LIKES_API % self._get_f_id(i)).json()
                if api_data.get('error'):
                    otput_scv.write('{},null,null,null'.format(i) + '\n')
                    continue
                sleep(random.choice(range(1, 2)))
                for r in self._get_posts_data(api_data, i):
                    otput_scv.write(r + '\n')

            workbook = Workbook('csvfile.xlsx')
            worksheet = workbook.add_worksheet()

        with open('output_file.csv', 'r') as otput_scv:
            reader = csv.reader(otput_scv)
            for r, row in enumerate(reader):
                print r
                for c, col in enumerate(row):
                    worksheet.write(r, c, col)
            workbook.close()

    def _get_posts_data(self, data, input_url, all_data=None):
        all_data = [] if all_data is None else all_data

        if data.get('data'):
            for p in data['data']:
                all_data.append(p)

        next_page = data['paging'].get('next') if data.get('paging') else None
        if not next_page:
            links = []
            for i in all_data:
                post_url = i.get('link', i['id'])
                post_time = i['created_time']
                post_likes = self._collect_likers(i, input_url, post_url, post_time)
                links.extend(post_likes)
            return links
        else:
            sleep(random.choice(range(1, 2)))
            next_data = requests.get(next_page.replace('limit=25', 'limit=100')).json()
            return self._get_posts_data(next_data, input_url, all_data)

    def _collect_likers(self, data, input_url, post_url, post_time, all_links=None):

        if all_links is None:
            all_links = []
        likers = data['likes']['data'] if data.get('likes') else []
        for i in likers:
            all_links.append('{},{},{},{}'.format(input_url, post_url, post_time, i['link']))
        next_page = data['paging'].get('next') if data.get('paging') else None
        if not next_page:
            return all_links
        else:
            sleep(random.choice(range(1, 2)))
            next_data = requests.get(next_page.replace('limit=25', 'limit=100')).json()
            return self._collect_likers(next_data, input_url, post_url, post_time, all_links)

    def _save_feed_data(self):
        with open('input_data.xlsx', 'w') as f:
            f.write(requests.get(FEED_URL).content)

    def _get_f_id(self, url):
        if '/groups/' in url:
            return url.split('/groups/')[-1].split('/')[0]
        data = requests.get(url).content

        r = re.search(F_ID_RE, data)
        if r:
            return r.group(1)

    def _get_input_links(self, data):
        links = []
        for l in data:
            links.extend([i for i in l if i and 'https:' in i])

        return tuple(set(links))

a = LikesScrapes()
print a.main()
