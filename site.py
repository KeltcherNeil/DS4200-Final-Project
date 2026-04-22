import os, json, webbrowser
from visualization import (
    df_no_world, disorder_cols, REGION_COLORS,
    chart_spec, anxiety_top10_spec,
    gdp_top_spec, gdp_bottom_spec,
    gdp_trend_spec, region_avg_spec, region_gdp_spec, country_time_spec,
    DISORDER_COLOR_RANGE, mh_top10_json, geo_spec,
    land_geojson_str, BASE, top10_time_spec,
)

# ---------------------------------------------------------------------------
# Summary stats
# ---------------------------------------------------------------------------
num_countries    = df_no_world["Country"].nunique()
year_min         = int(df_no_world["Year"].min())
year_max         = int(df_no_world["Year"].max())
num_records      = len(df_no_world)
disorder_means   = {col: round(df_no_world[col].mean(), 3) for col in disorder_cols}
highest_disorder = max(disorder_means, key=disorder_means.get)
highest_val      = disorder_means[highest_disorder]
lowest_disorder  = min(disorder_means, key=disorder_means.get)

# Total prevalence trend (global mean, first vs last year)
_first = df_no_world[df_no_world["Year"] == year_min][disorder_cols].mean().sum()
_last  = df_no_world[df_no_world["Year"] == year_max][disorder_cols].mean().sum()
trend_pct = round((_last - _first) / _first * 100, 1)

# GDP vs mental health summary stats (use agg from visualization.py - one row per country)
import numpy as _np
from visualization import agg as _agg

_s = _agg.copy()
_s["total"]   = _s[disorder_cols].sum(axis=1)
_s["log_GDP"] = _np.log10(_s["GDP"])

gdp_median_val    = _s["GDP"].median()
high_gdp_avg      = round(_s[_s["GDP"] >= gdp_median_val]["total"].mean(), 2)
low_gdp_avg       = round(_s[_s["GDP"] <  gdp_median_val]["total"].mean(), 2)
top_total_country = _s.loc[_s["total"].idxmax(), "Country"]
top_total_val     = round(_s["total"].max(), 2)

_corrs = {
    col: round(float(_s[["log_GDP", col]].dropna().corr().iloc[0, 1]), 3)
    for col in disorder_cols
}
most_corr_disorder  = max(_corrs, key=_corrs.get)
most_corr_r         = _corrs[most_corr_disorder]
least_corr_disorder = min(_corrs, key=_corrs.get)
least_corr_r        = _corrs[least_corr_disorder]

_region_totals    = _s.groupby("region_label")["total"].mean()
highest_region    = _region_totals.idxmax()
highest_region_val = round(_region_totals.max(), 2)
lowest_region     = _region_totals.idxmin()
lowest_region_val = round(_region_totals.min(), 2)

# ---------------------------------------------------------------------------
# Table data
# ---------------------------------------------------------------------------
table_df = df_no_world[["Country", "Year"] + disorder_cols + ["GDP"]].copy()
for col in disorder_cols:
    table_df[col] = table_df[col].round(4)
table_df["GDP"] = table_df["GDP"].round(0).astype("Int64")
table_data = table_df.to_json(orient="records")

country_list = sorted(df_no_world["Country"].unique().tolist())
country_options_html = "\n".join(
    f'          <option value="{c}">{c}</option>' for c in country_list
)

# ---------------------------------------------------------------------------
# CDN links
# ---------------------------------------------------------------------------
CDN_VEGA     = "https://cdn.jsdelivr.net/npm/vega@6"
CDN_VEGALITE = "https://cdn.jsdelivr.net/npm/vega-lite@6.1.0"
CDN_EMBED    = "https://cdn.jsdelivr.net/npm/vega-embed@7"
CDN_BS_CSS   = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
CDN_BS_JS    = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
CDN_DT_CSS   = "https://cdn.datatables.net/2.0.8/css/dataTables.bootstrap5.min.css"
CDN_DT_JS    = "https://cdn.datatables.net/2.0.8/js/dataTables.min.js"
CDN_DT_BS_JS = "https://cdn.datatables.net/2.0.8/js/dataTables.bootstrap5.min.js"
CDN_JQUERY   = "https://code.jquery.com/jquery-3.7.1.min.js"
CDN_BI       = "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"
CDN_D3       = "https://cdn.jsdelivr.net/npm/d3@7"

SITE_TITLE = "Mental Health Across the Globe"

# ---------------------------------------------------------------------------
# Shared rotating globe - land data embedded inline (no runtime CDN fetch)
# ---------------------------------------------------------------------------
GLOBE_SCRIPT = f"""<script>
(function () {{
  const sz = 210, r = 103;
  const proj = d3.geoOrthographic()
    .scale(r).translate([105, 105]).rotate([0, -28]);
  const path = d3.geoPath().projection(proj);
  const svg = d3.select("#header-globe").append("svg")
    .attr("width", sz).attr("height", sz);
  const defs = svg.append("defs");
  const og = defs.append("radialGradient").attr("id", "hg-ocean")
    .attr("cx", "38%").attr("cy", "32%");
  og.append("stop").attr("offset",   "0%").attr("stop-color", "#3b82f6").attr("stop-opacity", 0.5);
  og.append("stop").attr("offset", "100%").attr("stop-color", "#0d1b4b").attr("stop-opacity", 0.85);
  const hl = defs.append("radialGradient").attr("id", "hg-light")
    .attr("cx", "32%").attr("cy", "26%").attr("r", "55%");
  hl.append("stop").attr("offset",   "0%").attr("stop-color", "#fff").attr("stop-opacity", 0.22);
  hl.append("stop").attr("offset", "100%").attr("stop-color", "#fff").attr("stop-opacity", 0);
  svg.append("circle").attr("cx", 105).attr("cy", 105).attr("r", r)
    .attr("fill", "url(#hg-ocean)").attr("stroke", "rgba(255,255,255,0.2)").attr("stroke-width", 1);
  const gratPath = svg.append("path").datum(d3.geoGraticule()())
    .attr("fill", "none").attr("stroke", "rgba(255,255,255,0.09)").attr("stroke-width", 0.6);
  const landPath = svg.append("path")
    .attr("fill", "rgba(96,165,250,0.65)").attr("stroke", "rgba(255,255,255,0.35)").attr("stroke-width", 0.4);
  svg.append("circle").attr("cx", 105).attr("cy", 105).attr("r", r)
    .attr("fill", "url(#hg-light)").attr("pointer-events", "none");
  landPath.datum({land_geojson_str});
  let lam = 0;
  (function tick() {{
    lam += 0.12;
    proj.rotate([lam, -28]);
    gratPath.attr("d", path);
    landPath.attr("d", path);
    requestAnimationFrame(tick);
  }})();
}})();
</script>"""

GLOBE_HTML = """
      <div class="header-globe-wrap">
        <div id="header-globe"></div>
      </div>"""

