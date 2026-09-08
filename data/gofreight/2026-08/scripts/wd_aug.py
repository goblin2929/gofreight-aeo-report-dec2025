# -*- coding: utf-8 -*-
"""WorkDuo July+August occurrence-count citations + weekly non-brand visibility + SOV + mentions. Keys jul/aug."""
import urllib.request, urllib.parse, base64, json, sys, re, time, os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
AUTH=base64.b64encode(f"{os.environ['WORKDUO_PUBLIC_KEY']}:{os.environ['WORKDUO_SECRET_KEY']}".encode()).decode()
PID='cmhk59aw9001mlo33c3t8n3rj'
def api(path,params,att=6):
    url=f'https://api.workduo.ai/core/v1/{path}?'+urllib.parse.urlencode(params); last=None
    for i in range(att):
        try:
            req=urllib.request.Request(url); req.add_header('Authorization',f'Basic {AUTH}')
            with urllib.request.urlopen(req,timeout=120) as r: return json.loads(r.read())
        except urllib.error.HTTPError as e:
            b=e.read()[:200].decode(errors='replace')
            if e.code==400: raise RuntimeError('HTTP 400: '+b)
            last=f'HTTP {e.code}: {b}'
        except Exception as e: last=str(e)
        time.sleep(2*(i+1))
    raise RuntimeError('FAILED: '+str(last))
qs=json.load(open('/tmp/wd_queries_all.json')); qmap={q['id']:q.get('topic','?') for q in qs}
allq=list(qmap.keys()); nb=set(q for q,t in qmap.items() if t in ('MOFU','TOFU','BOFU'))
print(f'{len(allq)} queries, {len(nb)} non-brand',file=sys.stderr)
CHUNKS=[('2026-07-01','2026-07-31'),('2026-08-01','2026-08-31')]; MONTH={'2026-07':'jul','2026-08':'aug'}
def fetch(a):
    qid,s,e=a; out=[];tok=None
    for _ in range(300):
        p={'projectId':PID,'queryId':qid,'dateRange':'custom','startDate':s,'endDate':e,'limit':100}
        if tok:p['pageToken']=tok
        try:res=api('responses',p)
        except RuntimeError as ex: print('giveup',qid[-6:],s,ex,file=sys.stderr); break
        out.extend(res.get('data',[]));tok=res.get('nextPageToken')
        if not tok:break
    return qid,out
def bucket(p):
    pl=(p or '').lower()
    if 'chatgpt' in pl or pl.startswith('openai'):return 'ChatGPT'
    if 'perplexity' in pl:return 'Perplexity'
    if 'google' in pl or 'ai-overview' in pl or 'gemini' in pl:return 'Google AI'
    return 'Other'
def norm(u):
    u=u.strip().split('#')[0].split('?')[0]
    if u.endswith('/') and len(u)>len('https://gofreight.com/'): u=u.rstrip('/')
    return u.lower()
GF=re.compile(r'https?://[^\s\'">\]\\]*gofreight\.com[^\s\'">\]\\]*',re.I)
CIT=['citations','sources','references','citedUrls','sourceUrls','citedSources','mentionedUrls']
def extract(r):
    urls=[];found=False
    for f in CIT:
        v=r.get(f)
        if isinstance(v,list):
            found=True
            for it in v:
                if isinstance(it,str) and 'gofreight.com' in it.lower():urls.append(it)
                elif isinstance(it,dict):
                    for k in ('url','link','href','source','uri'):
                        if isinstance(it.get(k),str) and 'gofreight.com' in it[k].lower():urls.append(it[k]);break
        elif isinstance(v,str) and 'gofreight.com' in v.lower():found=True;urls.append(v)
    if not found: urls=GF.findall(json.dumps(r))
    return [norm(u) for u in urls if 'gofreight.com' in u.lower()]
