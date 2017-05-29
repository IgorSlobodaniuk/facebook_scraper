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


CREDENTIALS_LIST = ['', '']


PID_API = 'https://graph.facebook.com/%s?access_token=1318151578265722|8af8c5e756731c09ebcfaf8829103fc0'

LIKES_API = 'https://graph.facebook.com/%s/feed?' \
            'access_token=1318151578265722|8af8c5e756731c09ebcfaf8829103fc0&' \
            'since=2017-04-18&' \
            'fields=likes{link},link,created_time&limit=100'

F_ID_RE = re.compile('"page_id":(\d+),')


class LikesScrapes():

    def __init__(self, input_file_name):
        self.input_file = './input_files/{}'.format(input_file_name)
        self.output_scv = './output_files/{}.csv'.format(input_file_name.split('.')[0])
        self.output_file = './output_files/output_{}'.format(input_file_name)

    def main(self):
        input_data = get_data(self.input_file)
        self._write_to_csv(input_data)
        self._write_to_output_file()

    def _write_to_csv(self, input_data):
        with open(self.output_scv, 'w') as otput_scv:
            titles = input_data['Sheet1'][0]
            otput_scv.write(','.join(titles) + '\n')
            for i in self._get_input_links(input_data['Sheet1'][1:]):
                fid = self._get_f_id(i)
                if not fid:
                    otput_scv.write('{},{}{}'.format(','.join(titles[:-1]), 'Problematic source', '\n'))
                    continue
                api_data = requests.get(LIKES_API % fid).json()
                if api_data.get('error'):
                    otput_scv.write('{},{}{}'.format(','.join(titles[:-1]), 'Problematic source', '\n'))
                    continue
                sleep(random.choice(range(0, 1)))
                for r in self._get_posts_data(api_data, i):
                    otput_scv.write(r + '\n')

    def _get_posts_data(self, data, input_url, all_data=None):
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
                attrs['post_time'] = i['created_time']
                post_likes = self._collect_likers(i, input_url, **attrs)
                links.extend(post_likes)
            return links
        else:
            sleep(random.choice(range(0, 1)))
            next_data = requests.get(next_page.replace('limit=25', 'limit=100')).json()
            return self._get_posts_data(next_data, input_url, all_data)

    def _collect_likers(self, data, input_url, all_links=None, **attrs):

        if all_links is None:
            all_links = []
        likers = data['likes']['data'] if data.get('likes') else []
        for i in likers:
            if 'scoped_user_id' not in i['link']:
                continue

            all_links.append('{},{},{},{}'.format(input_url, attrs['post_url'].encode('utf-8'), attrs['post_time'].split('T')[0], i['link']))

        next_page = data['paging'].get('next') if data.get('paging') else None
        if not next_page:
            return all_links
        else:
            sleep(random.choice(range(0, 1)))
            next_data = requests.get(next_page.replace('limit=25', 'limit=100')).json()
            return self._collect_likers(next_data, input_url, all_links, **attrs)


    def _write_to_output_file(self):
        with open('output8.csv', 'r') as otput_scv:
            workbook = Workbook('output8.xlsx', {'strings_to_urls': False})
            worksheet = workbook.add_worksheet()
            reader = csv.reader(otput_scv)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    worksheet.write(r, c, col.encode('utf-8'))
            workbook.close()


########################################################################################################################
########################################################################################################################

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

    def _get_prew_output_links(self):

        # with open('output_old.csv', 'w') as old_scv:
        #     input_data = get_data('csvfile.xlsx')
        #     for i in input_data['Sheet1'][1:]:
        #         old_scv.write(i[-1] + '\n')

        f = open('output_old.csv', 'r').readlines()
        f = tuple(set(f))
        f = [g.strip('\n') for g in f]

        print len(f)


        # with open('output_current.csv', 'w') as current_scv:
        #     i_data = get_data('output_data_2_fixed (copy).xlsx')
        #     print len(i_data['Sheet1'][1:])
        #     for i in i_data['Sheet1'][1:]:
        #         current_scv.write(','.join(i) + '\n')

        with open('v', 'r') as final_scv:

            u_l = []

            with open('duplicates.csv', 'w') as o_scv:

                for p in final_scv:
                    if p.split(',')[-1].strip() in f and 'null' not in p.split(',')[-1].strip():
                        print 1
                        o_scv.write(p)
                        continue
                    # if p in u_l:
                    #     print 2
                    #     continue
                    # else:
                    #     u_l.append(p)

                    # o_scv.write(p)


a = LikesScrapes('Part ALL.xlsx')
print a.main()
