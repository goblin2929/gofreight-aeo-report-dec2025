# -*- coding: utf-8 -*-
"""Build GoFreight AEO Monthly Report — July 2026 vs June 2026 (June format)."""
import json, pickle, re

G = json.load(open('/Users/ekiriandra/tmp/gofreight-july-data.json', encoding='utf-8'))
WD = json.load(open('/Users/ekiriandra/tmp/wd_july.json', encoding='utf-8'))
PC = json.load(open('/Users/ekiriandra/tmp/gf-page-clicks-july.json', encoding='utf-8'))
CORE = json.load(open('/Users/ekiriandra/tmp/gf-core-page-us-july.json', encoding='utf-8'))
GA4 = json.load(open('/Users/ekiriandra/tmp/ga4_ai_traffic.json', encoding='utf-8'))
DROP = json.load(open('/Users/ekiriandra/tmp/ga4-ai-drop.json', encoding='utf-8'))
W31 = {}
RW = json.load(open('/Users/ekiriandra/tmp/recent_work_map.json', encoding='utf-8'))
CG = json.load(open('/Users/ekiriandra/tmp/ga4-chatgpt-lp.json', encoding='utf-8'))   # ChatGPT-only landing pages

def f(n): return f"{round(n):,}"
def norm(u):
    u=u.strip().split('#')[0].split('?')[0]
    if u.endswith('/') and len(u)>len('https://gofreight.com/'): u=u.rstrip('/')
    return u.lower()
def dcls(v): return 'up' if v>0 else ('down' if v<0 else '')
def sgn(v,dec=0,suf=''): return f"{'+' if v>0 else ''}{v:,.{dec}f}{suf}"

# ---- merge homepage variants in WD pages ----
def canon(u):
    n=norm(u)
    for pre in ('https://gofreight.com','http://gofreight.com','https://www.gofreight.com','http://www.gofreight.com'):
        if n==pre or n==pre+'/': return 'https://gofreight.com/'
    return n
_m={}
for p in WD['pages']:
    k=canon(p['url'])
    if k not in _m: _m[k]={'url':('https://gofreight.com/' if k=='https://gofreight.com/' else p['url']),'subfolder':('Homepage' if k=='https://gofreight.com/' else p['subfolder']),'jul':0,'jun':0}
    _m[k]['jul']+=p['jul']; _m[k]['jun']+=p['jun']
WD['pages']=sorted(_m.values(), key=lambda x:x['jul'], reverse=True)
wd_by={norm(p['url']):p for p in WD['pages']}
def cit(url):
    p=wd_by.get(norm(url)); return (p['jun'] if p else 0, p['jul'] if p else 0)
def clicks_of(url):
    e=PC.get(norm(url),{}); return (e.get('jun',0), e.get('jul',0))
roll=WD['subfolder_rollup']; TOT=WD['totals']

# ---- top-line (prior=July, current=August) ----
CL_JUN,CL_JUL=6390,7734           # clicks (Jul, Aug)
IM_JUN,IM_JUL=1247565,1510644     # impressions
CTR_JUN,CTR_JUL=0.51,0.51
POS_JUN,POS_JUL=10.3,10.2
AIS_JUN,AIS_JUL=392,579           # GA4 direct AI sessions
VIS_JUN,VIS_JUL=29.3,28.0         # WorkDuo non-brand visibility (API, matches dashboard)

# brand from unfiltered query-dim
segj,segn=G['julSeg'],G['junSeg']
EX_J,EX_N=segj['exact']['c'],segn['exact']['c']
BR_J,BR_N=segj['brandedRelated']['c'],segn['brandedRelated']['c']
EXIM_J,EXIM_N=segj['exact']['i'],segn['exact']['i']
BRIM_J,BRIM_N=segj['brandedRelated']['i'],segn['brandedRelated']['i']
brand_j,brand_n=EX_J+BR_J,EX_N+BR_N
NB_J,NB_N=CL_JUL-brand_j,CL_JUN-brand_n
NBIM_J=IM_JUL-EXIM_J-BRIM_J
NBIM_N=IM_JUN-EXIM_N-BRIM_N
nbsh_j,nbsh_n=NB_J/CL_JUL*100,NB_N/CL_JUN*100

