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


CREDENTIALS_LIST = [
    '1318151578265722|8af8c5e756731c09ebcfaf8829103fc0',
    '119249228626954|3354361a065a77584139686aa617b438',
    '240262026468917|5a13af7847222a7de910d06c4ba9b043'
]

TAGBOARD_API = 'https://funnel.tagboard.com/search/{}?excluded_networks=instagram,twitter,googleplus&count=10000'
POST_API = 'https://graph.facebook.com/{}?access_token={}&fields=likes.summary(true),comments.summary(true),created_time'


class LikesScrapes():
    def __init__(self, input_file_name, sheet_name):
        self.input_file = './input_files/{}'.format(input_file_name)
        self.output_scv = './output_files/{}.csv'.format(input_file_name.split('.')[0])
        self.output_file = './output_files/output_{}'.format(input_file_name)
        self.sheet = sheet_name

    def main(self):
        print 'Started'
        input_data = get_data(self.input_file)
        self._write_to_csv(input_data)
        self._write_to_output_file(self.output_scv, self.output_file)

    def _write_to_csv(self, input_data):

        with open(self.output_scv, 'w') as otput_scv:
            titles = input_data[self.sheet][0]
            otput_scv.write(','.join(titles) + '\n')
            print 'found {} input URLs'.format(input_data[self.sheet][1:])
            for n, i in enumerate(input_data[self.sheet][1:]):
                print n, i[2]
                if i:
                    tagboard_res = requests.get(TAGBOARD_API.format(i[2])).json()
                    if tagboard_res.get('posts'):
                        total_results = tagboard_res['meta']['hits']['total']
                        print 'Total results for {} are: {}'.format(i[2], total_results)
                        for p in tagboard_res.get('posts'):
                            post_link = p['permalink']
                            if p.get('sentiment'):
                                post_data = requests.get(POST_API.format(p['post_id'], random.choice(CREDENTIALS_LIST))).json()

                                if not post_data.get('likes'):
                                    continue

                                post_likes_count = post_data['likes']['summary']['total_count']
                                if post_likes_count:
                                    post_comments_count = post_data['comments']['summary']['total_count']
                                    otput_scv.write(
                                        '{},{},{},{},{},{},{}'.format(
                                            post_data['created_time'].split('T')[0], i[1], i[2], i[3], post_link, int(post_likes_count), int(post_comments_count)
                                        ) + '\n'
                                    )

                                    # sleep(random.choice(range(1, 2)))

    def _write_to_output_file(self, output_csv, output_file):
        with open(output_csv, 'r') as otput_scv:
            workbook = Workbook(output_file, {'strings_to_urls': False})
            worksheet = workbook.add_worksheet()
            reader = csv.reader(otput_scv)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    worksheet.write(r, c, col.encode('utf-8'))
            workbook.close()


a = LikesScrapes('Hashtag Master - Sample V.4.xlsx', 'Level 1')
a.main()
