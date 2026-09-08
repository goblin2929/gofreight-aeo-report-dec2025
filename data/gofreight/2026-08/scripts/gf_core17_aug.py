import sys, json
sys.path.insert(0,'scripts')
from gsc_client import GSC
from urllib.parse import urlparse
SITE='sc-domain:gofreight.com'
KW=['freight forwarding crm','logistics crm software','best tms software','freight forwarder software','freight software','freight tracking software',
    'freight forwarding software','freight management software','freight management system','freight management system software','best freight forwarding software','best freight management software','air freight forwarding software','global freight management system','ocean freight management software','sea freight management software','container freight management system']
MONTHS=[('jun','2026-06-01','2026-06-30'),('jul','2026-07-01','2026-07-31'),('aug','2026-08-01','2026-08-31')]
g=GSC('novastacks')
def pull(kw,s,e):
    f=[{'filters':[{'dimension':'country','operator':'equals','expression':'usa'},{'dimension':'query','operator':'equals','expression':kw}]}]
    return [{'url':r['keys'][0],'pos':round(r['position'],1),'impr':int(r['impressions'])} for r in g.query(SITE,s,e,dimensions=['page'],row_limit=1000,dimension_filter_groups=f)]
out={}
for kw in KW:
    per={lab:pull(kw,s,e) for lab,s,e in MONTHS}
    tot={}
    for lab in per:
        for r in per[lab]: tot[r['url']]=tot.get(r['url'],0)+r['impr']
    target=max(tot,key=tot.get) if tot else None
    d={'target':target}
    for lab in per:
        row=next((r for r in per[lab] if r['url']==target),None)
        d[lab+'Pos']=row['pos'] if row else None; d[lab+'Impr']=row['impr'] if row else 0
    out[kw]=d
json.dump(out,open('/Users/ekiriandra/tmp/gf_core17_aug.json','w'),indent=2)
def lab(u): 
    p=urlparse(u).path; return 'gofreight.com/' if p=='/' else p
print(f"{'keyword':36s} {'target':44s} {'Jul':>5} {'Aug':>5}  augImpr")
for kw in KW:
    d=out[kw]; print(f"{kw:36s} {lab(d['target'])[:44]:44s} {str(d['julPos']):>5} {str(d['augPos']):>5}  {d['augImpr']}")