# ---------------------------------------------------------------------------
# Shared CSS (injected into every page)
# ---------------------------------------------------------------------------
SHARED_CSS = """
    :root {
      --navy:        #0d1b4b;
      --navy-mid:    #1a3169;
      --blue:        #1e40af;
      --blue-mid:    #2952a3;
      --blue-light:  #3b82f6;
      --bg:          #f4f6fb;
      --bg-card:     #ffffff;
      --border:      #dde3f0;
      --border-dark: #b8c2dc;
      --text-head:   #0d1b4b;
      --text-body:   #374151;
      --text-muted:  #6b7280;
    }

    *, *::before, *::after { box-sizing: border-box; }

    body {
      background: var(--bg);
      font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
      font-size: 0.95rem;
      color: var(--text-body);
      margin: 0;
    }

    /* ── Navbar ── */
    .site-nav {
      background: var(--navy);
      border-bottom: 3px solid var(--blue-light);
      padding: 0 2rem;
    }
    .site-nav .navbar-brand {
      font-size: 1rem;
      font-weight: 700;
      letter-spacing: 0.01em;
      color: #fff !important;
      padding: 0.85rem 0;
    }
    .site-nav .navbar-brand span.brand-sub {
      font-weight: 400;
      opacity: 0.65;
      font-size: 0.85rem;
      margin-left: 0.4rem;
    }
    .site-nav .nav-link {
      color: rgba(255,255,255,0.72) !important;
      font-size: 0.85rem;
      font-weight: 500;
      letter-spacing: 0.02em;
      padding: 0.9rem 1rem !important;
      border-bottom: 3px solid transparent;
      margin-bottom: -3px;
      transition: color 0.15s, border-color 0.15s;
      white-space: nowrap;
    }
    .site-nav .nav-link:hover {
      color: #fff !important;
      border-bottom-color: rgba(255,255,255,0.4);
    }
    .site-nav .nav-link.active {
      color: #fff !important;
      border-bottom-color: var(--blue-light);
    }

    /* ── Page header ── */
    .page-header {
      background: var(--navy);
      color: #fff;
      padding: 3rem 2rem 3rem;
      border-bottom: 1px solid var(--navy-mid);
    }
    .page-header .eyebrow {
      font-size: 0.72rem;
      font-weight: 600;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--blue-light);
      margin-bottom: 0.6rem;
    }
    .page-header h1 {
      font-size: clamp(1.5rem, 3vw, 2.1rem);
      font-weight: 700;
      letter-spacing: -0.01em;
      margin-bottom: 0.75rem;
      line-height: 1.2;
    }
    .page-header p {
      font-size: 0.93rem;
      color: rgba(255,255,255,0.72);
      max-width: 680px;
      line-height: 1.7;
      margin-bottom: 0;
    }
    /* ── Chart vis containers must have explicit width for vega container sizing ── */
    #vis, #vis-top10, #vis4a, #vis4b, #vis-geo,
    #vis-region, #vis-region-gdp, #vis-country-time { width: 100%; min-height: 10px; }
    .bar-panels { flex: 1; min-width: 0; }

    /* ── D3 disorder pills ── */
    .dis-pills {
      display: flex;
      flex-wrap: wrap;
      gap: 0.45rem;
      padding: 0.9rem 1.25rem;
      background: #f8f9fc;
      border-bottom: 1px solid var(--border);
    }
    .dis-pills .dis-label {
      font-size: 0.72rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      color: var(--text-muted);
      align-self: center;
      margin-right: 0.25rem;
      white-space: nowrap;
    }
    .dis-pill {
      display: inline-flex;
      align-items: center;
      padding: 0.28rem 0.75rem;
      border-radius: 4px;
      border: 1px solid var(--border-dark);
      background: #fff;
      color: var(--text-body);
      font-size: 0.79rem;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.12s, color 0.12s, border-color 0.12s;
      user-select: none;
      line-height: 1.4;
    }
    .dis-pill:hover {
      border-color: var(--blue-light);
      color: var(--blue);
      background: #f0f4ff;
    }
    .dis-pill.active {
      background: var(--navy);
      border-color: var(--navy);
      color: #fff;
    }

    /* ── D3 tooltip ── */
    .d3-tip {
      position: absolute;
      background: rgba(13,27,75,0.92);
      color: #fff;
      padding: 0.45rem 0.75rem;
      border-radius: 5px;
      font-size: 0.82rem;
      pointer-events: none;
      z-index: 9999;
      line-height: 1.55;
      box-shadow: 0 4px 16px rgba(0,0,0,0.22);
      white-space: nowrap;
    }

    /* ── Section header ── */
    .section-header {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin: 2.5rem 0 1rem;
      padding-bottom: 0.6rem;
      border-bottom: 2px solid var(--border);
    }
    .section-header h2 {
      font-size: 1rem;
      font-weight: 700;
      color: var(--text-head);
      margin: 0;
      letter-spacing: 0.01em;
      text-transform: uppercase;
      font-size: 0.78rem;
    }
    .section-header .section-icon {
      width: 28px;
      height: 28px;
      background: var(--navy);
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-size: 0.8rem;
      flex-shrink: 0;
    }

    /* ── Stat cards ── */
    .stat-card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-left: 4px solid var(--blue-mid);
      border-radius: 6px;
      padding: 1.25rem 1.1rem;
    }
    .stat-card .stat-value {
      font-size: 1.75rem;
      font-weight: 700;
      color: var(--text-head);
      line-height: 1.1;
    }
    .stat-card .stat-label {
      font-size: 0.78rem;
      color: var(--text-muted);
      margin-top: 0.3rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-weight: 500;
    }

    /* ── Disorder summary cards ── */
    .disorder-card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-top: 3px solid var(--accent-color, var(--blue-mid));
      border-radius: 6px;
      padding: 1.2rem 1rem;
      text-align: center;
    }
    .disorder-card .d-icon {
      font-size: 1.4rem;
      color: var(--accent-color, var(--blue-mid));
      display: block;
      margin-bottom: 0.5rem;
    }
    .disorder-card .d-value {
      font-size: 1.4rem;
      font-weight: 700;
      color: var(--text-head);
      line-height: 1.1;
    }
    .disorder-card .d-label {
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-top: 0.3rem;
      font-weight: 500;
    }

    /* ── Chart card ── */
    .chart-card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 6px;
      overflow: hidden;
    }
    .chart-card-header {
      padding: 1rem 1.25rem 0.75rem;
      border-bottom: 1px solid var(--border);
    }
    .chart-card-header h3 {
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text-head);
      margin: 0 0 0.25rem;
    }
    .chart-card-header p {
      font-size: 0.82rem;
      color: var(--text-muted);
      margin: 0;
      line-height: 1.5;
    }
    .chart-card-body {
      padding: 1rem 1.25rem 1.25rem;
    }
    .chart-insight {
      margin: 0 1.25rem 1.25rem;
      padding: 0.9rem 1.1rem;
      background: #f4f6fb;
      border-left: 4px solid #3b5bdb;
      border-radius: 0 6px 6px 0;
      font-size: 0.92rem;
      line-height: 1.75;
      color: #374151;
    }
    .chart-insight p {
      margin: 0;
    }

    /* ── Vega-embed controls ── */
    .vega-embed .vega-bindings {
      display: flex;
      flex-wrap: wrap;
      gap: 1rem 2.5rem;
      align-items: flex-start;
      padding: 0.9rem 1.25rem;
      background: #f8f9fc;
      border-bottom: 1px solid var(--border);
      margin-bottom: 0;
    }
    .vega-embed .vega-bind {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.4rem;
    }
    .vega-embed .vega-bind-name {
      font-size: 0.72rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      color: var(--text-muted);
      white-space: nowrap;
      margin-right: 0.15rem;
    }

    /* Hide native radio input, style label as pill toggle */
    .vega-embed input[type="radio"] {
      position: absolute;
      opacity: 0;
      width: 0;
      height: 0;
      pointer-events: none;
    }
    .vega-embed label {
      display: inline-flex;
      align-items: center;
      padding: 0.28rem 0.7rem;
      border-radius: 4px;
      border: 1px solid var(--border-dark);
      background: #fff;
      color: var(--text-body);
      font-size: 0.79rem;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.12s, color 0.12s, border-color 0.12s;
      user-select: none;
      line-height: 1.4;
    }
    .vega-embed label:hover {
      border-color: var(--blue-light);
      color: var(--blue);
      background: #f0f4ff;
    }
    .vega-embed label:has(input[type="radio"]:checked) {
      background: var(--navy);
      border-color: var(--navy);
      color: #fff;
    }

    /* Disorder select dropdown */
    .vega-embed select {
      border: 1px solid var(--border-dark);
      border-radius: 4px;
      padding: 0.28rem 2rem 0.28rem 0.6rem;
      font-size: 0.82rem;
      font-weight: 500;
      color: var(--text-head);
      background: #fff;
      cursor: pointer;
      appearance: none;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' fill='%230d1b4b' viewBox='0 0 16 16'%3E%3Cpath d='M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 0.55rem center;
      transition: border-color 0.12s;
    }
    .vega-embed select:focus { outline: none; border-color: var(--blue-light); }
    .vega-embed select:hover { border-color: var(--blue-light); }

    /* ── Chart + HTML legend wrapper ── */
    .chart-with-legend {
      display: flex;
      gap: 1.25rem;
      align-items: flex-start;
    }
    .chart-with-legend > [id^="vis"] {
      flex: 1;
      min-width: 0;
    }
    .html-legend {
      flex-shrink: 0;
      background: #fff;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 0.9rem 1rem;
      min-width: 155px;
    }
    .html-legend .legend-title {
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      color: var(--text-muted);
      margin-bottom: 0.6rem;
    }
    .html-legend .legend-item {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 0.45rem;
      font-size: 0.82rem;
      color: var(--text-body);
    }
    .html-legend .legend-swatch {
      display: inline-block;
      width: 12px;
      height: 12px;
      border-radius: 2px;
      flex-shrink: 0;
    }

    /* ── Data explorer ── */
    .explorer-toolbar {
      background: var(--navy);
      padding: 0.75rem 1.25rem;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.75rem;
    }
    .explorer-toolbar h3 {
      color: #fff;
      font-size: 0.88rem;
      font-weight: 600;
      margin: 0;
    }
    .filter-wrap {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-left: auto;
    }
    .filter-wrap label {
      color: rgba(255,255,255,0.75);
      font-size: 0.78rem;
      font-weight: 500;
      white-space: nowrap;
    }
    .filter-wrap select {
      border: 1px solid rgba(255,255,255,0.3);
      border-radius: 4px;
      padding: 0.3rem 2rem 0.3rem 0.6rem;
      font-size: 0.82rem;
      color: var(--navy);
      background: #fff;
      cursor: pointer;
      min-width: 175px;
      max-width: 230px;
      appearance: none;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' fill='%230d1b4b' viewBox='0 0 16 16'%3E%3Cpath d='M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 0.55rem center;
    }
    .filter-wrap select:focus { outline: none; }
    .clear-btn {
      background: rgba(255,255,255,0.12);
      border: 1px solid rgba(255,255,255,0.25);
      color: rgba(255,255,255,0.85);
      border-radius: 4px;
      padding: 0.3rem 0.65rem;
      font-size: 0.78rem;
      cursor: pointer;
      transition: background 0.15s;
      white-space: nowrap;
    }
    .clear-btn:hover { background: rgba(255,255,255,0.22); }

    table.dataTable thead th {
      background: #1e3a6e !important;
      color: #fff !important;
      font-weight: 600;
      font-size: 0.8rem;
      letter-spacing: 0.02em;
      border-color: #2952a3 !important;
    }
    table.dataTable tbody td { font-size: 0.83rem; }
    table.dataTable tbody tr:hover { background: #eef1fa !important; }

    /* ── CTA buttons ── */
    .btn-primary-site {
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      background: var(--blue-light);
      color: #fff;
      padding: 0.6rem 1.4rem;
      border-radius: 4px;
      font-weight: 600;
      font-size: 0.88rem;
      text-decoration: none;
      border: none;
      transition: background 0.15s;
    }
    .btn-primary-site:hover { background: #2563eb; color: #fff; }
    .btn-outline-site {
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      background: transparent;
      color: rgba(255,255,255,0.85);
      padding: 0.6rem 1.4rem;
      border-radius: 4px;
      font-weight: 500;
      font-size: 0.88rem;
      text-decoration: none;
      border: 1px solid rgba(255,255,255,0.3);
      transition: background 0.15s, border-color 0.15s;
    }
    .btn-outline-site:hover {
      background: rgba(255,255,255,0.1);
      border-color: rgba(255,255,255,0.5);
      color: #fff;
    }

    /* ── Footer ── */
    .site-footer {
      background: var(--navy);
      color: rgba(255,255,255,0.55);
      font-size: 0.8rem;
      border-top: 1px solid var(--navy-mid);
      padding: 2rem 0;
    }
    .site-footer strong { color: rgba(255,255,255,0.85); }
    .site-footer a { color: rgba(255,255,255,0.55); text-decoration: none; }
    .site-footer a:hover { color: rgba(255,255,255,0.85); }

    /* ── Nav page card (index) ── */
    .nav-card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 1.5rem;
      text-decoration: none;
      color: var(--text-body);
      display: block;
      transition: border-color 0.15s, box-shadow 0.15s;
    }
    .nav-card:hover {
      border-color: var(--blue-light);
      box-shadow: 0 4px 16px rgba(30,64,175,0.1);
      color: var(--text-body);
    }
    .nav-card .nc-icon {
      width: 40px;
      height: 40px;
      background: var(--navy);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-size: 1.1rem;
      margin-bottom: 0.9rem;
    }
    .nav-card h3 {
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text-head);
      margin: 0 0 0.3rem;
    }
    .nav-card p {
      font-size: 0.82rem;
      color: var(--text-muted);
      margin: 0;
      line-height: 1.5;
    }
    .nav-card .nc-arrow {
      font-size: 0.8rem;
      color: var(--blue-light);
      margin-top: 0.75rem;
      font-weight: 600;
    }

    /* ── Header globe layout ── */
    .header-inner {
      display: flex;
      align-items: center;
      gap: 2.5rem;
    }
    .header-text { flex: 1; min-width: 0; }
    .header-globe-wrap {
      flex-shrink: 0;
      opacity: 0.9;
      filter: drop-shadow(0 0 18px rgba(59,130,246,0.35));
    }
    @media (max-width: 720px) {
      .header-globe-wrap { display: none; }
    }
"""