# ============ weekly series ============
MON={'01':'Jan','02':'Feb','03':'Mar','04':'Apr','05':'May','06':'Jun','07':'Jul','08':'Aug'}
def wlabel(w):
    y,m,d=w.split('-'); return f"{MON[m]} {int(d)}"
wser=[w for w in G['weekly'] if '2026-01-05'<=w['week']<='2026-08-24']
week_labels=[wlabel(w['week']) for w in wser]
clicks_tot=[w['total'] for w in wser]
clicks_nb=[w['nonBrand'] for w in wser]
# engine visibility: Jan5-May25 history + Jun/Jul weeks
chat_h=[8.33,5.71,7.14,5.71,9.29,10.71,10.0,15.0,17.14,17.14,13.57,15.71,15.0,13.57,17.86,14.29,13.57,14.29,16.43,12.14,27.14]
perp_h=[11.67,10.71,7.14,13.57,20.71,22.86,19.29,25.0,26.43,21.43,23.57,22.86,22.86,29.29,25.71,26.43,27.86,29.29,32.14,21.43,18.57]
goog_h=[16.67,14.29,16.54,21.26,21.71,25.0,25.2,30.71,20.77,27.87,26.67,29.75,27.42,27.87,25.2,28.12,30.95,31.5,33.33,29.2,36.61]
wv=WD['weekly_visibility']
# June weeks (W23-W26) carried from the July report (wd_aug pull only covers Jul+Aug)
wv.update({'2026-W23':{'ChatGPT':18.9,'Perplexity':18.3,'Google AI':39.1},'2026-W24':{'ChatGPT':12.8,'Perplexity':19.4,'Google AI':36.8},'2026-W25':{'ChatGPT':9.2,'Perplexity':17.3,'Google AI':36.4},'2026-W26':{'ChatGPT':14.8,'Perplexity':28.6,'Google AI':37.0}})
jj_weeks=['2026-W23','2026-W24','2026-W25','2026-W26','2026-W27','2026-W28','2026-W29','2026-W30','2026-W31','2026-W32','2026-W33','2026-W34','2026-W35']
chat=chat_h+[wv[w]['ChatGPT'] for w in jj_weeks]
perp=perp_h+[wv[w]['Perplexity'] for w in jj_weeks]
goog=goog_h+[wv[w]['Google AI'] for w in jj_weeks]
# AI sessions weekly (GA4)
gw=GA4['weekly']
ais=[gw.get(w['week'],'null') for w in wser]

# ============ tables ============
def seg_rows():
    rows=[]
    data=[('Exact "gofreight"',EX_J,EX_N,EXIM_J,EXIM_N),('Branded related',BR_J,BR_N,BRIM_J,BRIM_N),('Non-branded',NB_J,NB_N,NBIM_J,NBIM_N)]
    for name,cj,cn,ij,inn in data:
        dc=cj-cn; dp=dc/cn*100 if cn else 0; di=ij-inn
        rows.append(f'<tr><td>{name}</td><td class="num">{f(cn)}</td><td class="num">{f(cj)}</td><td class="num {dcls(dc)}">{sgn(dc)}</td><td class="num {dcls(dc)}">{sgn(dp,1,"%")}</td><td class="num">{f(inn)}</td><td class="num">{f(ij)}</td><td class="num {dcls(di)}">{sgn(di)}</td></tr>')
    dc=CL_JUL-CL_JUN; dp=dc/CL_JUN*100; di=IM_JUL-IM_JUN
    rows.append(f'<tr class="subtotal"><td>TOTAL</td><td class="num">{f(CL_JUN)}</td><td class="num">{f(CL_JUL)}</td><td class="num {dcls(dc)}">{sgn(dc)}</td><td class="num {dcls(dc)}">{sgn(dp,1,"%")}</td><td class="num">{f(IM_JUN)}</td><td class="num">{f(IM_JUL)}</td><td class="num {dcls(di)}">{sgn(di)}</td></tr>')
    return '\n'.join(rows)

