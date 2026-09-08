# -*- coding: utf-8 -*-
"""Assemble the July 2026 GoFreight report HTML from frag_aug.pkl."""
import json, pickle
fr = pickle.load(open('/Users/ekiriandra/tmp/frag_aug.pkl','rb'))
def f(n): return f"{round(n):,}"

CL_N,CL_J = fr['CL_JUN'],fr['CL_JUL']
NB_J,NB_N = fr['NB_J'],fr['NB_N']; nbsh_j=fr['nbsh_j']
d_tot=CL_J-CL_N; d_tot_p=d_tot/CL_N*100
d_nb=NB_J-NB_N; d_nb_p=d_nb/NB_N*100
TOT=fr['TOT']
pc_n,pc_j=TOT['jun_total_cit_primary'],TOT['jul_total_cit_primary']
ac_n,ac_j=TOT['jun_total_cit'],TOT['jul_total_cit']; ac_g=(ac_j-ac_n)/ac_n*100

def jsarr(a): return '['+','.join('null' if x=='null' else f'{x}' for x in a)+']'
week_labels_js='['+','.join(f'"{x}"' for x in fr['week_labels'])+']'

HTML = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AEO Monthly Report — GoFreight — August 2026</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root {{ --teal:#017d8e; --teal-d:#0e7490; --slate-9:#0f172a; --slate-7:#334155; --slate-5:#64748b; --slate-3:#cbd5e1; --slate-1:#f1f5f9; --green:#16a34a; --amber:#d97706; --red:#dc2626; }}
  * {{ box-sizing:border-box; }}
  body {{ font-family:-apple-system,BlinkMacSystemFont,'Inter','Segoe UI',system-ui,sans-serif; background:#fff; color:var(--slate-9); margin:0; padding:28px 36px; font-size:13.5px; line-height:1.45; }}
  .page {{ width:1280px; margin:0 auto; }}
  html {{ min-width:1320px; }}
  header {{ border-bottom:2px solid var(--teal); padding-bottom:12px; margin-bottom:18px; display:flex; justify-content:space-between; align-items:flex-end; }}
  header h1 {{ font-size:22px; margin:0; color:var(--slate-9); letter-spacing:-0.01em; }}
  header .meta {{ font-size:12px; color:var(--slate-5); text-align:right; }}
  header .meta strong {{ color:var(--slate-7); }}
  .hook {{ background:linear-gradient(90deg,#ecfeff 0%,#f0fdfa 100%); border-left:4px solid var(--teal); padding:12px 16px; border-radius:4px; margin-bottom:18px; font-size:14px; }}
  .hook strong {{ color:var(--teal-d); }}
  .kpi-row {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:16px; }}
  .kpi {{ border:1px solid var(--slate-3); border-radius:6px; padding:10px 14px; background:#fff; }}
  .kpi .label {{ font-size:11px; color:var(--slate-5); text-transform:uppercase; letter-spacing:0.04em; }}
  .kpi .val {{ font-size:20px; font-weight:700; color:var(--slate-9); margin-top:2px; }}
  .kpi .delta {{ font-size:12px; margin-top:2px; }}
  .delta.up {{ color:var(--green); }} .delta.down {{ color:var(--red); }} .delta.flat {{ color:var(--amber); }}
  .chart-row {{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-bottom:22px; }}
  .chart-card {{ border:1px solid var(--slate-3); border-radius:6px; padding:12px 14px 10px; background:#fff; }}
  .chart-card h3 {{ font-size:13px; margin:0 0 2px; color:var(--slate-9); }}
  .chart-card .sub {{ font-size:11px; color:var(--slate-5); margin-bottom:8px; }}
  .chart-canvas-wrap {{ height:200px; position:relative; }}
  .chart-card .takeaway {{ margin-top:8px; font-size:11.5px; color:var(--slate-7); background:var(--slate-1); padding:6px 8px; border-radius:4px; }}
  .chart-card .takeaway b {{ color:var(--slate-9); }}
  section {{ margin-bottom:22px; }}
  section h2 {{ font-size:13px; margin:0 0 8px; color:var(--teal-d); text-transform:uppercase; letter-spacing:0.06em; border-bottom:1px solid var(--slate-3); padding-bottom:4px; }}
  .two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:22px; }}
  table.t {{ width:100%; border-collapse:collapse; font-size:12px; background:#fff; }}
  table.t th {{ text-align:left; font-size:10.5px; text-transform:uppercase; letter-spacing:0.04em; color:var(--slate-5); border-bottom:1.5px solid var(--slate-3); padding:5px 8px; font-weight:600; }}
  table.t th.num, table.t td.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  table.t th.aeo, table.t td.aeo {{ background:#ecfeff; }}
  table.t th.aeo {{ color:var(--teal-d); }}
  table.t td {{ padding:5px 8px; border-bottom:1px solid var(--slate-1); color:var(--slate-7); }}
  table.t td:first-child {{ color:var(--slate-9); }}
  table.t tr.subtotal td {{ background:var(--slate-1); font-weight:700; color:var(--slate-9); border-top:1.5px solid var(--slate-3); }}
  table.t a {{ color:var(--teal-d); text-decoration:none; }}
  table.t a:hover {{ text-decoration:underline; }}
  .up {{ color:var(--green); }} .down {{ color:var(--red); }}
  .win-row td {{ background:#f0fdf4; }}
  .note {{ font-size:11px; color:var(--slate-5); margin-top:6px; }}
  .takeaway-box {{ margin-top:8px; font-size:11.5px; color:var(--slate-7); background:var(--slate-1); padding:8px 10px; border-radius:4px; }}
  .takeaway-box b {{ color:var(--slate-9); }}
  .takeaway-box.win {{ background:#f0fdf4; border-left:3px solid var(--green); }}
  .takeaway-box.watch {{ background:#fffbeb; border-left:3px solid var(--amber); }}
  .takeaway-box ul {{ margin:4px 0 0; padding-left:18px; }} .takeaway-box li {{ margin-bottom:3px; }}
  .focus-status {{ font-weight:700; font-size:11px; }} .focus-status.done {{ color:var(--green); }}
  .prio-list {{ margin:0; padding-left:20px; }} .prio-list li {{ margin-bottom:6px; font-size:12.5px; }} .prio-list li b {{ color:var(--teal-d); }}
  .tag {{ display:inline-block; font-size:9.5px; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; padding:1px 6px; border-radius:8px; margin-left:6px; vertical-align:middle; }}
  .tag.aeo {{ background:#ecfeff; color:var(--teal-d); border:1px solid #a5f3fc; }}
  .tag.content {{ background:#f0fdf4; color:var(--green); border:1px solid #bbf7d0; }}
  .tag.technical {{ background:#fffbeb; color:var(--amber); border:1px solid #fde68a; }}
  .tag.product {{ background:#eef2ff; color:#4338ca; border:1px solid #c7d2fe; }}
  footer {{ margin-top:16px; font-size:10.5px; color:var(--slate-5); text-align:center; border-top:1px solid var(--slate-3); padding-top:6px; }}
  @media print {{ body {{ padding:16px 20px; font-size:11.5px; }} .chart-canvas-wrap {{ height:160px; }} header h1 {{ font-size:18px; }} }}
</style>
</head>
<body>
<div class="page">
  <header>
    <div>
      <h1>AEO Monthly Report — August 2026</h1>
      <div style="font-size:11px; color:var(--slate-5); margin-top:2px;">August vs July 2026 monthly review · GoFreight ↔ Novastacks</div>
    </div>
    <div class="meta">
      <div><strong>September 9, 2026</strong></div>
      <div>Monthly tables: Aug 1–31 vs Jul 1–31 · Weekly trends: Jan 5 – Aug 24</div>
      <div>GSC filtered to gofreight.com (support / api / archive subdomains excluded)</div>
    </div>
  </header>

  <div class="hook">
    <strong>Headline:</strong> August extended the growth run — total clicks <strong>+21.0% (7,734)</strong>, non-brand <strong>+25.4% (6,631, now 85.7% of all clicks)</strong>, and impressions <strong>+21.1% (1.51M)</strong>. The standout: <strong>AI-referred sessions rebounded +47.7% (392 → 579)</strong>, with <strong>ChatGPT recovering strongly (251 → 394)</strong> — July’s pullback reversed, confirming it was a temporary platform change, not a GoFreight problem. Every AI engine grew. AI visibility held roughly steady (<strong>29.3% → 28.0%</strong>) and AI citations edged up (<strong>7,947 → 8,163</strong>) across a wider page set (156 → 186 pages).
  </div>

  <div class="kpi-row">
    <div class="kpi"><div class="label">Total Clicks · August</div><div class="val">7,734</div>
      <div class="delta up">+{f(d_tot)} (+{d_tot_p:.1f}%) vs July · Non-brand {f(NB_J)} ({nbsh_j:.1f}%)</div></div>
    <div class="kpi"><div class="label">Non-Brand Clicks · August</div><div class="val">{f(NB_J)}</div>
      <div class="delta up">+{f(d_nb)} (+{d_nb_p:.1f}%) MoM</div></div>
    <div class="kpi"><div class="label">AI Sessions · August (GA4)</div><div class="val">579</div>
      <div class="delta up">+47.7% vs July 392 · ChatGPT rebounded</div></div>
    <div class="kpi"><div class="label">AI Visibility · August (WorkDuo)</div><div class="val">28.0%</div>
      <div class="delta down">−1.3 pts vs July · citations +2.7% (7,947 → 8,163)</div></div>
  </div>

  <div class="chart-row">
    <div class="chart-card">
      <h3>① Total Clicks vs Non-Brand Clicks (Weekly)</h3>
      <div class="sub">GSC gofreight.com, date-dim · non-brand = total minus brand-regex queries</div>
      <div class="chart-canvas-wrap"><canvas id="chart1"></canvas></div>
      <div class="takeaway"><b>Read:</b> Non-brand clicks kept climbing — August delivered <b>{f(NB_J)} non-brand clicks (+{d_nb_p:.1f}% MoM)</b> and non-brand share reached <b>{nbsh_j:.1f}% of total</b>, up from 82.7% in July. Impressions also grew +21% — the content program keeps compounding on the informational long-tail.</div>
    </div>
    <div class="chart-card">
      <h3>② AEO Visibility · Non-Brand by Engine (Weekly)</h3>
      <div class="sub">WorkDuo · 28 non-brand prompts (MOFU/TOFU/BOFU); self-mention rate per engine</div>
      <div class="chart-canvas-wrap"><canvas id="chart2"></canvas></div>
      <div class="takeaway"><b>Read:</b> <b>Google AI Overview stayed in the high-30s band</b> through August, recovering from the late-July dip. Blended non-brand visibility settled at <b>28.0% for August</b> (from 29.3% in July) — roughly steady. Perplexity and ChatGPT held their mid-range; the panel is stable after the mid-2026 platform shake-out.</div>
    </div>
    <div class="chart-card">
      <h3>③ AI Traffic Sessions (Weekly · GA4)</h3>
      <div class="sub">GA4 property 373075091, sessionSource matching AI platforms (chatgpt, perplexity, gemini, claude, copilot…)</div>
      <div class="chart-canvas-wrap"><canvas id="chart3"></canvas></div>
      <div class="takeaway"><b>Read:</b> AI sessions <b>rebounded sharply in August — 579 vs July’s 392 (+47.7%)</b>, a series high. <b>ChatGPT recovered (251 → 394)</b> as its July pullback reversed, and every other engine grew too (Gemini, Claude, Perplexity). The July dip was a temporary platform effect, now normalized (see the deep-dive below).</div>
    </div>
  </div>

  <div class="two-col">
    <section>
      <h2>August — What Was Done</h2>
      <table class="t">
        <thead><tr><th>#</th><th>Initiative</th><th>Status</th></tr></thead>
        <tbody>
          <tr><td class="num">1</td><td><b>Buyer-question content enhancements</b> — added focused single-question sections + FAQ to the pages AI engines cite, closing the content gaps mapped in July (implementation timeline, scalability, real-time visibility, accounting, etc.).</td><td><span class="focus-status done">DONE</span></td></tr>
          <tr><td class="num">2</td><td><b>Published 30 new articles</b> — August blog cadence (BAU).</td><td><span class="focus-status done">DONE</span></td></tr>
          <tr><td class="num">3</td><td><b>New title experiment on /solutions/air-freight &amp; /solutions/ocean-freight</b> (~Aug 20) — <b>ocean-freight impressions rose ~19%/day</b> after the change, surfacing for strong software queries (“sea freight export software” ~pos 5, “ocean freight software”, “air freight import software” ~pos 5). Air-freight steady. Early read — impressions are trend-sensitive, so we keep watching.</td><td><span class="focus-status done">DONE</span></td></tr>
          <tr><td class="num">4</td><td><b>Structured data updated for /solutions/air-freight &amp; /solutions/ocean-freight</b> — richer schema for better rich-result and AI extraction.</td><td><span class="focus-status done">DONE</span></td></tr>
          <tr><td class="num">5</td><td><b>Fixed the footer link bug on /solutions/air-export</b> — restored the internal link.</td><td><span class="focus-status done">DONE</span></td></tr>
          <tr><td class="num">6</td><td><b>llms.txt updated</b> — refreshed the AI-crawler manifest exposing key content to LLMs.</td><td><span class="focus-status done">DONE</span></td></tr>
        </tbody>
      </table>
      <div class="takeaway-box" style="margin-top:10px;"><b>Effect visible in the data:</b> Glossary clicks +61.1% and Blog +10.4% MoM; non-brand share climbed 82.7% → 85.7%; AI-referred sessions rebounded +47.7% (392 → 579) and AI citations edged up across a wider page set ({TOT['jun_pages']} → {TOT['jul_pages']} pages).</div>
    </section>

    <section>
      <h2>September 2026 — Next Action Items &amp; Priorities</h2>
      <ol class="prio-list">
        <li><b>Blog publishing — September</b> — keep expanding the topics where GoFreight is <b>not yet visible in AI Overview &amp; ChatGPT</b>, and add coverage for <b>popular terminal queries</b> to capture that traffic. <a href="https://docs.google.com/spreadsheets/d/1D7MDm4_4HpuIfjUe2CBTYat2AoTWRFLK2XgGBI8gpUc/edit?gid=1223294981#gid=1223294981" target="_blank">September plan</a>.<span class="tag content">Content</span><span class="tag aeo">AEO</span></li>
        <li><b>Improve the Solution &amp; Product pages</b> — execute the on-page improvements. <a href="https://docs.google.com/document/d/1i9skfgqCa3SLx_nbfiao5p_Z1o7GDsAJ_sgHP89eoPE/edit?tab=t.0" target="_blank">Plan</a>.<span class="tag product">Product</span><span class="tag aeo">AEO</span></li>
        <li><b>SEO × SEM collaboration</b> — identify the best opportunity keywords so SEM can spend budget / CPC where it converts best.<span class="tag technical">SEM</span></li>
        <li><b>[Experimental] “Preferred Sources” button on the blog</b> — invite readers to add GoFreight as a <a href="https://developers.google.com/search/docs/appearance/preferred-sources" target="_blank">Google preferred source</a> so new posts surface in their Discover/Chrome feed.<span class="tag technical">Technical</span><span class="tag aeo">AEO</span></li>
        <li><b>Newsletter-registration strategy</b> — propose a plan to grow newsletter sign-ups, supporting GoFreight’s September event.<span class="tag content">Growth</span></li>
      </ol>
      <div class="takeaway-box watch" style="margin-top:12px;"><b>Watch:</b> AI visibility eased slightly (−1.3pp) and primary-domain citations were roughly flat while the page set widened — the September plan targets the not-yet-visible AIO / ChatGPT queries directly. Also re-check the air/ocean title experiment in 4–6 weeks once more impression data accrues.</div>
    </section>
  </div>

  <section>
    <h2>Query Segment Breakdown (August vs July)</h2>
    <table class="t"><thead>
      <tr><th>Segment</th><th class="num">July Clicks</th><th class="num">August Clicks</th><th class="num">Click Δ</th><th class="num">Δ %</th><th class="num">July Impr</th><th class="num">August Impr</th><th class="num">Impr Δ</th></tr>
    </thead><tbody>
      {fr['seg']}
    </tbody></table>
    <div class="takeaway-box"><b>Read:</b> Non-branded grew <b>+{d_nb_p:.1f}% MoM (+{f(d_nb)})</b> while branded held roughly flat — the content flywheel again. Non-branded now stands at <b>{nbsh_j:.1f}% of all clicks</b>, up from 82.7% in July. Brand rows are measured on the full property (query-dim); non-brand is derived as total minus brand.</div>
  </section>

  <section>
    <h2>Subfolder Performance (August vs July) — with AI Citation Coverage</h2>
    <table class="t"><thead>
      <tr><th>Subfolder</th><th class="num">July Clicks</th><th class="num">August Clicks</th><th class="num">Click Δ</th><th class="num">Δ %</th><th class="num">July Impr</th><th class="num">August Impr</th><th class="num aeo">Pages Cited · July</th><th class="num aeo">Pages Cited · August</th></tr>
    </thead><tbody>
      {fr['sub']}
    </tbody></table>
    <p class="note">Totals reflect the primary gofreight.com property (support / api / archive subdomains excluded per the filter). <b>Pages Cited by AI</b> = distinct pages cited as a source by ChatGPT, Perplexity, or Google AI in WorkDuo-tracked responses that month, shown as <i>pages (total citations)</i>.</p>
    <div class="takeaway-box"><b>Read:</b> <b>Glossary surged +61.1%</b> (clicks 1,690 → 2,723) on the terminal-tracking pages — the biggest driver again — and <b>Blog grew +10.4%</b> (2,805 → 3,098). The customer-portal blog and homepage jumped in AI citations. Product / Pricing / Solutions clicks eased slightly (small bases); the September Product-page work targets them.</div>
  </section>

  <section>
    <h2>Top 30 Pages by Clicks (August vs July) — with AI Citations per Page</h2>
    <table class="t"><thead>
      <tr><th>#</th><th>Page</th><th>Recent Work</th><th class="num">July Clicks</th><th class="num">August Clicks</th><th class="num">Δ Clicks</th><th class="num">August Impr</th><th class="num aeo">AI Citations · July</th><th class="num aeo">AI Citations · August</th></tr>
    </thead><tbody>
      {fr['top30']}
    </tbody></table>
    <p class="note"><b>Recent Work</b> tags carried forward from prior reports (historical NovaStacks work markers); August’s specific refreshed / new-article URLs are not individually tagged here. <b>AI Citations</b> = WorkDuo-tracked AI responses citing this page as a source in the month.</p>
  </section>

  <section>
    <h2>Top 15 Most-Cited Pages by AI — A Different List Than the Click Winners</h2>
    <table class="t"><thead>
      <tr><th>#</th><th>Page</th><th class="num aeo">AI Citations · July</th><th class="num aeo">AI Citations · August</th><th class="num">Δ</th><th class="num">August Clicks</th><th class="num">In Click Top 30?</th></tr>
    </thead><tbody>
      {fr['top15']}
    </tbody></table>
    <div class="takeaway-box"><b>Read: SEO winners and AEO winners are different pages.</b> Google clicks flow to educational long-tail content; AI engines answering buying-intent prompts cite the <b>commercial pages</b> — platform-overview, best-tms-software, cargowise-vs-gofreight, best-freight-management-software, /product/integrations, and the customer-portal page. Most of these barely register in a click-ranked view, which is why the report tracks both axes.</div>
  </section>

  <section>
    <h2>Core Keyword Tracking — Commercial Cluster (GSC avg position by target page, United States market, July vs June)</h2>
    <table class="t"><thead>
      <tr><th>Core Keyword</th><th>Target Page</th><th class="num">July Impr (US)</th><th class="num">June Pos</th><th class="num">July Pos</th><th class="num">Δ Position</th><th>Note</th></tr>
    </thead><tbody>
      {fr['core']}
    </tbody></table>
    <p class="note">United States market only (GSC country = usa), filtered to <b>each keyword's specific target page</b> (query + page), not the blended all-pages average. Lower = better.</p>
    <div class="two-col" style="margin-top:10px;">
      <div class="takeaway-box win"><b>✓ Wins on the target page (US)</b>
        <ul>
          <li><b>The homepage broke into the top of the US SERP</b> — “freight forwarder software” 4.1 → <b>1.8</b> and “freight forwarding software” 5.8 → <b>2.5</b>. June’s cannibalization has resolved and the homepage now owns these terms.</li>
          <li><b>“best tms software”</b> climbed 5.7 (15.7 → 10.0), and “best freight management software” (6.2 → 4.4) and “freight tracking software” (6.6 → 4.9) improved on the best-fms blog.</li>
          <li><b>“freight management software” is won by the listicle</b> — <b>/blog/best-freight-management-software holds position ~2 (1.8)</b> in the US, both months. (Tracking was re-pointed from the homepage, which only surfaces weakly at ~33 for this query — the listicle is the page that actually ranks.)</li>
        </ul>
      </div>
      <div class="takeaway-box watch"><b>⚠ Watch (US, target page)</b>
        <ul>
          <li><b>“logistics crm software”</b> softened on the CRM listicle (15.1 → 17.3) and <b>“freight software”</b> eased (8.3 → 10.0). The August Solution-page work targets the commercial cluster.</li>
          <li>The homepage still surfaces weakly (~33) as a secondary URL for “freight management software”; low priority (zero clicks), but a canonical/internal-link nudge toward the listicle would tidy the signal.</li>
        </ul>
      </div>
    </div>
  </section>

  <section>
    <h2>AI Traffic Deep-Dive — The August Rebound</h2>
    <p class="note" style="margin-bottom:8px;">AI-referred sessions rose from 392 (July) to 579 (August), <b>+47.7%</b>. This section isolates <b>which engines and which pages</b> drove the recovery.</p>
    <div class="two-col" style="align-items:start;">
      <div>
        <table class="t"><thead>
          <tr><th>AI Source</th><th class="num">July</th><th class="num">August</th><th class="num">Δ</th></tr>
        </thead><tbody>
          {fr['src']}
        </tbody></table>
        <div class="takeaway-box win" style="margin-top:8px;"><b>ChatGPT recovered and led the rebound.</b> ChatGPT sessions climbed <b>{fr['cg_jun']} → {fr['cg_jul']} (+{fr['cg_drop']})</b>, reversing July’s dip and confirming that decline was a <b>temporary ChatGPT platform change, not a GoFreight loss</b>. Every other engine grew too — Gemini +35, Claude +8, Copilot +3 — so the recovery is broad-based, not a single-platform blip.</div>
      </div>
      <div>
        <table class="t"><thead>
          <tr><th>Landing pages that gained AI sessions</th><th class="num">July</th><th class="num">August</th><th class="num">Δ</th></tr>
        </thead><tbody>
          {fr['lp_gain']}
        </tbody></table>
      </div>
    </div>
    <div class="takeaway-box win" style="margin-top:10px;"><b>The homepage led the recovery.</b> The gain is broad-based across pages, with the <b>homepage adding the most (+47 sessions, 63 → 110)</b> alongside pricing and glossary pages — the same broad, cross-page shape that fell in July now moving the other way. This is the clearest confirmation that July’s dip was a <b>platform-level referral change</b> and not a ranking or content problem on GoFreight’s side: when the platform behaviour normalised, the sessions came back across the whole site at once.</div>
    <div class="takeaway-box win"><b>In plain terms — the AI dip is over.</b> In July, ChatGPT (the biggest AI referrer) briefly sent fewer visitors to every website while it changed how it built answers. In August that reversed:
      <ul>
        <li><b>ChatGPT visitors bounced back.</b> ChatGPT sent GoFreight <b>394 visitors in August, up from 251 in July</b> — more than fully recovering the July drop.</li>
        <li><b>Every AI engine grew.</b> It was not just ChatGPT — Google’s Gemini, Claude and Microsoft Copilot all sent more visitors too, so GoFreight’s AI reach is widening across platforms.</li>
        <li><b>The whole site benefited.</b> The extra AI visitors landed across the homepage, pricing and glossary pages — not one lucky article — which is exactly what a healthy, broad recovery looks like.</li>
      </ul>
      <b>Bottom line:</b> July’s AI-traffic dip was a temporary platform change, and August confirmed it — GoFreight’s AI referrals grew +47.7% and are now at their highest level of the year.</div>
    <div class="takeaway-box win"><b>Newly published content is compounding the gain.</b> August’s 30 new articles and the refreshed glossary are already earning AI referrals across engines, so the content program is adding fresh AI reach on top of the platform recovery — the Glossary subfolder alone grew +61% in organic clicks this month.</div>
  </section>

  <section>
    <h2>AEO Metrics — Month over Month</h2>
    <table class="t"><thead>
      <tr><th>Metric</th><th class="num">July 2026</th><th class="num">August 2026</th><th class="num">Change</th><th>Source</th></tr>
    </thead><tbody>
      {fr['aeo']}
    </tbody></table>
    <p class="note">AI Platform Sessions from GA4 direct (property 373075091). AI Visibility (non-brand) from the WorkDuo API. Pages Cited / Total Citations recounted from the WorkDuo API (occurrence-count, 28-non-brand + 11-branded prompt panel, project cmhk59aw9001mlo33c3t8n3rj).</p>
    <div class="takeaway-box win"><b>AEO performance: sessions rebounded and citations kept climbing.</b>
      <ul>
        <li><b>AI Platform Sessions grew +47.7%</b> (392 → 579, GA4 direct) — the July dip fully recovered, led by ChatGPT and supported by every other engine (deep-dive above).</li>
        <li><b>AI citations grew +{ac_g:.1f}%</b> ({f(ac_n)} → {f(ac_j)} across all properties) on a wider page set ({TOT['jun_pages']} → {TOT['jul_pages']} pages) — the comparison blogs and Product pages carry the load, and August’s new content is already being cited.</li>
        <li><b>Non-brand AI visibility held at 28.0%</b> (29.3% → 28.0%, a shallow −1.3pp), while GoFreight stayed the most-cited freight-software vendor in the category.</li>
      </ul>
    </div>
  </section>

  <footer>
    Sources: GSC (sc-domain:gofreight.com, date-dim for totals; page-dim for page/subfolder; page filter = gofreight.com, subdomains excluded; US-market core keywords filtered country=usa, per target page) · WorkDuo project cmhk59aw9001mlo33c3t8n3rj (28 non-brand prompts for visibility; all-prompt citations occurrence-recounted from /responses API) · GA4 property 373075091 (AI-referral sessions + source/landing-page analysis) · Generated 2026-09-09
  </footer>
</div>

<script>
const fmt = (n) => n===null?'n/a':n.toLocaleString();
const weekLabels = {week_labels_js};
const clicks   = {jsarr(fr['clicks_tot'])};
const nbClicks = {jsarr(fr['clicks_nb'])};
const chatGpt    = {jsarr(fr['chat'])};
const perplexity = {jsarr(fr['perp'])};
const googleAi   = {jsarr(fr['goog'])};
const aiSessions = {jsarr(fr['ais'])};

new Chart(document.getElementById('chart1'), {{ type:'line', data:{{ labels:weekLabels, datasets:[
  {{label:'Total clicks', data:clicks, borderColor:'#94a3b8', backgroundColor:'rgba(148,163,184,0.08)', borderWidth:2, borderDash:[4,3], tension:0.25, fill:false, pointRadius:2, pointBackgroundColor:'#94a3b8'}},
  {{label:'Non-brand clicks', data:nbClicks, borderColor:'#017d8e', backgroundColor:'rgba(1,125,142,0.12)', borderWidth:2.8, tension:0.25, fill:true, pointRadius:2.5, pointBackgroundColor:'#017d8e'}}
]}}, options:{{responsive:true, maintainAspectRatio:false, plugins:{{legend:{{position:'bottom',labels:{{font:{{size:10}},boxWidth:14,padding:6}}}}, tooltip:{{callbacks:{{label:(c)=>`${{c.dataset.label}}: ${{fmt(c.parsed.y)}}`}}}}}}, scales:{{y:{{beginAtZero:true,ticks:{{font:{{size:10}},callback:(v)=>v.toLocaleString()}},grid:{{color:'#f1f5f9'}}}}, x:{{ticks:{{font:{{size:10}},maxRotation:0,autoSkip:true,maxTicksLimit:8}},grid:{{display:false}}}}}}}}}});

new Chart(document.getElementById('chart2'), {{ type:'line', data:{{ labels:weekLabels, datasets:[
  {{label:'Google AI Overview', data:googleAi, borderColor:'#0891b2', backgroundColor:'rgba(8,145,178,0.08)', borderWidth:2.2, tension:0.3, pointRadius:1.8}},
  {{label:'Perplexity', data:perplexity, borderColor:'#16a34a', backgroundColor:'rgba(22,163,74,0.08)', borderWidth:2.2, tension:0.3, pointRadius:1.8}},
  {{label:'ChatGPT', data:chatGpt, borderColor:'#d97706', backgroundColor:'rgba(217,119,6,0.08)', borderWidth:2.2, tension:0.3, pointRadius:1.8}}
]}}, options:{{responsive:true, maintainAspectRatio:false, plugins:{{legend:{{position:'bottom',labels:{{font:{{size:10}},boxWidth:10,padding:6}}}}, tooltip:{{callbacks:{{label:(c)=>`${{c.dataset.label}}: ${{c.parsed.y.toFixed(1)}}%`}}}}}}, scales:{{y:{{beginAtZero:true,max:45,ticks:{{font:{{size:10}},callback:(v)=>v+'%'}},grid:{{color:'#f1f5f9'}}}}, x:{{ticks:{{font:{{size:10}},maxRotation:0,autoSkip:true,maxTicksLimit:8}},grid:{{display:false}}}}}}}}}});

new Chart(document.getElementById('chart3'), {{ type:'line', data:{{ labels:weekLabels, datasets:[
  {{label:'AI sessions', data:aiSessions, borderColor:'#7c3aed', backgroundColor:'rgba(124,58,237,0.15)', borderWidth:2.5, tension:0.3, fill:true, pointRadius:2.5, pointBackgroundColor:'#7c3aed', spanGaps:false}}
]}}, options:{{responsive:true, maintainAspectRatio:false, plugins:{{legend:{{display:false}}, tooltip:{{callbacks:{{label:(c)=>`${{c.parsed.y}} AI sessions`}}}}}}, scales:{{y:{{beginAtZero:true,suggestedMax:150,ticks:{{stepSize:25,font:{{size:10}}}},grid:{{color:'#f1f5f9'}}}}, x:{{ticks:{{font:{{size:10}},maxRotation:0,autoSkip:true,maxTicksLimit:8}},grid:{{display:false}}}}}}}}}});
</script>
</body>
</html>'''

import os
outdir='/Users/ekiriandra/seo-projects/novastacks/clients/gofreight/output/reports'
os.makedirs(outdir,exist_ok=True)
open(outdir+'/gofreight_august_2026_report.html','w',encoding='utf-8').write(HTML)
print('WROTE',outdir+'/gofreight_august_2026_report.html','len',len(HTML))