# ---------------------------------------------------------------------------
# Nav generator (active page highlighted)
# ---------------------------------------------------------------------------
def make_nav(active):
    pages = [
        ("index.html",             "Home"),
        ("mental_health.html",     "Mental Health"),
        ("gdp_mental_health.html", "GDP vs. Mental Health"),
        ("key_findings.html",      "Key Findings &amp; Conclusions"),
    ]
    items = ""
    for href, label in pages:
        cls = "nav-link active" if active == href else "nav-link"
        items += f"""
      <li class="nav-item">
        <a class="{cls}" href="{href}">
          {label}
        </a>
      </li>"""
    return f"""
<nav class="navbar navbar-expand-lg site-nav sticky-top">
  <div class="container-fluid px-0">
    <a class="navbar-brand ms-0" href="index.html">
      Mental Health Across the Globe
      <span class="brand-sub">/ Global Analysis</span>
    </a>
    <button class="navbar-toggler border-0 text-white" type="button"
            data-bs-toggle="collapse" data-bs-target="#nav-collapse">
      <i class="bi bi-list fs-5"></i>
    </button>
    <div class="collapse navbar-collapse" id="nav-collapse">
      <ul class="navbar-nav ms-auto">
        {items}
      </ul>
    </div>
  </div>
</nav>"""

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
FOOTER = f"""
<footer class="site-footer mt-5">
  <div class="container">
    <div class="row align-items-center">
      <div class="col-md-6 mb-2 mb-md-0">
        <strong>{SITE_TITLE}</strong>
      </div>
      <div class="col-md-6 text-md-end">
        Data sourced from the Global Burden of Disease Study,
        {num_countries} countries, {year_min} to {year_max}.
      </div>
    </div>
  </div>
</footer>"""