SUB_LABEL={'Blog':'Blog','Homepage':'Homepage','Glossary':'Glossary','Solutions':'Solutions','Product':'Product','Pricing':'Pricing','Other':'Other (Company, Tools, etc.)'}
SUB_ORDER=['Blog','Homepage','Glossary','Solutions','Product','Pricing','Other']
gsub={s['name']:s for s in G['subfolders']}
def subfolder_rows():
    rows=[]
    for key in SUB_ORDER:
        s=gsub.get(key,{'junClicks':0,'julClicks':0,'junImpr':0,'julImpr':0})
        cn,cj=s['junClicks'],s['julClicks']; inn,ij=s['junImpr'],s['julImpr']
        dc=cj-cn; dp=dc/cn*100 if cn else 0
        r=roll.get(key,{'jun_pages':0,'jul_pages':0,'jun_cit':0,'jul_cit':0})
        def aic(p,c): return f'{p} <span style="color:var(--slate-5)">({f(c)})</span>' if p else '0'
        rows.append(f'<tr><td>{SUB_LABEL[key]}</td><td class="num">{f(cn)}</td><td class="num">{f(cj)}</td><td class="num {dcls(dc)}">{sgn(dc)}</td><td class="num {dcls(dc)}">{sgn(dp,1,"%")}</td><td class="num">{f(inn)}</td><td class="num">{f(ij)}</td><td class="num aeo">{aic(r["jun_pages"],r["jun_cit"])}</td><td class="num aeo">{aic(r["jul_pages"],r["jul_cit"])}</td></tr>')
    dc=CL_JUL-CL_JUN; dp=dc/CL_JUN*100
    pn,pj=TOT['jun_pages_primary'],TOT['jul_pages_primary']; tcn,tcj=TOT['jun_total_cit_primary'],TOT['jul_total_cit_primary']
    rows.append(f'<tr class="subtotal"><td>TOTAL (gofreight.com)</td><td class="num">{f(CL_JUN)}</td><td class="num">{f(CL_JUL)}</td><td class="num {dcls(dc)}">{sgn(dc)}</td><td class="num {dcls(dc)}">{sgn(dp,1,"%")}</td><td class="num">{f(IM_JUN)}</td><td class="num">{f(IM_JUL)}</td><td class="num aeo">{pn} <span style="color:var(--slate-5)">({f(tcn)})</span></td><td class="num aeo">{pj} <span style="color:var(--slate-5)">({f(tcj)})</span></td></tr>')
    return '\n'.join(rows)

def shorten(url):
    u=url.replace('https://gofreight.com','').replace('https://','')
    if u=='' or u=='/': return 'gofreight.com/ (homepage)'
    u=re.sub(r'\.html$','',u)
    if len(u)>62:
        parts=u.split('/'); u='/'.join(parts[:2])+'/…/'+parts[-1]
        if len(u)>62: u=u[:60]+'…'
    return u
top30=G['topPages'][:30]
top30_norm=set(norm(p['url']) for p in top30)
_rw_norm={norm(u):t for u,t in RW.items()}
def recent_work(url): return RW.get(url) or _rw_norm.get(norm(url),'')
def top30_rows():
    rows=[]; scj=scn=sdc=scan=scaj=0
    for i,p in enumerate(top30,1):
        cj,cn=p['julClicks'],p['junClicks']; dc=cj-cn
        mn,jl=cit(p['url']); scj+=cj; scn+=cn; sdc+=dc; scan+=mn; scaj+=jl
        rows.append(f'<tr><td class="num">{i}</td><td><a href="{p["url"]}" target="_blank">{shorten(p["url"])}</a></td><td>{recent_work(p["url"])}</td><td class="num">{f(cn)}</td><td class="num">{f(cj)}</td><td class="num {dcls(dc)}">{sgn(dc)}</td><td class="num">{f(p["julImpr"])}</td><td class="num aeo">{f(mn)}</td><td class="num aeo">{f(jl)}</td></tr>')
    rows.append(f'<tr class="subtotal"><td colspan="3">SUBTOTAL (Top 30)</td><td class="num">{f(scn)}</td><td class="num">{f(scj)}</td><td class="num {dcls(sdc)}">{sgn(sdc)}</td><td class="num">—</td><td class="num aeo">{f(scan)}</td><td class="num aeo">{f(scaj)}</td></tr>')
    return '\n'.join(rows)

