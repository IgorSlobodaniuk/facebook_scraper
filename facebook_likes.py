import json
import re
import random
import requests
from pyexcel_xlsx import get_data, save_data
from time import sleep
from collections import OrderedDict


FEED_URL = 'https://www.dropbox.com/s/1avucuy5zs2a7wc/Pages & Groups Analysis Quo Use V.2.xlsx?' \
       '_download_id=038177759136897694518006274979411474180122286806755418256791666272' \
       '&_notify_domain=www.dropbox.com&dl=1'

LIKES_API = 'https://graph.facebook.com/%s/feed?' \
            'access_token=1318151578265722|8af8c5e756731c09ebcfaf8829103fc0&' \
            'since=2017-01-01&' \
            'fields=likes{link},link&limit=100'

F_ID_RE = re.compile('"page_id":(\d+),')


class LikesScrapes():
    def main(self):
        result_data = {'Sheet1': []}
        self._save_feed_data()
        data = get_data('input_data.xlsx')
        nnn = 1
        for i in self._get_input_links(data['Sheet1']):
            print nnn
            fid = self._get_f_id(i)
            if not fid:
                print 444444, i
                continue
            print LIKES_API % fid
            api_data = requests.get(LIKES_API % self._get_f_id(i)).json()
            nnn += 1

            if api_data.get('error'):
                print "error 1"
                continue

            sleep(random.choice(range(1, 2)))

            col_b = self._get_posts_data(api_data)
            col_a = [''] * (len(col_b)-1)
            col_a.insert(0, i)
            tuples = zip(col_a, col_b)
            lists = [list(t) for t in tuples]
            result_data['Sheet1'].extend(lists)

        output_data = OrderedDict()
        output_data.update(result_data)
        save_data("output_file.xlsx", output_data)
        open('fffff.txt', 'w').write(json.dumps(result_data))

    def _get_posts_data(self, data, all_data=None):
        all_data = [] if all_data is None else all_data

        if data.get('data'):
            for p in data['data']:
                all_data.append(p)

        next_page = data['paging'].get('next') if data.get('paging') else None
        if not next_page:
            links = []
            for i in all_data:
                links.extend(self._collect_likers(i))
            return list(set(links))
        else:
            sleep(random.choice(range(1, 2)))
            next_data = requests.get(next_page.replace('limit=25', 'limit=100')).json()
            return self._get_posts_data(next_data, all_data)

    def _collect_likers(self, data, all_links=None):

        if all_links is None:
            all_links = []
        likers = data['likes']['data'] if data.get('likes') else []
        for i in likers:
            all_links.append(i['link'])
        next_page = data['paging'].get('next') if data.get('paging') else None
        if not next_page:
            return list(set(all_links))
        else:
            sleep(random.choice(range(1, 2)))
            next_data = requests.get(next_page.replace('limit=25', 'limit=100')).json()
            return self._collect_likers(next_data, all_links)

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