# ---------------------------------------------------------------------------
# Disorder card metadata
# ---------------------------------------------------------------------------
DISORDER_COLORS = {
    "Depressive Disorders": "#4f6cd4",
    "Anxiety Disorders":    "#0d9488",
    "Bipolar Disorders":    "#dc2626",
    "Schizophrenia":        "#7c5c3e",
    "Eating Disorders":     "#be185d",
}
DISORDER_ICONS = {
    "Depressive Disorders": "bi-cloud-drizzle",
    "Anxiety Disorders":    "bi-lightning-charge",
    "Bipolar Disorders":    "bi-arrow-left-right",
    "Schizophrenia":        "bi-person-slash",
    "Eating Disorders":     "bi-heart-pulse",
}

bar_legend_html = "".join(
    f'<div class="legend-item">'
    f'<span class="legend-swatch" style="background:{DISORDER_COLOR_RANGE[i]}"></span>'
    f'{col}'
    f'</div>'
    for i, col in enumerate(disorder_cols)
)

disorder_cards_html = "".join(f"""
    <div class="col-6 col-md-4 col-xl">
      <div class="disorder-card" style="--accent-color:{DISORDER_COLORS[k]}">
        <i class="bi {DISORDER_ICONS[k]} d-icon"></i>
        <div class="d-value">{v:.3f}%</div>
        <div class="d-label">{k}</div>
      </div>
    </div>""" for k, v in disorder_means.items())

# ---------------------------------------------------------------------------
# index.html - Overview & Dataset
# ---------------------------------------------------------------------------
index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{SITE_TITLE}</title>
  <link rel="stylesheet" href="{CDN_BS_CSS}"/>
  <link rel="stylesheet" href="{CDN_DT_CSS}"/>
  <link rel="stylesheet" href="{CDN_BI}"/>
  <style>{SHARED_CSS}</style>
</head>
<body>
{make_nav("index.html")}

<div class="page-header">
  <div class="container">
    <div class="header-inner">
      <div class="header-text">
        <h1>{SITE_TITLE}</h1>
        <p>
          An analysis of the estimated share of the population affected by five major mental
          health disorders across {num_countries} countries from {year_min} to {year_max}.
          Navigate to the analysis pages to explore interactive visualizations.
        </p>
        <div class="d-flex gap-2 flex-wrap mt-3">
          <a href="gdp_mental_health.html" class="btn-primary-site">
            GDP vs. Mental Health
          </a>
          <a href="mental_health.html" class="btn-outline-site">
            Mental Health
          </a>
        </div>
      </div>
{GLOBE_HTML}
    </div>
  </div>
</div>

<div class="container py-4">

  <!-- Key statistics -->
  <div class="section-header">
    <h2>Dataset Summary</h2>
  </div>
  <div class="row g-3 mb-2">
    <div class="col-6 col-md-3">
      <div class="stat-card">
        <div class="stat-value">{num_countries}</div>
        <div class="stat-label">Countries Covered</div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="stat-card">
        <div class="stat-value">{year_min} to {year_max}</div>
        <div class="stat-label">Years Tracked</div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="stat-card">
        <div class="stat-value">{num_records:,}</div>
        <div class="stat-label">Total Records</div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="stat-card">
        <div class="stat-value">{highest_val:.2f}%</div>
        <div class="stat-label">Highest Average<br/>
          <span style="text-transform:none;letter-spacing:0;font-size:.78rem;color:#374151;">{highest_disorder}</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Dataset summary -->
  <div class="section-header mt-4">
    <h2>About this Dataset</h2>
  </div>
  <div class="chart-card mb-4">
    <div class="chart-card-body" style="line-height:1.85;">
      <p style="margin-bottom:0.9rem;">
        This dataset tracks the estimated prevalence of five major mental health disorders:
        Depressive Disorders, Anxiety Disorders,
        Bipolar Disorders, Schizophrenia, and
        Eating Disorders, across {num_countries} countries
        from {year_min} to {year_max}, sourced from the
        <em>Global Burden of Disease (GBD) Study</em>. Prevalence figures represent the
        estimated share of each country&rsquo;s population affected in a given year.
        Across the study period, {highest_disorder} is the most prevalent
        disorder globally (avg.&nbsp;{highest_val:.2f}%), while
        {lowest_disorder} is the least common.
      </p>
      <p style="margin-bottom:0.9rem;">
        The relationship between national wealth and mental health rates is real but nuanced.
        Countries above the global GDP median average a combined disorder prevalence of
        {high_gdp_avg}%, compared to {low_gdp_avg}% for
        lower-income nations, a modest gap of roughly
        {round(high_gdp_avg - low_gdp_avg, 2)} percentage points. This
        reflects a well-documented paradox: wealthier nations tend to report <em>higher</em>
        rates partly because they have greater diagnostic infrastructure and cultural
        acceptance of mental health disclosure, not necessarily because their populations
        are less mentally healthy. The effect is especially pronounced for
        {most_corr_disorder} (Pearson r&nbsp;=&nbsp;{most_corr_r} with
        log&nbsp;GDP), which is strongly associated with high-income, Western countries.
        By contrast, {least_corr_disorder} shows almost no correlation
        with GDP (r&nbsp;=&nbsp;{least_corr_r}), suggesting its prevalence is distributed
        more evenly across income levels worldwide.
      </p>
      <p style="margin-bottom:0.9rem;">
        Geographically, the {highest_region} region carries the highest
        average total burden at {highest_region_val}%, while
        {lowest_region} reports the lowest at
        {lowest_region_val}%. At the country level,
        {top_total_country} records the highest combined prevalence across
        all five disorders at {top_total_val}%, nearly double the global
        average, largely driven by elevated Anxiety and Depressive Disorder rates.
      </p>
    </div>
  </div>

  <!-- Disorder prevalence -->
  <div class="section-header">
    <h2>Global Average Prevalence by Disorder</h2>
  </div>
  <div class="row g-3 mb-2">
{disorder_cards_html}
  </div>

  <!-- Navigation cards -->
  <div class="section-header mt-4">
    <h2>Analysis Pages</h2>
  </div>
  <div class="row g-3 mb-4">
    <div class="col-md-6">
      <a href="gdp_mental_health.html" class="nav-card">
        <h3>GDP vs. Mental Health</h3>
        <p>Explore the relationship between national income and disorder prevalence through
           an interactive scatter plot, regional breakdown, and top-10 country trends.</p>
        <div class="nc-arrow">View Analysis <i class="bi bi-arrow-right"></i></div>
      </a>
    </div>
    <div class="col-md-6">
      <a href="mental_health.html" class="nav-card">
        <h3>Mental Health</h3>
        <p>Examine country-level rankings for Anxiety Disorders prevalence, identifying the
           nations with the highest recorded rates across the study period.</p>
        <div class="nc-arrow">View Analysis <i class="bi bi-arrow-right"></i></div>
      </a>
    </div>
  </div>

  <!-- Dataset explorer -->
  <div class="section-header">
    <h2>Dataset Explorer</h2>
  </div>
  <div class="chart-card mb-4">
    <div class="explorer-toolbar">
      <h3><i class="bi bi-table me-2"></i>{num_records:,} Records, {num_countries} Countries</h3>
      <div class="filter-wrap">
        <label for="country-filter"><i class="bi bi-funnel me-1"></i>Filter by Country</label>
        <select id="country-filter">
          <option value="">All Countries</option>
{country_options_html}
        </select>
        <button class="clear-btn" id="clear-filter">
          <i class="bi bi-x"></i> Clear
        </button>
      </div>
    </div>
    <div class="table-responsive">
      <table id="data-table" class="table table-striped table-hover mb-0" style="width:100%">
        <thead>
          <tr>
            <th>Country</th><th>Year</th>
            <th>Depressive Disorders (%)</th><th>Anxiety Disorders (%)</th>
            <th>Bipolar Disorders (%)</th><th>Schizophrenia (%)</th>
            <th>Eating Disorders (%)</th><th>GDP (M USD)</th>
          </tr>
        </thead>
        <tbody id="table-body"></tbody>
      </table>
    </div>
  </div>

  <div class="section-header">
    <h2>References</h2>
  </div>
  <div class="chart-card mb-4">
    <div class="chart-card-body">
      <h6 class="fw-bold mb-2">Research</h6>
      <ul class="mb-3">
        <li><a href="https://doi.org/10.1016/S2215-0366(14)70277-9" target="_blank" rel="noopener">Whiteford et al. (2014) — Global burden of disease attributable to mental and substance use disorders. <em>The Lancet Psychiatry.</em> https://doi.org/10.1016/S2215-0366(14)70277-9</a></li>
        <li><a href="https://doi.org/10.1186/s12889-023-16871-6" target="_blank" rel="noopener">Tabler et al. (2023) — GDP and mental health outcomes across nations. <em>BMC Public Health.</em> https://doi.org/10.1186/s12889-023-16871-6</a></li>
      </ul>
      <h6 class="fw-bold mb-2">Data</h6>
      <ul class="mb-0">
        <li><a href="https://www.kaggle.com/datasets/imtkaggleteam/mental-health" target="_blank" rel="noopener">Mental Health Dataset — Kaggle (imtkaggleteam). https://www.kaggle.com/datasets/imtkaggleteam/mental-health</a></li>
        <li><a href="https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)" target="_blank" rel="noopener">List of Countries by GDP (Nominal) — Wikipedia. https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)</a></li>
      </ul>
    </div>
  </div>