def top15_rows():
    pages=sorted(WD['pages'],key=lambda x:x['jul'],reverse=True)[:15]
    pages=sorted(pages,key=lambda x:x['jul']-x['jun'],reverse=True)  # reorder the 15 by delta (biggest gainers first)
    rows=[]
    for i,p in enumerate(pages,1):
        cj=p['jul']; cn=p['jun']; d=cj-cn; cn2,cj2=clicks_of(p['url'])
        intop='yes' if norm(p['url']) in top30_norm else '—'
        rows.append(f'<tr><td class="num">{i}</td><td><a href="{p["url"]}" target="_blank">{shorten(p["url"])}</a></td><td class="num aeo">{f(cn)}</td><td class="num aeo">{f(cj)}</td><td class="num {dcls(d)}">{sgn(d)}</td><td class="num">{f(cj2)}</td><td class="num" style="color:var(--slate-5)">{intop}</td></tr>')
    return '\n'.join(rows)

CORE_ORDER=['freight forwarding crm','logistics crm software','best tms software','freight management system','freight management software','freight forwarding software','freight forwarder software','best freight management software','freight software','freight tracking software']
def plabel(t): return 'gofreight.com/' if t=='https://gofreight.com/' else '/'+t.split('gofreight.com/',1)[1]
CORE_NOTE={'freight forwarding crm':'Holding top 3 on the CRM listicle','logistics crm software':'Softened on the CRM listicle','best tms software':'TMS article up 5.7 spots','freight management system':'Holding top 4','freight management software':'Listicle owns the US SERP (top 2); homepage a weak secondary','freight forwarding software':'Homepage into the top 3','freight forwarder software':'Homepage into the top 2','best freight management software':'Improved into top 5','freight software':'Softened, page 1 edge','freight tracking software':'Improved into top 5'}
def core_rows():
    rows=[]
    for kw in CORE_ORDER:
        d=CORE[kw]; pn,pj=d['junPos_'],d['julPos']
        dd=(pn-pj) if (pn is not None and pj is not None) else None
        if dd is None: winrow=False; cls=''; dcell='n/a'
        elif dd>0: winrow=True; cls='up'; dcell=f'+{dd:.1f} ▲'
        elif dd==0: winrow=True; cls=''; dcell='±0.0 ●'
        else: winrow=False; cls='down'; dcell=f'{dd:.1f} ▼'
        pnc=f'{pn:.1f}' if pn is not None else 'n/a'; pjc=f'{pj:.1f}' if pj is not None else 'n/a'
        rows.append(f'<tr class="{ "win-row" if winrow else ""}"><td><b>{kw}</b></td><td><a href="{d["target"]}" target="_blank">{plabel(d["target"])}</a></td><td class="num">{f(d["julImpr"])}</td><td class="num">{pnc}</td><td class="num">{pjc}</td><td class="num {cls}">{dcell}</td><td>{CORE_NOTE[kw]}</td></tr>')
    return '\n'.join(rows)

def aeo_mom_rows():
    pn_all,pj_all=TOT['jun_pages'],TOT['jul_pages']
    tn_all,tj_all=TOT['jun_total_cit'],TOT['jul_total_cit']
    dtot=(tj_all-tn_all)/tn_all*100
    ds=(AIS_JUL-AIS_JUN)/AIS_JUN*100
    return f'''<tr><td>AI Platform Sessions (GA4)</td><td class="num">{f(AIS_JUN)}</td><td class="num">{f(AIS_JUL)}</td><td class="num up">+{ds:.1f}%</td><td>GA4 direct</td></tr>
<tr><td>AI Visibility (non-brand)</td><td class="num">{VIS_JUN:.1f}%</td><td class="num">{VIS_JUL:.1f}%</td><td class="num down">{VIS_JUL-VIS_JUN:+.1f} pts</td><td>WorkDuo</td></tr>
<tr><td>GoFreight Pages Cited by AI (all properties)</td><td class="num">{pn_all}</td><td class="num">{pj_all}</td><td class="num up">+{pj_all-pn_all}</td><td>WorkDuo citations</td></tr>
<tr><td>Total AI Citations of GoFreight Pages</td><td class="num">{f(tn_all)}</td><td class="num">{f(tj_all)}</td><td class="num up">+{dtot:.1f}%</td><td>WorkDuo citations</td></tr>'''

# ---- AI traffic deep-dive (source + landing page) ----
def src_bucket(s):
    s=s.lower()
    if 'chatgpt' in s or 'openai' in s: return 'ChatGPT'
    if 'gemini' in s or 'bard' in s: return 'Gemini'
    if 'claude' in s or 'anthropic' in s: return 'Claude'
    if 'perplexity' in s: return 'Perplexity'
    if 'copilot' in s: return 'Copilot'
    return 'Other AI'