weekly=defaultdict(lambda:defaultdict(lambda:{'m':0,'t':0})); mvis=defaultdict(lambda:{'m':0,'t':0})
msov=defaultdict(lambda:{'s':0.0,'n':0}); mmen=defaultdict(int)
pcit=defaultdict(lambda:defaultdict(lambda:defaultdict(int))); ptot=defaultdict(lambda:defaultdict(int)); rc=defaultdict(int)
for s,e in CHUNKS:
    tasks=[(q,s,e) for q in allq]; got=0
    with ThreadPoolExecutor(max_workers=4) as ex:
        for qid,rs in ex.map(fetch,tasks):
            got+=len(rs); isnb=qid in nb
            for r in rs:
                d=r.get('date','');mo=d[:7];pl=bucket(r.get('platform',''))
                if pl!='Other':
                    rc[mo]+=1
                    if r.get('selfMentioned'):mmen[mo]+=1
                    if isnb:
                        wk=datetime.strptime(d,'%Y-%m-%d').strftime('%Y-W%V')
                        weekly[wk][pl]['t']+=1;mvis[mo]['t']+=1
                        try:msov[mo]['s']+=float(r.get('sov') or 0);msov[mo]['n']+=1
                        except(TypeError,ValueError):pass
                        if r.get('selfMentioned'):weekly[wk][pl]['m']+=1;mvis[mo]['m']+=1
                if mo in MONTH:
                    ml=MONTH[mo]
                    for u in extract(r):pcit[u][ml][pl]+=1;ptot[u][ml]+=1
    print(f'  {s}: {got}',file=sys.stderr)
def classify(url):
    if 'support.gofreight.com' in url:return 'Support'
    if 'archive.gofreight.com' in url:return 'Archive'
    if 'api.gofreight.com' in url:return 'API'
    path=url
    for pre in ['https://gofreight.com','http://gofreight.com','https://www.gofreight.com']:
        if url.startswith(pre):path=url[len(pre):];break
    if path in ('','/'):return 'Homepage'
    path=path.rstrip('/')
    if path.startswith('/blog'):return 'Blog'
    if path.startswith('/glossary'):return 'Glossary'
    if path.startswith('/pricing'):return 'Pricing'
    if path.startswith('/product'):return 'Product'
    if path.startswith('/solution'):return 'Solutions'
    for sp in ['/freight-forwarding-software','/freight-management-software','/freight-management-system','/air-freight-software','/ocean-freight-software','/customs-management','/warehouse-management']:
        if path==sp or path.startswith(sp+'/'):return 'Solutions'
    return 'Other'
pages=[]
for url in ptot:
    pages.append({'url':url,'subfolder':classify(url),'aug':ptot[url].get('aug',0),'jul':ptot[url].get('jul',0)})
pages.sort(key=lambda x:x['aug'],reverse=True)
BUCK=['Homepage','Blog','Glossary','Solutions','Product','Pricing','Support','API','Archive','Other']
roll={}
for b in BUCK:
    ps=[p for p in pages if p['subfolder']==b]
    roll[b]={'aug_pages':len([p for p in ps if p['aug']>0]),'jul_pages':len([p for p in ps if p['jul']>0]),'aug_cit':sum(p['aug'] for p in ps),'jul_cit':sum(p['jul'] for p in ps)}
prim=[p for p in pages if p['subfolder'] not in ('Support','API','Archive')]
tot={'aug_total_cit':sum(p['aug'] for p in pages),'jul_total_cit':sum(p['jul'] for p in pages),
 'aug_pages':len([p for p in pages if p['aug']>0]),'jul_pages':len([p for p in pages if p['jul']>0]),
 'aug_total_cit_primary':sum(p['aug'] for p in prim),'jul_total_cit_primary':sum(p['jul'] for p in prim),
 'aug_pages_primary':len([p for p in prim if p['aug']>0]),'jul_pages_primary':len([p for p in prim if p['jul']>0])}
wk={w:{pl:(round(weekly[w][pl]['m']/weekly[w][pl]['t']*100,1) if weekly[w][pl]['t'] else 0) for pl in ['ChatGPT','Perplexity','Google AI']} for w in sorted(weekly)}
mv={m:(round(v['m']/v['t']*100,1) if v['t'] else 0) for m,v in sorted(mvis.items())}
sov={m:(round(v['s']/v['n']*100,1) if v['n'] else 0) for m,v in sorted(msov.items())}
out={'weekly_visibility':wk,'monthly_visibility_nonbrand':mv,'monthly_sov_nonbrand':sov,'monthly_brand_mentions':dict(sorted(mmen.items())),'monthly_response_counts':dict(sorted(rc.items())),'pages':pages,'subfolder_rollup':roll,'totals':tot}
json.dump(out,open('/Users/ekiriandra/tmp/wd_aug.json','w'),indent=2)
print('monthly vis:',mv,file=sys.stderr); print('totals:',json.dumps(tot),file=sys.stderr)
print('mentions:',dict(mmen),'sov:',sov,file=sys.stderr)
print('top15:',file=sys.stderr)
for p in pages[:15]: print(f"  aug {p['aug']:4d} jul {p['jul']:4d} {p['subfolder']:9s} {p['url']}",file=sys.stderr)
print('WROTE wd_aug.json',file=sys.stderr)
