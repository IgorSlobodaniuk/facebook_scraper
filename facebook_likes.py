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


FEED_URL = 'https://www.dropbox.com/s/1avucuy5zs2a7wc/Pages & Groups Analysis Quo Use V.2.xlsx?' \
       '_download_id=038177759136897694518006274979411474180122286806755418256791666272' \
       '&_notify_domain=www.dropbox.com&dl=1'

PAGE_ID_API = 'https://graph.facebook.com/%s?access_token=1318151578265722|8af8c5e756731c09ebcfaf8829103fc0'

LIKES_API = 'https://graph.facebook.com/%s/feed?' \
            'access_token=1318151578265722|8af8c5e756731c09ebcfaf8829103fc0&' \
            'since=2017-01-01&' \
            'fields=likes{link},link,created_time&limit=100'

F_ID_RE = re.compile('"page_id":(\d+),')


class LikesScrapes():

    def __init__(self, input_file, output_scv, output_file, r_format):
        self.input_file = input_file
        self.output_scv = output_scv
        self.output_file = output_file
        self.r_format = r_format

    def main(self):
        # input_data = get_data(self.input_file)
        # self._write_to_csv(input_data)
        # self._write_v_2_to_csv(input_data)
        # self._write_to_output_file()
        #
        self._get_prew_output_links()

    def _get_posts_data(self, data, input_url, all_data=None, n=0):
        all_data = [] if all_data is None else all_data

        n += 1

        if data.get('data'):
            for p in data['data']:
                all_data.append(p)

        next_page = data['paging'].get('next') if data.get('paging') else None


        if not next_page or n > 20:
            links = []
            for i in all_data:
                post_url = i.get('link', i['id'])
                post_time = i['created_time']
                post_likes = self._collect_likers(i, input_url, post_url, post_time)
                links.extend(post_likes)
            return links
        else:
            sleep(random.choice(range(0, 1)))
            next_data = requests.get(next_page.replace('limit=25', 'limit=100')).json()
            return self._get_posts_data(next_data, input_url, all_data, n)

    def _collect_likers(self, data, input_url, post_url=None, post_time=None, all_links=None):

        if all_links is None:
            all_links = []
        likers = data['likes']['data'] if data.get('likes') else []
        for i in likers:
            if 'scoped_user_id' not in i['link']:
                continue
            if self.r_format == 1:
                all_links.append('{},{},{},{}'.format(input_url, post_url.encode('utf-8'), post_time.split('T')[0], i['link']))
            else:
                all_links.append('{},{},{},{},{},{}'.format(input_url[0], input_url[1], input_url[2], input_url[3], input_url[4], i['link']))
        next_page = data['paging'].get('next') if data.get('paging') else None
        if not next_page:
            return all_links
        else:
            sleep(random.choice(range(0, 1)))
            next_data = requests.get(next_page.replace('limit=25', 'limit=100')).json()
            return self._collect_likers(next_data, input_url, post_url, post_time, all_links)

    def _write_to_csv(self, input_data):
        with open(self.output_scv, 'w') as otput_scv:
            otput_scv.write('{},{},{},{}'.format('Groups or pages', 'Post links', 'Post date', 'Profile link') + '\n')
            for i in self._get_input_links(input_data['Sheet1']):
                fid = self._get_f_id(i)
                if not fid:
                    otput_scv.write('{},null,null,null'.format(i).encode('utf-8') + '\n')
                    continue
                api_data = requests.get(LIKES_API % fid).json()
                if api_data.get('error'):
                    otput_scv.write('{},null,null,null'.format(i).encode('utf-8') + '\n')
                    continue
                sleep(random.choice(range(0, 1)))
                for r in self._get_posts_data(api_data, i):
                    otput_scv.write(r + '\n')

    def _get_posts_data_v_2(self, data, input_url, all_data=None, n=0):
        all_data = [] if all_data is None else all_data
        n += 1

        if data.get('data'):
            for p in data['data']:
                all_data.append(p)

        next_page = data['paging'].get('next') if data.get('paging') else None

        if n > 20:
            print 44444

        if not next_page or n > 20:
            links = []
            for i in all_data:
                post_url = i.get('link')
                post_likes = self._collect_likers(i, input_url, post_url)
                links.extend(post_likes)
            return links
        else:
            sleep(random.choice(range(0, 1)))
            next_data = requests.get(next_page.replace('limit=25', 'limit=100')).json()
            return self._get_posts_data_v_2(next_data, input_url, all_data, n)

    def _write_v_2_to_csv(self, input_data):
        with open(self.output_scv, 'w') as otput_scv:
            otput_scv.write('{},{},{},{},{},{}'.format('Country', 'PIC', 'China', 'Chinese language', 'Groups & Pages', 'Profile Links') + '\n')
            for i in input_data['Sheet1'][1300:]:
                print 77777734777, i
                fid = self._get_f_id(i[4])
                if not fid:
                    print 111111111
                    otput_scv.write('{},{},{},{},{},null'.format(i[0], i[1], i[2], i[3], i[4]).encode('utf-8') + '\n')
                    continue
                api_data = requests.get(LIKES_API % fid).json()
                if api_data.get('error'):
                    otput_scv.write('{},{},{},{},{},null'.format(i[0], i[1], i[2], i[3], i[4]).encode('utf-8') + '\n')
                    print 22222222222
                    continue
                sleep(random.choice(range(0, 1)))
                for r in self._get_posts_data_v_2(api_data, i):
                    otput_scv.write(r + '\n')

    def _write_to_output_file(self):
        with open('o_scv.csv', 'r') as otput_scv:
            workbook = Workbook('csvfile.xlsx', {'strings_to_urls': False})
            worksheet = workbook.add_worksheet()
            reader = csv.reader(otput_scv)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    worksheet.write(r, c, col.encode('utf-8'))
            workbook.close()


############################################################
        ##################################################################3

    def _save_feed_data(self):
        with open('input_data.xlsx', 'w') as f:
            f.write(requests.get(FEED_URL).content)

    def _get_f_id(self, url):

        if '/groups/' in url:
            return url.split('/groups/')[-1].split('/')[0]
        data = requests.get(PAGE_ID_API % url.strip().strip('?ref=br_rs')).json()
        pid = data.get('id')

        if pid:
            return pid

    def _get_input_links(self, data):
        links = []
        for l in data:
            links.extend([i for i in l if i and 'https:' in i])

        return tuple(set(links))

    def _get_prew_output_links(self):


        with open('output_data/output_old.csv', 'w') as old_scv:
            input_data = get_data('input_data/new_format_file.xlsx')
            for i in input_data['Sheet1'][1:]:
                old_scv.write(i[-1] + '\n')


        f = open('output_data/output_old.csv', 'r').readlines()
        f = tuple(set(f))

        print len(f)



        with open('o_scv.csv', 'r') as final_scv:

            u_l = []

            with open('o_scv2.csv', 'w') as o_scv:

                for p in final_scv:
                    if p.split(',')[-1].strip() in f:
                        print 1,
                        continue
                    # if p in u_l:
                    #     print 2
                    #     continue
                    # else:
                    #     u_l.append(p)

                    o_scv.write(p)


a = LikesScrapes('input_data/input_data2.xlsx', 'output_data/output3.csv', 'output_data/output2.xlsx', 2)
print a.main()