</div>

{FOOTER}

<script src="{CDN_JQUERY}"></script>
<script src="{CDN_BS_JS}"></script>
<script src="{CDN_DT_JS}"></script>
<script src="{CDN_DT_BS_JS}"></script>
<script src="{CDN_D3}"></script>
<script>
const rows = {table_data};
const tbody = document.getElementById("table-body");
rows.forEach(r => {{
  const tr = document.createElement("tr");
  tr.innerHTML = `
    <td>${{r.Country}}</td><td>${{r.Year}}</td>
    <td class="text-end">${{r["Depressive Disorders"] ?? ""}}</td>
    <td class="text-end">${{r["Anxiety Disorders"] ?? ""}}</td>
    <td class="text-end">${{r["Bipolar Disorders"] ?? ""}}</td>
    <td class="text-end">${{r.Schizophrenia ?? ""}}</td>
    <td class="text-end">${{r["Eating Disorders"] ?? ""}}</td>
    <td class="text-end">${{r.GDP != null ? r.GDP.toLocaleString() : ""}}</td>
  `;
  tbody.appendChild(tr);
}});
const dt = new DataTable("#data-table", {{
  pageLength: 25,
  lengthMenu: [10, 25, 50, 100],
  order: [[0, "asc"], [1, "asc"]],
}});
const countrySelect = document.getElementById("country-filter");
const clearBtn      = document.getElementById("clear-filter");
countrySelect.addEventListener("change", () => {{
  dt.column(0).search(
    countrySelect.value ? "^" + countrySelect.value + "$" : "",
    true, false
  ).draw();
  clearBtn.style.display = countrySelect.value ? "inline-block" : "none";
}});
clearBtn.style.display = "none";
clearBtn.addEventListener("click", () => {{
  countrySelect.value = "";
  dt.column(0).search("").draw();
  clearBtn.style.display = "none";
}});
</script>
{GLOBE_SCRIPT}
</body>
</html>
"""

# ---------------------------------------------------------------------------
# gdp_mental_health.html - GDP vs. Mental Health Analysis
# ---------------------------------------------------------------------------
gdp_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>GDP vs. Mental Health: {SITE_TITLE}</title>
  <link rel="stylesheet" href="{CDN_BS_CSS}"/>
  <link rel="stylesheet" href="{CDN_BI}"/>
  <script src="{CDN_VEGA}"></script>
  <script src="{CDN_VEGALITE}"></script>
  <script src="{CDN_EMBED}"></script>
  <style>{SHARED_CSS}</style>
</head>
<body>
{make_nav("gdp_mental_health.html")}

<div class="page-header">
  <div class="container">
    <div class="header-inner">
      <div class="header-text">
        <h1>GDP vs. Mental Health Disorder Prevalence</h1>
        <p>
          Three complementary views of the relationship between national income and mental health
          outcomes across {num_countries} countries ({year_min} to {year_max}). The scatter
          plot reveals distributional patterns; the regional bar chart compares average disorder
          burden across world regions; and the line chart tracks top-10 country trends over time.
        </p>
      </div>
      {GLOBE_HTML}
    </div>
  </div>
</div>

<div class="container-fluid py-4 px-4">

  <div class="section-header">
    <h2>GDP vs. Disorder Prevalence: Country-Level Scatter</h2>
  </div>
  <div class="chart-card mb-4">
    <div class="chart-card-header">
      <h3>GDP vs. Mental Health Disorder Prevalence</h3>
      <p>
        Each point represents one country&rsquo;s mean disorder prevalence (averaged across
        {year_min} to {year_max}) plotted against its mean GDP on a logarithmic scale.
        Higher-income nations tend to report elevated prevalence, partly attributable to
        greater diagnostic capacity and awareness.
      </p>
    </div>
    <div class="chart-card-body">
      <div id="vis"></div>
    </div>
    <div class="chart-insight">
      <p>
        The scatter plot reveals a modest but consistent positive relationship between national wealth and reported
        mental health disorder prevalence. High-income countries, particularly in Western Europe, North America,
        and Australia, cluster toward the upper right, combining large GDPs with elevated disorder rates.
        This pattern is most striking for Eating Disorders, which are nearly exclusive to wealthy nations, likely
        because they depend heavily on cultural context, specialist care, and formal diagnosis.
        By contrast, lower-income countries in Sub-Saharan Africa and South Asia tend to report lower prevalence,
        but this almost certainly reflects gaps in healthcare infrastructure and under-diagnosis rather than genuinely
        better mental health outcomes. The logarithmic GDP scale helps spread countries evenly and makes clear
        that the relationship is not linear: gains in prevalence reporting accelerate once countries cross a
        certain income threshold. Overall, this chart cautions against reading higher reported prevalence as
        a sign of worse mental health: it is equally a signal of a country's capacity to identify and measure it.
      </p>
    </div>
  </div>

  <div class="section-header">
    <h2>Average Prevalence by World Region</h2>
  </div>
  <div class="chart-card mb-4">
    <div class="chart-card-header">
      <h3>Mean Disorder Prevalence &amp; Average GDP by Region (All Years)</h3>
      <p>
        Country-level averages aggregated by world region. Select a disorder to compare
        regional prevalence baselines (left). Average GDP per region (right) is static
        and does not change with disorder selection.
      </p>
    </div>
    <div class="chart-card-body">
      <div class="mb-3">
        <label for="region-disorder-select" class="fw-semibold small me-2">Disorder:</label>
        <select id="region-disorder-select" class="form-select form-select-sm d-inline-block" style="width:auto;">
          {''.join(f'<option{"  selected" if d == "Depressive Disorders" else ""}>{d}</option>' for d in disorder_cols)}
        </select>
      </div>
      <div style="display:flex; gap:1.5rem;">
        <div style="flex:1; min-width:0;"><div id="vis-region"></div></div>
        <div style="flex:1; min-width:0;"><div id="vis-region-gdp"></div></div>
      </div>
    </div>
    <div class="chart-insight">
      <p>
        Regional averages expose sharp geographic disparities in how mental health burden is distributed globally.
        The Middle East &amp; North Africa consistently records the highest average prevalence, particularly for
        Anxiety Disorders, a pattern that likely reflects the compounding effects of prolonged conflict,
        displacement, and socioeconomic instability across the region.
        Europe &amp; Central Asia and the Americas also rank near the top for most disorder types, driven by strong
        diagnostic infrastructure and greater cultural openness to mental health reporting.
        East Asia &amp; Pacific records the lowest overall averages, a result shaped partly by genuine differences in
        lifestyle and community support structures, but also by cultural norms around mental health disclosure and
        historically lower investment in psychiatric services.
        Sub-Saharan Africa similarly shows low averages, though the data here is sparse: many countries in the
        region lack the clinical infrastructure to systematically diagnose and record mental health conditions.
        Switching between disorders reveals that the regional rankings shift considerably: Eating Disorders are
        almost entirely absent outside high-income regions, while Schizophrenia and Bipolar Disorders are
        distributed more evenly across the world.
      </p>
    </div>
  </div>

  <div class="section-header">
    <h2>Top 10 Countries: Disorder Prevalence Over Time</h2>
  </div>
  <div class="chart-card mb-5">
    <div class="chart-card-header">
      <h3>Mental Health Disorders &mdash; Top 10 Countries by Prevalence Over Time</h3>
      <p>
        Tracks disorder prevalence from {year_min} to {year_max} for the ten countries with the
        highest average rates. Use the dropdown to switch between disorder types.
      </p>
    </div>
    <div class="chart-card-body">
      <div id="vis-top10"></div>
    </div>
    <div class="chart-insight">
      <p>
        Across all five disorders, the top-ranked countries remain largely consistent over
        the 30-year period, suggesting that national burden is shaped by structural and
        cultural factors rather than short-term fluctuations. Portugal and Brazil consistently
        lead for Depressive and Anxiety Disorders, while Eating Disorder prevalence is
        concentrated almost entirely in high-income, Western nations throughout the entire
        timespan. The dropdown selector reveals that different disorders have distinct
        geographic footprints: Schizophrenia and Bipolar Disorders show narrower cross-country
        variation compared to Anxiety and Depressive Disorders.
      </p>
    </div>
  </div>

  <div class="section-header">
    <h2>All Disorders Over Time by Country</h2>
  </div>
  <div class="chart-card mb-5">
    <div class="chart-card-header">
      <h3>Disorder Prevalence Over Time &mdash; Country View</h3>
      <p>
        Select a country to see how all five disorder types have trended from
        {year_min} to {year_max}. Average GDP is shown in the top-right corner of the chart.
      </p>
    </div>
    <div class="chart-card-body">
      <div id="vis-country-time"></div>
    </div>
  </div>

</div>

{FOOTER}

<script src="{CDN_BS_JS}"></script>
<script>
  const embedOpts = {{ mode: "vega-lite", renderer: "svg", actions: false }};
  vegaEmbed("#vis",            {chart_spec},        embedOpts).catch(console.error);
  vegaEmbed("#vis-region", {region_avg_spec}, embedOpts).then(function(r) {{
    document.getElementById("region-disorder-select").addEventListener("change", function(e) {{
      r.view.signal("RegionDisorder", e.target.value).run();
    }});
  }});
  vegaEmbed("#vis-region-gdp", {region_gdp_spec}, embedOpts).catch(console.error);
  vegaEmbed("#vis-top10",      {top10_time_spec},   embedOpts).catch(console.error);
  vegaEmbed("#vis-country-time", {country_time_spec}, embedOpts).catch(console.error);
</script>
<script src="{CDN_D3}"></script>
{GLOBE_SCRIPT}
</body>
</html>
"""