def source_rows():
    agg={}
    for s in DROP['sources']:
        b=src_bucket(s['source']); e=agg.setdefault(b,{'jun':0,'jul':0}); e['jun']+=s['jun']; e['jul']+=s['jul']
    order=['ChatGPT','Gemini','Claude','Perplexity','Copilot','Other AI']
    rows=[]; tj=tn=0
    for b in order:
        if b not in agg: continue
        e=agg[b]; d=e['jul']-e['jun']; tj+=e['jul']; tn+=e['jun']
        cls='down' if d<0 else ('up' if d>0 else '')
        rows.append(f'<tr class="{ "win-row" if d>0 else ""}"><td><b>{b}</b></td><td class="num">{f(e["jun"])}</td><td class="num">{f(e["jul"])}</td><td class="num {cls}">{sgn(d)}</td></tr>')
    d=tj-tn
    rows.append(f'<tr class="subtotal"><td>TOTAL AI sessions</td><td class="num">{f(tn)}</td><td class="num">{f(tj)}</td><td class="num {dcls(d)}">{sgn(d)}</td></tr>')
    return '\n'.join(rows)
def lp_label(p):
    if p=='(not set)': return '(not set / unattributed)'
    return p if len(p)<=58 else p[:56]+'…'
def lp_link(p):
    if p.startswith('/'): return f'<a href="https://gofreight.com{p}" target="_blank">{lp_label(p)}</a>'
    return lp_label(p)
def lp_drop_rows():   # ChatGPT-specific drops
    drops=[l for l in CG if l['delta']<0 and l['page']!='(not set)'][:8]
    return '\n'.join(f'<tr><td>{lp_link(l["page"])}</td><td class="num">{f(l["jun"])}</td><td class="num">{f(l["jul"])}</td><td class="num down">{sgn(l["delta"])}</td></tr>' for l in drops)
def lp_gain_rows():   # ChatGPT-specific gains
    gains=sorted([l for l in CG if l['delta']>0], key=lambda x:-x['delta'])[:6]
    return '\n'.join(f'<tr class="win-row"><td>{lp_link(l["page"])}</td><td class="num">{f(l["jun"])}</td><td class="num">{f(l["jul"])}</td><td class="num up">{sgn(l["delta"])}</td></tr>' for l in gains)
# ChatGPT share of AI sessions (June) for the insight
_cg_jun=sum(l['jun'] for l in CG); _cg_jul=sum(l['jul'] for l in CG)
_ai_jun=sum(s['jun'] for s in DROP['sources']); _ai_jul=sum(s['jul'] for s in DROP['sources'])
cg_share_jun=round(_cg_jun/_ai_jun*100) if _ai_jun else 0
cg_share_jul=round(_cg_jul/_ai_jul*100) if _ai_jul else 0
cg_drop=_cg_jul-_cg_jun; ai_drop=_ai_jul-_ai_jun

print("NB_J",NB_J,"share",round(nbsh_j,1),"| citations jun",TOT['jun_total_cit'],"jul",TOT['jul_total_cit'])
frag=dict(seg=seg_rows(),sub=subfolder_rows(),top30=top30_rows(),top15=top15_rows(),core=core_rows(),aeo=aeo_mom_rows(),
    src=source_rows(),lp_drop=lp_drop_rows(),lp_gain=lp_gain_rows(),
    cg_share_jun=cg_share_jun,cg_share_jul=cg_share_jul,cg_jun=_cg_jun,cg_jul=_cg_jul,cg_drop=cg_drop,ai_drop=ai_drop,
    week_labels=week_labels,clicks_tot=clicks_tot,clicks_nb=clicks_nb,chat=chat,perp=perp,goog=goog,ais=ais,
    NB_J=NB_J,NB_N=NB_N,nbsh_j=nbsh_j,nbsh_n=nbsh_n,TOT=TOT,
    CL_JUN=CL_JUN,CL_JUL=CL_JUL,IM_JUN=IM_JUN,IM_JUL=IM_JUL)
pickle.dump(frag,open('/Users/ekiriandra/tmp/frag_aug.pkl','wb'))
print("wrote frag_aug.pkl; weeks:",len(week_labels))
