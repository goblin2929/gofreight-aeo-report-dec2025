# GoFreight AEO Monthly Report - Data Extraction & Process Guide

## Overview
This document standardizes the monthly AEO performance report creation process, including data sources, extraction methods, calculations, and validation checks.

---

## Data Sources & Access

### 1. Google Search Console (GSC)
**Purpose:** Organic search performance metrics
**Access:** MCP Server `google-search-console`
**Site URL:** `sc-domain:gofreight.com`

#### Metrics to Extract:
| Metric | Tool/Query | Notes |
|--------|------------|-------|
| Site-level clicks, impressions, CTR, position | `get_performance_data` | Set date range for current + previous month |
| Subfolder performance | `get_performance_data` with `dimensions: ["page"]` | Group by URL path prefix |
| Top pages | `get_performance_data` with `dimensions: ["page"]` | Sort by clicks desc |
| Top keywords | `get_performance_data` with `dimensions: ["query"]` | Sort by clicks desc |

#### Example Query:
```
mcp__google-search-console__get_performance_data
- site_url: "sc-domain:gofreight.com"
- start_date: "2024-12-01"
- end_date: "2024-12-31"
- dimensions: ["page"] or ["query"] or ["date"]
- row_limit: 1000
```

#### Subfolder Grouping Logic:
- `/blog/*` → Blog
- `/solutions/*` → Solutions
- `/customers/*` → Customers
- `/pricing` → Pricing
- `/get-demo` → Get Demo
- `/` (homepage only) → Homepage

---

### 2. Google Analytics 4 (GA4)
**Purpose:** Conversion and engagement metrics
**Access:** Direct API via `curl` with Application Default Credentials
**Property ID:** `373075091`

#### Metrics to Extract:
| Metric | Dimensions | Notes |
|--------|------------|-------|
| Sessions by page | pagePath | For conversion rate calculations |
| Form starts | eventName = "form_start" | Interest signal |
| Form submits | eventName = "form_submit" | Lead conversion |
| Demo submissions | eventName = "get_demo_form_submit_hero_success" | High-intent conversion |

#### API Setup:
```bash
# Authenticate (one-time)
gcloud auth application-default login --scopes="https://www.googleapis.com/auth/analytics.readonly"
gcloud auth application-default set-quota-project seo-agency-478605

# Query example
curl -X POST "https://analyticsdata.googleapis.com/v1beta/properties/373075091:runReport" \
  -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "dateRanges": [{"startDate": "2024-12-01", "endDate": "2024-12-31"}],
    "dimensions": [{"name": "pagePath"}],
    "metrics": [{"name": "sessions"}, {"name": "eventCount"}]
  }'
```

#### Conversion Formulas:
| Metric | Formula |
|--------|---------|
| Form Start Rate | Form Starts ÷ Sessions × 100 |
| Conversion Rate | Form Submits ÷ Sessions × 100 |
| Form Completion Rate | Form Submits ÷ Form Starts × 100 |

---

### 3. Workduo.ai (AEO Metrics)
**Purpose:** AI visibility and share of voice metrics
**Access:** Workduo Dashboard (API auth issues - use screenshot export)
**Project ID:** `cmhk59aw9001mlo33c3t8n3rj`

#### Metrics to Extract:
| Metric | Description |
|--------|-------------|
| AI Visibility % | % of monitored prompts where brand appears |
| Share of Voice % | Brand's share of total AI mentions |
| Avg Position | Average ranking position in AI responses |
| Competitive Rank | Position vs tracked competitors |

#### Current Process (Manual):
1. Log into Workduo dashboard
2. Navigate to project → AI Search Brand Visibility
3. Screenshot the competitor comparison table
4. Extract values for GoFreight and top competitors

#### Competitors to Track:
1. CargoWise
2. Magaya Supply Chain
3. Descartes Forwarder Enterprise
4. Shipthis
5. GoFreight (self)

---

### 4. Content Delivery Tracker (Google Sheet)
**Purpose:** Track deliverables shipped vs pending
**Spreadsheet ID:** `1D7MDm4_4HpuIfjUe2CBTYat2AoTWRFLK2XgGBI8gpUc`
**Sheet:** `Novastacks Content delivery Tracker`

#### Key Columns:
| Column | Content |
|--------|---------|
| A | Contractual Month |
| B | # |
| C | Content Production Initiative |
| D | Title |
| F | Status |
| G | Page Type |
| H | Production URL |

#### Status Values:
- `Published` → Include in "Deliverables Shipped"
- `Gofreight Approved yet to Publish` → Include in "Pending Publication"
- `To Do` → Do not include in report

