import os, json, webbrowser
from visualization import (
    df_no_world, disorder_cols, REGION_COLORS,
    chart_spec, BASE,
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

# ---------------------------------------------------------------------------
# Table data (rounded for browser payload size)
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

SITE_TITLE = "Mental Health Across the Globe"

# ---------------------------------------------------------------------------
# Shared nav & footer
# ---------------------------------------------------------------------------
NAV = """
<nav class="navbar navbar-expand-lg navbar-dark sticky-top site-nav px-4 py-2">
  <a class="navbar-brand fw-bold d-flex align-items-center gap-2" href="index.html">
    <i class="bi bi-globe2 fs-5"></i> Mental Health Across the Globe
  </a>
  <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#nav">
    <span class="navbar-toggler-icon"></span>
  </button>
  <div class="collapse navbar-collapse" id="nav">
    <ul class="navbar-nav ms-auto gap-1">
      <li class="nav-item">
        <a class="nav-link nav-pill" href="index.html">
          <i class="bi bi-house-fill me-1"></i>Home
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link nav-pill" href="visualization.html">
          <i class="bi bi-bar-chart-fill me-1"></i>Visualization
        </a>
      </li>
    </ul>
  </div>
</nav>
"""

FOOTER = f"""
<footer class="site-footer mt-5 py-4">
  <div class="container text-center">
    <p class="mb-1 fw-semibold">{SITE_TITLE}</p>
    <p class="mb-0 small opacity-75">
      Data sourced from the Global Burden of Disease Study &mdash;
      covering {num_countries} countries, {year_min}&ndash;{year_max}.
    </p>
  </div>
</footer>
"""

# ---------------------------------------------------------------------------
# Disorder card styling metadata
# ---------------------------------------------------------------------------
DISORDER_COLORS = {
    "Depressive Disorders": "#5c6bc0",
    "Anxiety Disorders":    "#26a69a",
    "Bipolar Disorders":    "#ef5350",
    "Schizophrenia":        "#8d6e63",
    "Eating Disorders":     "#ec407a",
}

DISORDER_ICONS = {
    "Depressive Disorders": "bi-cloud-drizzle-fill",
    "Anxiety Disorders":    "bi-lightning-charge-fill",
    "Bipolar Disorders":    "bi-arrow-left-right",
    "Schizophrenia":        "bi-person-fill-slash",
    "Eating Disorders":     "bi-heart-pulse-fill",
}

disorder_cards_html = "".join(f"""
    <div class="col-6 col-md-4 col-xl">
      <div class="disorder-card" style="--accent:{DISORDER_COLORS[k]}">
        <i class="bi {DISORDER_ICONS[k]} disorder-icon"></i>
        <div class="disorder-value">{v:.3f}%</div>
        <div class="disorder-label">{k}</div>
      </div>
    </div>""" for k, v in disorder_means.items())

# ---------------------------------------------------------------------------
# index.html
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
  <style>
    :root {{
      --primary: #1e2a6e;
      --primary-light: #3d4fb5;
      --accent: #7c83e8;
    }}
    * {{ box-sizing: border-box; }}
    body {{ background: #f0f2f8; font-family: system-ui, sans-serif; margin: 0; }}

    /* ── Navbar ── */
    .site-nav {{
      background: linear-gradient(90deg, var(--primary) 0%, #2d3a8c 100%);
      box-shadow: 0 2px 12px rgba(0,0,0,.3);
    }}
    .nav-pill {{ border-radius: 20px; padding: .35rem .9rem !important; transition: background .2s; }}
    .nav-pill:hover {{ background: rgba(255,255,255,.15) !important; }}

    /* ── Hero ── */
    .hero {{
      background: linear-gradient(135deg, #111838 0%, #1e2a6e 50%, #2e3fa3 100%);
      color: #fff;
      padding: 5rem 2rem 7rem;
      position: relative;
      overflow: hidden;
    }}
    .hero::before {{
      content: "";
      position: absolute; inset: 0;
      background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Ccircle cx='30' cy='30' r='4'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    }}
    .hero-badge {{
      display: inline-block;
      background: rgba(255,255,255,.12);
      border: 1px solid rgba(255,255,255,.25);
      border-radius: 30px;
      padding: .3rem 1rem;
      font-size: .8rem;
      letter-spacing: .05em;
      text-transform: uppercase;
      margin-bottom: 1.2rem;
    }}
    .hero h1 {{ font-size: clamp(1.9rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; }}
    .hero p   {{ font-size: 1.1rem; opacity: .85; max-width: 680px; line-height: 1.7; }}
    .hero-cta {{
      display: inline-flex; align-items: center; gap: .5rem;
      background: var(--accent); color: #fff;
      padding: .7rem 1.6rem; border-radius: 30px;
      font-weight: 600; text-decoration: none;
      box-shadow: 0 4px 18px rgba(124,131,232,.5);
      transition: transform .2s, box-shadow .2s;
    }}
    .hero-cta:hover {{ transform: translateY(-2px); box-shadow: 0 8px 24px rgba(124,131,232,.6); color:#fff; }}
    .wave {{ display:block; width:100%; margin-top:-2px; }}

    /* ── Stat cards ── */
    .stat-card {{
      background: #fff;
      border-radius: 14px;
      padding: 1.5rem 1.2rem;
      box-shadow: 0 2px 14px rgba(30,42,110,.08);
      text-align: center;
      transition: transform .2s, box-shadow .2s;
    }}
    .stat-card:hover {{ transform: translateY(-4px); box-shadow: 0 8px 28px rgba(30,42,110,.14); }}
    .stat-card .stat-icon {{ font-size: 1.7rem; margin-bottom: .4rem; color: var(--primary-light); }}
    .stat-card .value {{ font-size: 1.9rem; font-weight: 800; color: var(--primary); }}
    .stat-card .label {{ font-size: .82rem; color: #6c757d; margin-top: .2rem; }}

    /* ── Disorder cards ── */
    .disorder-card {{
      background: #fff;
      border-radius: 14px;
      padding: 1.4rem 1rem;
      box-shadow: 0 2px 10px rgba(0,0,0,.07);
      text-align: center;
      border-top: 4px solid var(--accent);
      transition: transform .2s, box-shadow .2s;
    }}
    .disorder-card:hover {{ transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,.12); }}
    .disorder-icon {{ font-size: 1.8rem; color: var(--accent); margin-bottom: .5rem; display: block; }}
    .disorder-value {{ font-size: 1.5rem; font-weight: 800; color: var(--primary); }}
    .disorder-label {{ font-size: .78rem; color: #6c757d; margin-top: .3rem; }}

    /* ── Section title ── */
    .section-title {{
      font-size: 1.25rem; font-weight: 700;
      color: var(--primary);
      display: flex; align-items: center; gap: .6rem;
      margin: 3rem 0 1.2rem;
    }}
    .section-title::after {{
      content: ""; flex: 1;
      height: 2px;
      background: linear-gradient(to right, var(--primary-light), transparent);
      border-radius: 2px;
    }}

    /* ── Explorer card ── */
    .explorer-card {{
      border-radius: 16px;
      border: 2px solid #c7cdf0;
      box-shadow: 0 4px 24px rgba(30,42,110,.1);
      overflow: hidden;
    }}
    .explorer-header {{
      background: linear-gradient(90deg, var(--primary) 0%, var(--primary-light) 100%);
      padding: 1rem 1.4rem;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: .8rem;
    }}
    .explorer-header h2 {{
      color: #fff;
      font-size: 1rem;
      font-weight: 700;
      margin: 0;
      display: flex;
      align-items: center;
      gap: .45rem;
    }}
    .country-select-wrap {{
      display: flex;
      align-items: center;
      gap: .5rem;
      margin-left: auto;
    }}
    .country-select-wrap label {{
      color: rgba(255,255,255,.85);
      font-size: .82rem;
      font-weight: 600;
      white-space: nowrap;
    }}
    .country-select-wrap select {{
      border: 1.5px solid rgba(255,255,255,.35);
      border-radius: 8px;
      padding: .35rem 2rem .35rem .7rem;
      font-size: .83rem;
      color: var(--primary);
      background: #fff;
      cursor: pointer;
      min-width: 180px;
      max-width: 240px;
      appearance: none;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%231e2a6e' viewBox='0 0 16 16'%3E%3Cpath d='M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right .6rem center;
    }}
    .country-select-wrap select:focus {{ outline: none; border-color: var(--accent); }}
    .clear-btn {{
      background: rgba(255,255,255,.15);
      border: 1px solid rgba(255,255,255,.3);
      color: #fff;
      border-radius: 8px;
      padding: .35rem .75rem;
      font-size: .8rem;
      cursor: pointer;
      transition: background .2s;
      white-space: nowrap;
    }}
    .clear-btn:hover {{ background: rgba(255,255,255,.28); }}

    /* ── Table ── */
    table.dataTable thead th {{
      background: var(--primary);
      color: #fff;
      font-weight: 600;
      border-color: #2d3a8c !important;
    }}
    table.dataTable tbody tr:hover {{ background: #eef0fb !important; }}

    /* ── Footer ── */
    .site-footer {{
      background: linear-gradient(90deg, var(--primary) 0%, #2d3a8c 100%);
      color: rgba(255,255,255,.7);
      font-size: .85rem;
    }}
    .site-footer .fw-semibold {{ color: #fff; }}
  </style>
</head>
<body>
{NAV}

<div class="hero">
  <div class="container position-relative">
    <div class="hero-badge"><i class="bi bi-globe-americas me-1"></i>Global Dataset</div>
    <h1>{SITE_TITLE}</h1>
    <p class="mt-3">
      Tracking the estimated share of the population affected by five major mental health
      disorders across <strong style="color:#a5b4fc">{num_countries} countries</strong> from
      <strong style="color:#a5b4fc">{year_min}</strong> to
      <strong style="color:#a5b4fc">{year_max}</strong>. Explore the raw data below or
      dive into the interactive chart.
    </p>
    <a href="visualization.html" class="hero-cta mt-2">
      <i class="bi bi-bar-chart-fill"></i> Explore the Visualization
    </a>
  </div>
</div>
<svg class="wave" viewBox="0 0 1440 60" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none" style="background:#111838">
  <path d="M0,30 C360,70 1080,-10 1440,30 L1440,60 L0,60 Z" fill="#f0f2f8"/>
</svg>

<div class="container py-2">

  <!-- Top stat cards -->
  <div class="row g-3 mb-2">
    <div class="col-6 col-md-3">
      <div class="stat-card">
        <div class="stat-icon"><i class="bi bi-globe2"></i></div>
        <div class="value">{num_countries}</div>
        <div class="label">Countries Covered</div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="stat-card">
        <div class="stat-icon"><i class="bi bi-calendar3"></i></div>
        <div class="value">{year_min}–{year_max}</div>
        <div class="label">Years Tracked</div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="stat-card">
        <div class="stat-icon"><i class="bi bi-table"></i></div>
        <div class="value">{num_records:,}</div>
        <div class="label">Total Records</div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="stat-card">
        <div class="stat-icon"><i class="bi bi-graph-up-arrow"></i></div>
        <div class="value">{highest_val:.2f}%</div>
        <div class="label">Highest Avg<br/><small class="text-muted">{highest_disorder}</small></div>
      </div>
    </div>
  </div>

  <!-- Disorder prevalence cards -->
  <div class="section-title">
    <i class="bi bi-heart-pulse-fill text-danger me-1"></i>Global Average Prevalence by Disorder
  </div>
  <div class="row g-3 mb-2">
{disorder_cards_html}
  </div>

  <!-- Data table -->
  <div class="section-title">
    <i class="bi bi-search text-primary me-1"></i>Dataset Explorer
  </div>
  <div class="explorer-card mb-5">
    <!-- Header bar with country filter -->
    <div class="explorer-header">
      <h2><i class="bi bi-table"></i> {num_records:,} Records &mdash; {num_countries} Countries</h2>
      <div class="country-select-wrap">
        <label for="country-filter"><i class="bi bi-funnel-fill"></i> Filter by Country:</label>
        <select id="country-filter">
          <option value="">All Countries</option>
{country_options_html}
        </select>
        <button class="clear-btn" id="clear-filter">
          <i class="bi bi-x-lg"></i> Clear
        </button>
      </div>
    </div>
    <!-- Table -->
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

</div>

{FOOTER}

<script src="{CDN_JQUERY}"></script>
<script src="{CDN_BS_JS}"></script>
<script src="{CDN_DT_JS}"></script>
<script src="{CDN_DT_BS_JS}"></script>
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

// Country filter
const countrySelect = document.getElementById("country-filter");
const clearBtn      = document.getElementById("clear-filter");

countrySelect.addEventListener("change", () => {{
  // Exact-match search on column 0 (Country)
  dt.column(0).search(
    countrySelect.value ? "^" + countrySelect.value + "$" : "",
    true,   // regex
    false   // smart
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
</body>
</html>
"""

# ---------------------------------------------------------------------------
# visualization.html
# ---------------------------------------------------------------------------
vis_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Visualization — {SITE_TITLE}</title>
  <link rel="stylesheet" href="{CDN_BS_CSS}"/>
  <link rel="stylesheet" href="{CDN_BI}"/>
  <script src="{CDN_VEGA}"></script>
  <script src="{CDN_VEGALITE}"></script>
  <script src="{CDN_EMBED}"></script>
  <style>
    :root {{
      --primary: #1e2a6e;
      --primary-light: #3d4fb5;
      --accent: #7c83e8;
    }}
    body {{ background: #f0f2f8; font-family: system-ui, sans-serif; margin: 0; }}

    /* ── Navbar ── */
    .site-nav {{
      background: linear-gradient(90deg, var(--primary) 0%, #2d3a8c 100%);
      box-shadow: 0 2px 12px rgba(0,0,0,.3);
    }}
    .nav-pill {{ border-radius: 20px; padding: .35rem .9rem !important; transition: background .2s; }}
    .nav-pill:hover {{ background: rgba(255,255,255,.15) !important; }}

    /* ── Page header ── */
    .page-header {{
      background: linear-gradient(135deg, #111838 0%, #1e2a6e 50%, #2e3fa3 100%);
      color: #fff;
      padding: 3.5rem 2rem 5.5rem;
      position: relative;
      overflow: hidden;
    }}
    .page-header::before {{
      content: "";
      position: absolute; inset: 0;
      background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Ccircle cx='30' cy='30' r='4'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    }}
    .page-header h1 {{ font-size: clamp(1.6rem, 3vw, 2.3rem); font-weight: 800; }}
    .page-header p  {{ opacity: .85; max-width: 700px; line-height: 1.7; margin-bottom: 0; }}
    .how-to-badge {{
      display: inline-flex; align-items: center; gap: .5rem;
      background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.2);
      border-radius: 8px; padding: .4rem .9rem;
      font-size: .82rem;
    }}
    .wave {{ display:block; width:100%; margin-top:-2px; }}

    /* ── Chart card ── */
    .chart-card {{
      background: #fff;
      border-radius: 16px;
      box-shadow: 0 4px 24px rgba(30,42,110,.1);
      padding: 1.5rem;
    }}
    #vis {{ width: 100%; }}

    /* ── Vega-embed controls re-skin ── */
    .vega-embed .vega-bindings {{
      display: flex;
      flex-wrap: wrap;
      gap: 1.5rem 2.5rem;
      align-items: flex-start;
      padding: 1rem 1.2rem;
      background: #f6f7fb;
      border-radius: 10px;
      border: 1px solid #e0e3f0;
      margin-bottom: 1rem;
    }}
    .vega-embed .vega-bind {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: .4rem .6rem;
    }}
    .vega-embed .vega-bind-name {{
      font-weight: 700;
      font-size: .85rem;
      color: var(--primary);
      white-space: nowrap;
    }}
    .vega-embed input[type="radio"] {{
      accent-color: var(--primary-light);
      width: 15px; height: 15px;
      cursor: pointer;
    }}
    .vega-embed label {{
      font-size: .82rem;
      color: #444;
      cursor: pointer;
    }}
    .vega-embed select {{
      border: 1.5px solid #c5cae9;
      border-radius: 6px;
      padding: .3rem .6rem;
      font-size: .85rem;
      color: var(--primary);
      background: #fff;
      cursor: pointer;
    }}
    .vega-embed select:focus {{ outline: none; border-color: var(--accent); }}

    /* ── Footer ── */
    .site-footer {{
      background: linear-gradient(90deg, var(--primary) 0%, #2d3a8c 100%);
      color: rgba(255,255,255,.7);
      font-size: .85rem;
    }}
    .site-footer .fw-semibold {{ color: #fff; }}
  </style>
</head>
<body>
{NAV}

<div class="page-header">
  <div class="container position-relative">
    <div class="d-flex gap-2 flex-wrap mb-3">
      <span class="how-to-badge"><i class="bi bi-hand-index-thumb-fill"></i> Click a region radio button to highlight</span>
      <span class="how-to-badge"><i class="bi bi-arrow-down-up"></i> Use the dropdown to switch disorder</span>
      <span class="how-to-badge"><i class="bi bi-cursor-fill"></i> Hover a circle for details</span>
    </div>
    <h1>GDP vs. Mental Health Disorder Prevalence</h1>
    <p class="mt-2">
      Each circle is one country&rsquo;s <strong>average disorder prevalence</strong> (across
      {year_min}&ndash;{year_max}) plotted against its GDP on a log scale. Wealthier nations
      tend to report higher prevalence &mdash; partly reflecting better diagnosis rates.
      Select a region or disorder to dig deeper.
    </p>
  </div>
</div>
<svg class="wave" viewBox="0 0 1440 60" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none" style="background:#111838">
  <path d="M0,30 C360,70 1080,-10 1440,30 L1440,60 L0,60 Z" fill="#f0f2f8"/>
</svg>

<div class="container-fluid py-3 px-4">
  <div class="chart-card">
    <div id="vis"></div>
  </div>
</div>

{FOOTER}

<script src="{CDN_BS_JS}"></script>
<script>
  vegaEmbed("#vis", {chart_spec}, {{
    mode: "vega-lite",
    renderer: "svg",
    actions: false,
  }}).catch(console.error);
</script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Write files & open
# ---------------------------------------------------------------------------
with open(os.path.join(BASE, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

with open(os.path.join(BASE, "visualization.html"), "w", encoding="utf-8") as f:
    f.write(vis_html)

index_path = os.path.join(BASE, "index.html")
print("Generated index.html and visualization.html")
webbrowser.open(f"file:///{index_path}")
