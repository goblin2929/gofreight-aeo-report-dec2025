import sys, json
sys.path.insert(0,'scripts')
from gsc_client import GSC
from urllib.parse import urlparse
from datetime import date, datetime
SITE='sc-domain:gofreight.com'
AUG=('2026-08-01','2026-08-31'); JUL=('2026-07-01','2026-07-31')
PRIMARY=[{'filters':[{'dimension':'page','operator':'contains','expression':'https://gofreight.com/'}]}]
g=GSC('novastacks')
def q(s,e,dims,filt=None):
    return g.query(SITE,s,e,dimensions=dims,row_limit=25000,dimension_filter_groups=filt)
def agg(rows):
    m={}
    for r in rows:
        k=r['keys'][0]; x=m.setdefault(k,{'clicks':0,'impressions':0,'ps':0})
        x['clicks']+=r['clicks']; x['impressions']+=r['impressions']; x['ps']+=r['position']*r['impressions']
    for v in m.values(): v['avgPos']=v['ps']/v['impressions'] if v['impressions'] else 0
    return m
def totals(rows):
    c=sum(r['clicks'] for r in rows); i=sum(r['impressions'] for r in rows); ps=sum(r['position']*r['impressions'] for r in rows)
    return {'clicks':c,'impressions':i,'avgPos':ps/i if i else 0,'ctr':c/i*100 if i else 0}
def subf(u):
    try:
        h=urlparse(u).netloc; p=urlparse(u).path
    except: return 'Other'
    if h.startswith('support.'):return 'Support'
    if h.startswith('api.'):return 'API'
    if h.startswith('archive.'):return 'Archive'
    if p in ('','/'):return 'Homepage'
    if p.startswith('/blog'):return 'Blog'
    if p.startswith('/glossary'):return 'Glossary'
    if p.startswith('/solutions') or p.startswith('/solution'):return 'Solutions'
    if p.startswith('/pricing'):return 'Pricing'
    if p.startswith('/product') or p.startswith('/features'):return 'Product'
    return 'Other'
def cls(qq):
    s=qq.lower()
    if s in('gofreight','go freight'):return 'exact'
    if 'gofreight' in s or 'go freight' in s:return 'brandedRelated'
    return 'nonBranded'
def wkmon(ds):
    d=datetime.strptime(ds,'%Y-%m-%d').date(); return (d.fromordinal(d.toordinal()-d.weekday())).isoformat()

augP=q(*AUG,['page'],PRIMARY); julP=q(*JUL,['page'],PRIMARY)
augQ=agg(q(*AUG,['query'])); julQ=agg(q(*JUL,['query']))
augPa=agg(augP); julPa=agg(julP)
augTot=totals(augP); julTot=totals(julP)
top=[{'url':k,'augClicks':v['clicks'],'augImpr':v['impressions'],'augPos':v['avgPos'],'julClicks':julPa.get(k,{}).get('clicks',0),'julImpr':julPa.get(k,{}).get('impressions',0)} for k,v in augPa.items()]
top.sort(key=lambda x:-x['augClicks']); top=top[:30]
def subagg(pm):
    m={}
    for u,v in pm.items():
        s=subf(u); x=m.setdefault(s,{'clicks':0,'impressions':0}); x['clicks']+=v['clicks']; x['impressions']+=v['impressions']
    return m
aS=subagg(augPa); jS=subagg(julPa)
subs=[{'name':k,'augClicks':aS.get(k,{}).get('clicks',0),'julClicks':jS.get(k,{}).get('clicks',0),'augImpr':aS.get(k,{}).get('impressions',0),'julImpr':jS.get(k,{}).get('impressions',0)} for k in set(aS)|set(jS)]
subs.sort(key=lambda x:-x['augClicks'])
def segagg(qm):
    s={'exact':{'c':0,'i':0},'brandedRelated':{'c':0,'i':0},'nonBranded':{'c':0,'i':0}}
    for qq,v in qm.items():
        c=cls(qq); s[c]['c']+=v['clicks']; s[c]['i']+=v['impressions']
    return s
augSeg=segagg(augQ); julSeg=segagg(julQ)
# weekly Jan5 - Sep6
REGEX='(?i)go\\s*-?\\s*freight|gofright'
dTot=q('2026-01-01','2026-09-06',['date'],PRIMARY)
dBr=q('2026-01-01','2026-09-06',['date'],[{'filters':[{'dimension':'page','operator':'contains','expression':'https://gofreight.com/'},{'dimension':'query','operator':'includingRegex','expression':REGEX}]}])
br={r['keys'][0]:r['clicks'] for r in dBr}
wk={}
for r in dTot:
    w=wkmon(r['keys'][0]); x=wk.setdefault(w,{'t':0,'b':0}); x['t']+=r['clicks']; x['b']+=br.get(r['keys'][0],0)
weekly=[{'week':w,'total':v['t'],'nonBrand':v['t']-v['b']} for w,v in sorted(wk.items())]
out={'augTot':augTot,'julTot':julTot,'augSeg':augSeg,'julSeg':julSeg,'subfolders':subs,'topPages':top,'weekly':weekly}
json.dump(out,open('/Users/ekiriandra/tmp/gofreight-aug-data.json','w'),indent=2)
print(f"AUG: {augTot['clicks']} clicks, {round(augTot['impressions'])} impr, pos {augTot['avgPos']:.2f}, CTR {augTot['ctr']:.3f}%")
print(f"JUL: {julTot['clicks']} clicks, {round(julTot['impressions'])} impr, pos {julTot['avgPos']:.2f}, CTR {julTot['ctr']:.3f}%")
print("segments AUG:",json.dumps(augSeg),"JUL:",json.dumps(julSeg))
print("subs:",json.dumps([(s['name'],s['julClicks'],s['augClicks']) for s in subs]))
