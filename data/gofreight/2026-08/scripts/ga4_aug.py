import json, os, re, urllib.parse, urllib.request
from datetime import date, datetime
CRED='input/credentials'
prof=json.load(open(os.path.join(CRED,'gsc-profiles.json')))['profiles'] if 'profiles' in json.load(open(os.path.join(CRED,'gsc-profiles.json'))) else json.load(open(os.path.join(CRED,'gsc-profiles.json')))
p=prof['novastacks']
tok=json.load(open(os.path.join(CRED,'ga4-google-tokens.json')))
refresh=tok.get('refresh_token') or (tok.get('tokens') or {}).get('refresh_token')
body=urllib.parse.urlencode({'client_id':p['client_id'],'client_secret':p['client_secret'],'refresh_token':refresh,'grant_type':'refresh_token'}).encode()
req=urllib.request.Request('https://oauth2.googleapis.com/token',data=body,headers={'Content-Type':'application/x-www-form-urlencoded'})
ACCESS=json.load(urllib.request.urlopen(req,timeout=60))['access_token']
PROP='373075091'
AI=re.compile(r'(chatgpt|chat\.openai|openai\.com|perplexity|gemini\.google|bard\.google|claude\.ai|anthropic|copilot|you\.com|poe\.com|deepseek|grok\.com|x\.ai|mistral|phind|searchgpt|edgeservices|aimode)',re.I)
CG=re.compile(r'(chatgpt|chat\.openai|openai\.com)',re.I)
def run(dims,s,e):
    payload={'dateRanges':[{'startDate':s,'endDate':e}],'dimensions':[{'name':d} for d in dims],'metrics':[{'name':'sessions'}],'limit':200000}
    req=urllib.request.Request(f'https://analyticsdata.googleapis.com/v1beta/properties/{PROP}:runReport',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+ACCESS,'Content-Type':'application/json'})
    return json.loads(urllib.request.urlopen(req,timeout=120).read()).get('rows',[])
def wkmon(ds):
    d=date(int(ds[:4]),int(ds[4:6]),int(ds[6:8])); return d.fromordinal(d.toordinal()-d.weekday()).isoformat()
# weekly + monthly AI sessions
daily={};bysrc={}
for r in run(['date','sessionSource'],'2026-01-01','2026-09-06'):
    d=r['dimensionValues'][0]['value'];src=r['dimensionValues'][1]['value'];s=int(r['metricValues'][0]['value'])
    if AI.search(src): daily[d]=daily.get(d,0)+s; bysrc[src]=bysrc.get(src,0)+s
weekly={};monthly={}
for d,s in daily.items():
    w=wkmon(d);weekly[w]=weekly.get(w,0)+s;mo=f"{d[:4]}-{d[4:6]}";monthly[mo]=monthly.get(mo,0)+s
json.dump({'weekly':dict(sorted(weekly.items())),'monthly':dict(sorted(monthly.items())),'by_source_total':dict(sorted(bysrc.items(),key=lambda x:-x[1]))},open('/Users/ekiriandra/tmp/ga4_ai_traffic.json','w'),indent=2)
# source drop Jul vs Aug
src={}
for m,(s,e) in {'jul':('2026-07-01','2026-07-31'),'aug':('2026-08-01','2026-08-31')}.items():
    for r in run(['sessionSource'],s,e):
        so=r['dimensionValues'][0]['value'];n=int(r['metricValues'][0]['value'])
        if AI.search(so): src.setdefault(so,{'jul':0,'aug':0})[m]+=n
srcarr=[{'source':k,'jun':v['jul'],'jul':v['aug'],'delta':v['aug']-v['jul']} for k,v in src.items()]  # reuse jun/jul keys=prior/current
srcarr.sort(key=lambda x:x['delta'])
# landing pages (all AI + chatgpt) Jul vs Aug
lp={};cg={}
for m,(s,e) in {'jul':('2026-07-01','2026-07-31'),'aug':('2026-08-01','2026-08-31')}.items():
    for r in run(['landingPage','sessionSource'],s,e):
        pg=r['dimensionValues'][0]['value'];so=r['dimensionValues'][1]['value'];n=int(r['metricValues'][0]['value'])
        if AI.search(so): lp.setdefault(pg,{'jul':0,'aug':0})[m]+=n
        if CG.search(so): cg.setdefault(pg,{'jul':0,'aug':0})[m]+=n
lparr=[{'page':k,'jun':v['jul'],'jul':v['aug'],'delta':v['aug']-v['jul']} for k,v in lp.items()]; lparr.sort(key=lambda x:x['delta'])
cgarr=[{'page':k,'jun':v['jul'],'jul':v['aug'],'delta':v['aug']-v['jul']} for k,v in cg.items()]; cgarr.sort(key=lambda x:x['delta'])
json.dump({'sources':srcarr,'landingPages':lparr},open('/Users/ekiriandra/tmp/ga4-ai-drop.json','w'),indent=2)
json.dump(cgarr,open('/Users/ekiriandra/tmp/ga4-chatgpt-lp.json','w'),indent=2)
print("MONTHLY:",json.dumps(dict(sorted(monthly.items()))))
print("SOURCES jul->aug:")
for s in srcarr: print(f"  {s['jun']:>4} -> {s['jul']:>4} ({s['delta']:+d})  {s['source']}")
print("TOTAL jul",sum(s['jun'] for s in srcarr),"aug",sum(s['jul'] for s in srcarr))
