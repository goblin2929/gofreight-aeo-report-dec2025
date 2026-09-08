import sys, json
sys.path.insert(0,'scripts')
from gsc_client import GSC
from urllib.parse import urlparse
SITE='sc-domain:gofreight.com'
PRIMARY=[{'filters':[{'dimension':'page','operator':'contains','expression':'https://gofreight.com/'}]}]
g=GSC('novastacks')
def norm(u):
    u=u.strip().split('#')[0].split('?')[0]
    if u.endswith('/') and len(u)>len('https://gofreight.com/'): u=u.rstrip('/')
    return u.lower()
def pull(s,e):
    return g.query(SITE,s,e,dimensions=['page'],row_limit=25000,dimension_filter_groups=PRIMARY)
m={}
for r in pull('2026-08-01','2026-08-31'): m.setdefault(norm(r['keys'][0]),{'aug':0,'jul':0})['aug']+=r['clicks']
for r in pull('2026-07-01','2026-07-31'): m.setdefault(norm(r['keys'][0]),{'aug':0,'jul':0})['jul']+=r['clicks']
json.dump(m,open('/Users/ekiriandra/tmp/gf-page-clicks-aug.json','w'))
print('pages:',len(m))