# ---------------------------------------------------------------------------
# mental_health.html - Mental Health Overview
# ---------------------------------------------------------------------------
_disorder_color_map = json.dumps(dict(zip(disorder_cols, DISORDER_COLOR_RANGE)))
_disorder_list_js   = json.dumps(disorder_cols)

mh_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Mental Health Overview: {SITE_TITLE}</title>
  <link rel="stylesheet" href="{CDN_BS_CSS}"/>
  <link rel="stylesheet" href="{CDN_BI}"/>
  <script src="{CDN_D3}"></script>
  <script src="{CDN_VEGA}"></script>
  <script src="{CDN_VEGALITE}"></script>
  <script src="{CDN_EMBED}"></script>
  <style>{SHARED_CSS}</style>
</head>
<body>
{make_nav("mental_health.html")}

<div class="page-header">
  <div class="container">
    <div class="header-inner">
      <div class="header-text">
        <h1>Mental Health Overview</h1>
        <p>
          Country-level rankings across all five mental health disorders, independent of economic
          indicators. Select any disorder to explore the ten countries with the highest recorded
          peak prevalence. Below, compare all disorders side-by-side across GDP tiers.
        </p>
      </div>
      {GLOBE_HTML}
    </div>
  </div>
</div>

<div class="container-fluid py-4 px-4">

  <!-- ── Section 1: Interactive D3 Top-10 Rankings ── -->
  <div class="section-header">
    <h2>Top 10 Country Rankings by Disorder</h2>
  </div>
  <div class="chart-card mb-4">
    <div class="chart-card-header">
      <h3>Ten Countries with the Highest Peak Disorder Prevalence</h3>
      <p>
        Select a disorder below. Rankings are based on each country&rsquo;s maximum recorded
        prevalence across {year_min} to {year_max}.
      </p>
    </div>
    <div class="dis-pills">
      <span class="dis-label">Disorder:</span>
      <div id="disorder-pills" style="display:contents;"></div>
    </div>
    <div class="chart-card-body">
      <div id="d3-bar-chart" style="width:100%;"></div>
    </div>
    <div class="chart-insight">
      <p>
        Ranking countries by their peak disorder prevalence reveals that no single region dominates across
        all five conditions, each with very different geographic footprints.
        Portugal consistently appears near the top across multiple disorders, holding the highest overall
        combined mental health prevalence of any country in the dataset at {top_total_val}% of its population,
        a figure that reflects both genuine burden and a well-developed mental health reporting system.
        Switching to Eating Disorders shifts the top-10 almost entirely to high-income Western nations:
        the United States, Australia, New Zealand, and several Northern European countries, reinforcing how
        tightly this condition is linked to affluent, image-conscious cultural environments.
        Anxiety Disorders draw from a broader mix of regions, with countries in Latin America, the Middle East,
        and Southern Europe featuring prominently alongside wealthier nations.
        Schizophrenia and Bipolar Disorders show the most geographically diverse top-10 lists, with countries
        from every income bracket represented, consistent with their status as conditions driven primarily
        by biology rather than socioeconomic environment.
        Exploring each disorder individually paints a nuanced picture: mental health burden is not simply
        a function of wealth, but rather the product of culture, history, healthcare access, and
        the willingness of a society to name and measure its mental health challenges.
      </p>
    </div>
  </div>


  <!-- ── Section 2: Choropleth world map ── -->
  <div class="section-header">
    <h2>Global Distribution of Mental Health Disorder Prevalence (2019)</h2>
  </div>
  <div class="chart-card mb-5">
    <div class="chart-card-header">
      <h3>Mental Health Disorder Prevalence by Country (2019)</h3>
      <p>
        Prevalence as a percentage of population in 2019. Use the dropdown to switch
        between All Disorders (combined) and individual disorder types.
        Grey countries have no data available. Hover a country for details.
      </p>
    </div>
    <div class="chart-card-body">
      <div id="vis-geo"></div>
    </div>
    <div class="chart-insight">
      <p>
        The choropleth map makes the global distribution of mental health burden immediately visible,
        with the deepest reds concentrated across Western Europe, North America, Australia, and parts of
        Latin America, all regions with both high income levels and strong mental health reporting systems.
        Portugal, the United States, and Australia are among the darkest countries on the map, reflecting
        their status as nations with both high genuine prevalence and mature diagnostic infrastructure.
        A broad East-West divide is apparent: wealthy Western nations carry the highest reported total burden,
        while large stretches of Africa, Central Asia, and parts of the Middle East appear in lighter shades.
        Grey countries indicate missing data, a pattern that is itself revealing, as the absence of
        measurement is concentrated in lower-income regions where mental health surveillance systems are
        underdeveloped or entirely absent.
        This data gap means the map almost certainly understates the true global burden: many of the
        lighter-colored or grey nations likely have significant undiagnosed mental health conditions that
        simply go uncounted.
        Together, the map tells two stories at once: the geographic distribution of reported mental health
        prevalence, and the uneven global capacity to detect and record it.
      </p>
    </div>
  </div>

