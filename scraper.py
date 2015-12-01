import requests
import dataset
import math
from itertools import count
from urlparse import urljoin

engine = dataset.connect('sqlite:///data.sqlite')
table = engine['data']

PAGE_SIZE = 1000
BASE = 'http://instante.justice.md/apps/hotariri_judecata/inst/'
COURTS = ["cac/cac.php", "cab/cab.php", "cabe/cabe.php", "cach/cach.php",
          "caco/caco.php", "jan/jan.php", "jba/jba.php", "jbs/jbs.php",
          "jbe/jbe.php", "jb/jb.php", "jbr/jbr.php", "jbu/jbu.php",
          "jch/jch.php", "jcl/jcl.php", "jct/jct.php", "jca/jca.php",
          "jcg/jcg.php", "jcc/jcc.php", "jcm/jcm.php", "jci/jci.php",
          "jco/jco.php", "jcr/jcr.php", "jdn/jdn.php", "jdr/jdr.php",
          "je/je.php", "jed/jed.php", "jfa/jfa.php", "jfl/jfl.php",
          "jgl/jgl.php", "jhn/jhn.php", "jia/jia.php", "jlv/jlv.php",
          "jns/jns.php", "joc/joc.php", "jor/jor.php", "jrz/jrz.php",
          "jrz/jrz.php", "jrc/jrc.php", "jrsr/jrsr.php", "jsi/jsi.php",
          "jsd/jsd.php", "jsr/jsr.php", "jsv/jsv.php", "jst/jst.php",
          "jt/jt.php", "jtl/jtl.php", "jun/jun.php", "jvl/jvl.php",
          "jdb/jdb.php", "jcc/jcc.php", "jm/jm.php"]


def scrape_court(court):
    url = urljoin(BASE, court)
    url = urljoin(url, 'db_hot_grid.php')
    for i in count(1):
        q = {
            '_search': 'false',
            'nd': 1448893196876,
            'rows': PAGE_SIZE,
            'page': i,
            'sidx': 'id',
            'sord': 'asc'
        }
        res = requests.post(url, data=q)
        data = res.json()
        pages = int(math.ceil(float(data['records']) / PAGE_SIZE))
        print 'Court %s: page %s (of %s)' % (court, i, pages)
        if i > pages:
            return
        for row in data['rows']:
            id = row.get('id')
            file_href, date, case, parties, typ, topic, _ = row['cell']
            _, href = file_href.split('"', 1)
            href, _ = href.split('"', 1)
            record = {
                'record_id': id,
                'url': urljoin(url, href),
                'date': date,
                'case_id': case,
                'parties': parties,
                'type': typ,
                'court': court,
                'topic': topic
            }
            table.upsert(record, ['record_id'])

            # res = requests.head(record['url'])
            # print res.headers
            # print record['url']


if __name__ == '__main__':
    for court in COURTS:
        scrape_court(court)
