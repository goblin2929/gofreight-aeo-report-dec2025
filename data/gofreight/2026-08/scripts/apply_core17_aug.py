import json, re
DATA=json.load(open('/Users/ekiriandra/tmp/gf_core17_aug.json'))
CANON=['freight forwarding software','freight management software','freight management system','freight management system software','best freight forwarding software','best freight management software','air freight forwarding software','global freight management system','ocean freight management software','sea freight management software','container freight management system']
EMERG=['freight forwarding crm','logistics crm software','best tms software','freight forwarder software','freight software','freight tracking software']
def plabel(t):
    from urllib.parse import urlparse
    p=urlparse(t).path
    return 'gofreight.com/' if p=='/' else p
def pagename(t):
    if 'best-freight-management' in t: return 'FMS listicle'
    if 'best-logistics-crm' in t: return 'CRM listicle'
    if 'best-tms' in t: return 'TMS article'
    if 'tracking-software-comparison' in t: return 'tracking page'
    if t.rstrip('/').endswith('gofreight.com'): return 'homepage'
    return 'blog'
def band(cp):
    return 'top 2' if cp<=2 else ('top 3' if cp<=3 else ('top 5' if cp<=5 else ('page 1' if cp<=10 else ('page 2' if cp<=20 else 'page 3+'))))
def row(kw, prior, cur):
    d=DATA[kw]; pp=d[prior+'Pos']; cp=d[cur+'Pos']; ci=d[cur+'Impr']; tgt=d['target']
    if pp is not None and cp is not None: dd=round(pp-cp,1)
    else: dd=None
    if dd is None: winrow=False; cls=''; dcell='n/a'
    elif dd>0: winrow=True; cls='up'; dcell=f'+{dd:.1f} ▲'
    elif dd==0: winrow=True; cls=''; dcell='±0.0 ●'
    else: winrow=False; cls='down'; dcell=f'{dd:.1f} ▼'
    mv='improved' if (dd is not None and dd>0.3) else ('softened' if (dd is not None and dd<-0.3) else 'held')
    note=f"{pagename(tgt).capitalize()}, {band(cp)} ({mv})" if cp is not None else "No US impressions this month"
    ppc=f'{pp:.1f}' if pp is not None else 'n/a'; cpc=f'{cp:.1f}' if cp is not None else 'n/a'
    return f'<tr class="{ "win-row" if winrow else ""}"><td><b>{kw}</b></td><td><a href="{tgt}" target="_blank">{plabel(tgt)}</a></td><td class="num">{ci:,}</td><td class="num">{ppc}</td><td class="num">{cpc}</td><td class="num {cls}">{dcell}</td><td>{note}</td></tr>'
def movers(order,prior,cur):
    ups=[];downs=[]
    for kw in order:
        d=DATA[kw]; pp=d[prior+'Pos']; cp=d[cur+'Pos']
        if pp is None or cp is None: continue
        dd=round(pp-cp,1)
        if dd>0.3: ups.append((dd,kw,pp,cp))
        elif dd<-0.3: downs.append((dd,kw,pp,cp))
    ups.sort(reverse=True); downs.sort()
    return ups,downs
def build(prior,cur,PL,CL):
    canon='\n'.join(row(k,prior,cur) for k in CANON)
    emerg='\n'.join(row(k,prior,cur) for k in EMERG)
    allord=CANON+EMERG
    ups,downs=movers(allord,prior,cur)
    def li(t):
        return ''.join(f'<li><b>“{kw}”</b> {pp:.1f} → {cp:.1f} ({"+" if dd>0 else ""}{dd:.1f})</li>' for dd,kw,pp,cp in t[:4])
    hdr=lambda first: (f'<tr><th>{first}</th><th>Target Page</th><th class="num">{CL} Impr (US)</th>'
        f'<th class="num">{PL} Pos</th><th class="num">{CL} Pos</th><th class="num">Δ Position</th><th>Note</th></tr>')
    return f'''<section>
    <h2>Core Keyword Tracking — Commercial Cluster (GSC avg position by target page, United States market, {CL} vs {PL})</h2>
    <p class="note" style="margin-bottom:8px;"><b>Canonical static panel</b> — the full commercial-cluster set (11 terms), kept fixed month over month. Each keyword is tracked on the GoFreight page it actually ranks on (the page with the most US impressions for that query).</p>
    <table class="t"><thead>
      {hdr('Core Keyword')}
    </thead><tbody>
      {canon}
    </tbody></table>
    <p class="note">United States market only (GSC country = usa), each keyword filtered to its best-ranking target page (query + page). Lower = better; “n/a” = no US impressions for that query that month.</p>
    <div class="two-col" style="margin-top:10px;">
      <div class="takeaway-box win"><b>✓ Wins on the target page (US)</b><ul>{li(ups)}</ul></div>
      <div class="takeaway-box watch"><b>⚠ Watch (US, target page)</b><ul>{li(downs) or '<li>No material declines this month.</li>'}</ul></div>
    </div>
    <div class="takeaway-box" style="margin-top:10px;background:#e6f4f1;">
      <b>Panel note:</b> the canonical set = the 11 freight-management / forwarding-software cluster terms (tracked since April); the 6 CRM / TMS / tracking terms sit in the <b>Emerging Keywords</b> table below. Each term is tracked on its actual best-ranking page. <b>Do not drop terms from the panel — keep old + new every month.</b>
    </div>
    <h3 style="margin-top:16px;">Emerging Keywords (candidate terms — CRM / TMS / tracking)</h3>
    <table class="t"><thead>
      {hdr('Emerging Keyword')}
    </thead><tbody>
      {emerg}
    </tbody></table>
    <p class="note">Tracked alongside the core panel; promote into the canonical set only with a noted change.</p>
  </section>'''
def replace_section(fn, section_html):
    h=open(fn,encoding='utf-8').read()
    m=re.search(r'<section>\s*<h2>[^<]*Core Keyword Tracking.*?</section>', h, re.S)
    if not m: raise SystemExit('core section not found in '+fn)
    h=h[:m.start()]+section_html+h[m.end():]
    open(fn,'w',encoding='utf-8').write(h)
    print('updated', fn)
replace_section('/Users/ekiriandra/seo-projects/aeo-report/gofreight_august_2026_report.html', build('jul','aug','July','August'))
import shutil
shutil.copy('/Users/ekiriandra/seo-projects/aeo-report/gofreight_august_2026_report.html',
            '/Users/ekiriandra/seo-projects/novastacks/clients/gofreight/output/reports/gofreight_august_2026_report.html')
print("done")