</div>

{FOOTER}

<script src="{CDN_BS_JS}"></script>
<script>
  const embedOpts = {{ mode: "vega-lite", renderer: "svg", actions: false }};
  vegaEmbed("#vis-geo", {geo_spec}, embedOpts).catch(console.error);
</script>
<script>
(function () {{
  const mhData   = {mh_top10_json};
  const disorders = {_disorder_list_js};
  const colorMap  = {_disorder_color_map};

  let active = disorders[0];

  // ── Pill buttons ──
  const pillWrap = document.getElementById("disorder-pills");
  disorders.forEach(d => {{
    const btn = document.createElement("button");
    btn.className = "dis-pill" + (d === active ? " active" : "");
    btn.dataset.disorder = d;
    btn.textContent = d;
    btn.addEventListener("click", function () {{
      document.querySelectorAll(".dis-pill").forEach(b => b.classList.remove("active"));
      this.classList.add("active");
      active = this.dataset.disorder;
      update(active);
    }});
    pillWrap.appendChild(btn);
  }});

  // ── SVG setup ──
  const margin = {{ top: 10, right: 72, bottom: 40, left: 168 }};
  const wrap   = document.getElementById("d3-bar-chart");
  const totalW = Math.max(wrap.offsetWidth || 700, 400);
  const innerW = totalW - margin.left - margin.right;
  const innerH = 360 - margin.top - margin.bottom;

  const svg = d3.select("#d3-bar-chart")
    .append("svg")
    .attr("width", "100%")
    .attr("viewBox", `0 0 ${{totalW}} ${{innerH + margin.top + margin.bottom}}`)
    .append("g")
    .attr("transform", `translate(${{margin.left}},${{margin.top}})`);

  const x = d3.scaleLinear().range([0, innerW]);
  const y = d3.scaleBand().range([0, innerH]).padding(0.28);

  const xAxisG = svg.append("g").attr("transform", `translate(0,${{innerH}})`);
  const yAxisG = svg.append("g");
  const gridG  = svg.insert("g", ":first-child").attr("class", "grid-lines");

  // ── Tooltip ──
  const tip = d3.select("body").append("div").attr("class", "d3-tip").style("opacity", 0);

  function styleAxes() {{
    xAxisG.selectAll("text").attr("fill", "#6b7280").attr("font-size", "11px");
    xAxisG.selectAll(".domain, .tick line").attr("stroke", "#dee2e6");
    yAxisG.selectAll("text").attr("fill", "#374151").attr("font-size", "12px");
    yAxisG.selectAll(".domain, .tick line").attr("stroke", "#dee2e6");
  }}

  function update(disorder) {{
    const data  = mhData[disorder];
    const color = colorMap[disorder];

    x.domain([0, d3.max(data, d => d.value) * 1.12]);
    y.domain(data.map(d => d.Country));

    xAxisG.transition().duration(500)
      .call(d3.axisBottom(x).ticks(5).tickFormat(v => v.toFixed(1) + "%"));
    yAxisG.transition().duration(500)
      .call(d3.axisLeft(y));
    setTimeout(styleAxes, 520);

    // Grid lines
    gridG.selectAll("line.vgrid").remove();
    gridG.selectAll("line.vgrid")
      .data(x.ticks(5))
      .join("line")
      .attr("class", "vgrid")
      .attr("x1", d => x(d)).attr("x2", d => x(d))
      .attr("y1", 0).attr("y2", innerH)
      .attr("stroke", "#e9ecef").attr("stroke-width", 1);

    // ── Bars ──
    svg.selectAll("rect.bar")
      .data(data, d => d.Country)
      .join(
        enter => enter.append("rect").attr("class", "bar")
          .attr("y", d => y(d.Country))
          .attr("height", y.bandwidth())
          .attr("x", 0).attr("width", 0)
          .attr("rx", 3).attr("fill", color)
          .call(sel => sel.transition().duration(600).attr("width", d => x(d.value))),
        upd => upd.call(sel => sel.transition().duration(600)
          .attr("y",      d => y(d.Country))
          .attr("height", y.bandwidth())
          .attr("width",  d => x(d.value))
          .attr("fill",   color)),
        exit => exit.call(sel => sel.transition().duration(300).attr("width", 0).remove())
      )
      .on("mouseover", (event, d) => {{
        tip.transition().duration(120).style("opacity", 1);
        tip.html(`<strong>${{d.Country}}</strong><br/>${{d.value.toFixed(3)}}% of population`)
           .style("left",  (event.pageX + 14) + "px")
           .style("top",   (event.pageY - 36) + "px");
      }})
      .on("mousemove", event => {{
        tip.style("left", (event.pageX + 14) + "px")
           .style("top",  (event.pageY - 36) + "px");
      }})
      .on("mouseout", () => tip.transition().duration(200).style("opacity", 0));

    // ── Value labels ──
    svg.selectAll("text.bar-lbl")
      .data(data, d => d.Country)
      .join(
        enter => enter.append("text").attr("class", "bar-lbl")
          .attr("x", d => x(d.value) + 5)
          .attr("y", d => y(d.Country) + y.bandwidth() / 2 + 4)
          .attr("font-size", "11px").attr("fill", "#6b7280")
          .text(d => d.value.toFixed(2) + "%")
          .style("opacity", 0)
          .call(sel => sel.transition().duration(600).style("opacity", 1)),
        upd => upd.call(sel => sel.transition().duration(600)
          .attr("x", d => x(d.value) + 5)
          .attr("y", d => y(d.Country) + y.bandwidth() / 2 + 4)
          .text(d => d.value.toFixed(2) + "%")),
        exit => exit.call(sel => sel.transition().duration(300).style("opacity", 0).remove())
      );
  }}

  update(active);
  styleAxes();
}})();

</script>
{GLOBE_SCRIPT}
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Also write visualization.html as an alias to gdp_mental_health.html
# (keeps backwards-compatibility if any bookmarks exist)
# ---------------------------------------------------------------------------
vis_html = gdp_html