#### Query Example:
```
mcp__google-sheets__get_sheet_data
- spreadsheet_id: "1D7MDm4_4HpuIfjUe2CBTYat2AoTWRFLK2XgGBI8gpUc"
- sheet: "Novastacks Content delivery Tracker"
- range: "A1:S50"
```

---

## Report Sections & Data Mapping

### Section 1: Executive Summary KPIs
| KPI | Source | Calculation |
|-----|--------|-------------|
| Total Clicks | GSC | Direct from API |
| Total Impressions | GSC | Direct from API |
| Avg CTR | GSC | Direct from API (or Clicks ÷ Impressions × 100) |
| Avg Position | GSC | Direct from API |
| MoM Change | GSC | (Current - Previous) ÷ Previous × 100 |

### Section 2: Deliverables Shipped
| Item | Source | Filter |
|------|--------|--------|
| Customer Story Pages | Content Tracker | Status = "Published", Page Type = "Customer Page" |
| CargoWise Articles | Content Tracker | Status = "Published", Initiative contains "CargoWise" |
| Blog Content | Content Tracker | Status = "Published", Page Type = "Blog" |
| Pending Content | Content Tracker | Status = "Gofreight Approved yet to Publish" |

### Section 3: Subfolder Performance
| Metric | Source | Notes |
|--------|--------|-------|
| Clicks by subfolder | GSC | Group pages by URL prefix |
| Impressions by subfolder | GSC | Group pages by URL prefix |
| % of Site Total | Calculated | Subfolder ÷ Site Total × 100 |
| MoM Change | GSC | Compare to previous month |

### Section 4: Conversion Performance
| Metric | Source |
|--------|--------|
| Sessions by subfolder | GA4 |
| Form Starts by subfolder | GA4 |
| Form Submits by subfolder | GA4 |
| Conversion rates | Calculated (see formulas above) |

### Section 5: Top Pages & Keywords
| Data | Source | Limit |
|------|--------|-------|
| Top Pages by Clicks | GSC | Top 10-15 |
| Top Keywords by Clicks | GSC | Top 10-15 |
| Ranking URL for keywords | GSC | `dimensions: ["query", "page"]` |

### Section 6: AEO / AI Visibility
| Metric | Source |
|--------|--------|
| All AEO metrics | Workduo screenshot |
| Competitor comparison | Workduo screenshot |

---

## Validation Checklist

### Before Publishing, Verify:

- [ ] **GSC totals match:** Sum of subfolder clicks = site total clicks
- [ ] **% calculations correct:** Subfolder ÷ Total × 100 (not subfolder ÷ subfolder)
- [ ] **Content status accurate:** Cross-check "Published" items are actually live on site
- [ ] **AEO data from source:** Use actual Workduo screenshot, not estimated values
- [ ] **MoM comparisons use same date ranges:** e.g., Dec 1-31 vs Nov 1-30
- [ ] **No fabricated data:** All metrics traced to actual data source

### Common Mistakes to Avoid:

1. **Wrong % of total base:** Always use SITE TOTAL as denominator, not subtotal
2. **Content marked "shipped" that isn't live:** Verify against actual URLs
3. **AEO position inverted:** Lower position = better (1.5 beats 3.1)
4. **Mixing archive vs main site data:** archive.gofreight.com is separate from gofreight.com

---

## Monthly Report Workflow

### Week 1 of New Month:
1. [ ] Export GSC data for previous month (full month)
2. [ ] Export GSC data for month before (for MoM comparison)
3. [ ] Query GA4 for conversion metrics
4. [ ] Screenshot Workduo AEO dashboard
5. [ ] Pull Content Tracker sheet data

### Week 1-2:
6. [ ] Build/update report with new data
7. [ ] Calculate all derived metrics
8. [ ] Run validation checklist
9. [ ] Internal review

### Week 2:
10. [ ] Client delivery
11. [ ] Archive report and data sources

---

## File Locations

| File | Path |
|------|------|
| Report HTML | `/Users/tinachu/gofreight-aeo-report-dec2025/gofreight_december_2025_report.html` |
| GitHub Pages | `index.html` (copy of report) |
| This Process Doc | `REPORT_PROCESS.md` |
| AEO Screenshot | `/Users/tinachu/Desktop/AEO gofreight dec 25 data.jpg` |

---

## Contacts & Access

| System | Access Method |
|--------|---------------|
| GSC | MCP Server (auto-authenticated) |
| GA4 | gcloud ADC + Property 373075091 |
| Workduo | Dashboard login (API pending) |
| Content Tracker | Google Sheets MCP Server |

---

*Last Updated: January 2026*
*Report Version: December 2025*