# ---------------------------------------------------------------------------
# key_findings.html - Key Findings & Conclusions
# ---------------------------------------------------------------------------
kf_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Key Findings &amp; Conclusions: {SITE_TITLE}</title>
  <link rel="stylesheet" href="{CDN_BS_CSS}"/>
  <link rel="stylesheet" href="{CDN_BI}"/>
  <style>{SHARED_CSS}
    .finding-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-left: 4px solid var(--blue-light);
      border-radius: 8px;
      padding: 1.25rem 1.5rem;
      margin-bottom: 1.25rem;
    }}
    .finding-card h4 {{
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text-head);
      margin: 0 0 0.5rem;
    }}
    .finding-card p {{
      font-size: 0.9rem;
      color: var(--text-body);
      line-height: 1.75;
      margin: 0;
    }}
    .finding-number {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: var(--navy);
      color: #fff;
      font-size: 0.78rem;
      font-weight: 700;
      margin-right: 0.6rem;
      flex-shrink: 0;
    }}
    .finding-title-row {{
      display: flex;
      align-items: center;
      margin-bottom: 0.5rem;
    }}
    .conclusion-box {{
      background: var(--navy);
      color: #fff;
      border-radius: 8px;
      padding: 2rem;
      margin-bottom: 2rem;
    }}
    .conclusion-box h3 {{
      font-size: 1.05rem;
      font-weight: 700;
      color: #fff;
      margin-bottom: 1rem;
    }}
    .conclusion-box p {{
      font-size: 0.92rem;
      color: rgba(255,255,255,0.82);
      line-height: 1.8;
      margin-bottom: 0;
    }}
  </style>
</head>
<body>
{make_nav("key_findings.html")}

<div class="page-header">
  <div class="container">
    <div class="eyebrow">Summary</div>
    <h1>Key Findings &amp; Conclusions</h1>
    <p>
      A synthesis of the major patterns and takeaways drawn from analyzing mental health
      disorder prevalence across {num_countries} countries from {year_min} to {year_max}.
    </p>
  </div>
</div>

<div class="container py-4">

  <div class="section-header">
    <h2>Key Findings</h2>
  </div>

  <div class="finding-card">
    <div class="finding-title-row">
      <span class="finding-number">1</span>
      <h4>Anxiety Disorders are the most prevalent condition globally</h4>
    </div>
    <p>
      Across all {num_countries} countries and the full {year_min} to {year_max} period,
      Anxiety Disorders carry the highest average prevalence at {highest_val:.2f}% of the
      population. Eating Disorders remain the least common condition in every region.
      These rankings are stable over time, suggesting deeply structural drivers rather
      than fluctuating trends.
    </p>
  </div>

  <div class="finding-card">
    <div class="finding-title-row">
      <span class="finding-number">2</span>
      <h4>Wealthier nations report higher prevalence, but not necessarily worse outcomes</h4>
    </div>
    <p>
      Countries above the global GDP median average a combined disorder prevalence of
      {high_gdp_avg}%, compared to {low_gdp_avg}% for lower-income nations, a gap of
      just {round(high_gdp_avg - low_gdp_avg, 2)} percentage points. This modest
      difference reflects a well-documented paradox: richer countries have stronger
      diagnostic infrastructure, greater cultural openness to mental health disclosure,
      and more specialists per capita. Higher reported rates are partly a signal of better
      measurement, not necessarily greater suffering.
    </p>
  </div>

  <div class="finding-card">
    <div class="finding-title-row">
      <span class="finding-number">3</span>
      <h4>Eating Disorders are almost exclusively a high-income phenomenon</h4>
    </div>
    <p>
      Of all five disorders, {most_corr_disorder} show the strongest correlation with
      national wealth (Pearson r&nbsp;=&nbsp;{most_corr_r} with log GDP). They are nearly
      absent from low-income countries and concentrated in Western, high-income nations.
      This pattern reflects both genuine cultural risk factors and the fact that Eating
      Disorders require specialist diagnosis that is rarely available in lower-resource settings.
    </p>
  </div>

  <div class="finding-card">
    <div class="finding-title-row">
      <span class="finding-number">4</span>
      <h4>Depressive Disorders show almost no relationship with GDP</h4>
    </div>
    <p>
      With a Pearson correlation of just r&nbsp;=&nbsp;{least_corr_r} with log GDP,
      {least_corr_disorder} are distributed more evenly across income levels than any other
      condition. This suggests that depression is a truly global burden, influenced by
      factors including grief, trauma, social isolation, and chronic illness, that are not
      meaningfully tied to a country's economic development.
    </p>
  </div>

  <div class="finding-card">
    <div class="finding-title-row">
      <span class="finding-number">5</span>
      <h4>The Middle East &amp; North Africa carries the highest regional burden</h4>
    </div>
    <p>
      The Middle East &amp; North Africa region records the highest average combined
      disorder prevalence at {highest_region_val}%, particularly for Anxiety Disorders.
      This likely reflects the compounding effects of prolonged conflict, displacement,
      and socioeconomic instability across the region. By contrast, {lowest_region} reports
      the lowest regional average at {lowest_region_val}%.
    </p>
  </div>

  <div class="finding-card">
    <div class="finding-title-row">
      <span class="finding-number">6</span>
      <h4>{top_total_country} records the highest country-level prevalence of any nation</h4>
    </div>
    <p>
      {top_total_country} consistently ranks first in combined disorder prevalence at
      {top_total_val}%, nearly double the global average, driven primarily by elevated
      Anxiety and Depressive Disorder rates. This stands out even among high-income nations
      and may reflect both genuine burden and a strong tradition of mental health research
      and clinical reporting.
    </p>
  </div>

  <div class="finding-card">
    <div class="finding-title-row">
      <span class="finding-number">7</span>
      <h4>Country rankings are stable over three decades</h4>
    </div>
    <p>
      The top-ranked countries for each disorder have remained largely consistent from
      {year_min} to {year_max}, as shown in the time-series analysis on the GDP vs. Mental
      Health page. This persistence suggests that national mental health burden is shaped by
      long-term structural, cultural, and healthcare-system factors rather than year-to-year
      events, and that meaningful improvement requires sustained, systemic intervention.
    </p>
  </div>

  <div class="section-header mt-4">
    <h2>Conclusion</h2>
  </div>

  <div class="conclusion-box">
    <h3>What the data tells us, and what it doesn&rsquo;t</h3>
    <p>
      One key thing we learned from this project and our dataset is that measurement
      capacity (the ability to detect, diagnose, and report mental illness) heavily
      influences the reported rates of mental illnesses, arguably more than the actual
      rates themselves. The relationship between GDP and mental illness is real, but it
      is quite small, only {round(high_gdp_avg - low_gdp_avg, 2)}%, because wealthier
      countries detect more, so they report more. Low-income countries almost certainly
      have the same, if not higher rates that are just not captured due to lower measurement
      capacity. Within the picture the data has painted, Eating Disorders are uniquely
      Western, with higher ties to both wealth and Western countries. With an r-value of
      {most_corr_r} (the strongest correlation with income of any disorder we measured),
      the prevalence of Eating Disorders in Western countries shows not only the cultural
      risk inherent to the West, but also their stronger ability to detect and measure these
      illnesses. Depression, by contrast, is universal. With an r-value of {least_corr_r}
      (in correlation to GDP), depression is roughly the same everywhere, a byproduct of
      grief and isolation that can be found anywhere on the globe. The Middle East and
      North Africa consistently rank highest in Anxiety Disorders, echoing centuries of war
      and turmoil that still leave their scars today. However, what we think is the largest,
      most important takeaway is that country rankings barely changed over these 30 years,
      meaning the structural and social influences that cause these disorders are very deeply
      entrenched in our societies, and to change this would require sustained commitment to
      change on a scale currently unheard of.
    </p>
  </div>

</div>

{FOOTER}

<script src="{CDN_BS_JS}"></script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Write files & open
# ---------------------------------------------------------------------------
for fname, content in [
    ("index.html",            index_html),
    ("gdp_mental_health.html",gdp_html),
    ("mental_health.html",    mh_html),
    ("visualization.html",    vis_html),
    ("key_findings.html",     kf_html),
]:
    with open(os.path.join(BASE, fname), "w", encoding="utf-8") as f:
        f.write(content)

index_path = os.path.join(BASE, "index.html")
print("Generated index.html, gdp_mental_health.html, mental_health.html, visualization.html")
webbrowser.open(f"file:///{index_path}")
