#!/usr/bin/env python3
"""
Generate an interactive HTML graph of the LispBM GitHub ecosystem.

Scrapes GitHub for forks of svenssonjoel/lispbm and repos that mention
"lispbm", then writes a self-contained D3.js force-directed graph.

Usage:
    python3 lispbm_graph.py [--token TOKEN] [--output graph.html] [--depth 1]

A GitHub personal access token raises the rate limit from 60 to 5000 req/hr.
Without a token, depth=1 with ~100 forks should stay within the limit fine.
"""

import argparse
import json
import sys
import time

try:
    import requests
except ImportError:
    sys.exit("Install requests:  pip install requests")

GITHUB_API = "https://api.github.com"
ORIGIN = "svenssonjoel/lispbm"


# ── GitHub helpers ─────────────────────────────────────────────────────────────

def gh_get(url, headers, params=None, retries=3):
    for _ in range(retries):
        r = requests.get(url, headers=headers, params=params, timeout=20)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (403, 429):
            reset = int(r.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(5, reset - int(time.time()) + 1)
            print(f"  Rate-limited – sleeping {wait}s", file=sys.stderr)
            time.sleep(wait)
        else:
            print(f"  HTTP {r.status_code}: {url}", file=sys.stderr)
            return None
    return None


def fetch_forks(full_name, headers, cur_depth, max_depth, seen):
    if cur_depth > max_depth or full_name in seen:
        return []
    seen.add(full_name)
    pairs = []
    page = 1
    while True:
        data = gh_get(
            f"{GITHUB_API}/repos/{full_name}/forks",
            headers,
            params={"per_page": 100, "page": page, "sort": "stargazers"},
        )
        if not data:
            break
        for fork in data:
            pairs.append((full_name, fork))
            if cur_depth < max_depth:
                pairs.extend(
                    fetch_forks(fork["full_name"], headers, cur_depth + 1, max_depth, seen)
                )
        if len(data) < 100:
            break
        page += 1
        time.sleep(0.3)
    return pairs


def search_repos(query, headers, max_pages=2):
    results = []
    for page in range(1, max_pages + 1):
        data = gh_get(
            f"{GITHUB_API}/search/repositories",
            headers,
            params={"q": query, "per_page": 30, "page": page, "sort": "stars"},
        )
        if not data:
            break
        results.extend(data.get("items", []))
        if len(data.get("items", [])) < 30:
            break
        time.sleep(1)
    return results


def search_uses_repos(headers):
    """Find repos that embed lispbm source by searching for a unique internal
    identifier. lbm_dec_as_i32 is defined in lispbm's lbm_types.h and is
    unlikely to appear in any unrelated codebase."""
    seen, results = set(), []
    for page in range(1, 5):  # 4 pages × 100 = 400 results max
        data = gh_get(
            f"{GITHUB_API}/search/code",
            headers,
            params={"q": "lbm_dec_as_i32", "per_page": 100, "page": page},
        )
        if not data:
            break
        items = data.get("items", [])
        for item in items:
            repo = item["repository"]
            fn = repo["full_name"]
            if fn not in seen:
                seen.add(fn)
                results.append(repo)
        print(f"  uses search page {page}: {len(items)} hits, {len(seen)} unique repos so far", file=sys.stderr)
        if len(items) < 100:
            break
        time.sleep(7)  # code search: 10 req/min authenticated
    return results



def is_driveby(fork, upstream=None, headers=None):
    """True if the fork was never meaningfully touched after creation.

    GitHub copies the parent description to every fork automatically, so
    description is not a useful signal. Base check: no stars AND never pushed
    to (pushed_at inherited from parent will be older than created_at).

    If upstream and headers are provided, also checks whether the fork owner
    ever opened a PR toward the upstream — if so, it is not a drive-by.
    """
    base = (
        fork.get("stargazers_count", 0) == 0
        and fork.get("pushed_at", "z") <= fork.get("created_at", "")
    )
    if not base:
        return False
    if upstream and headers:
        owner = fork["owner"]["login"]
        data = gh_get(
            f"{GITHUB_API}/repos/{upstream}/pulls",
            headers,
            params={"state": "all", "head": owner, "per_page": 1},
        )
        if data:  # at least one PR found → not a drive-by
            return False
        time.sleep(0.2)
    return True


def make_node(repo, kind):
    return {
        "id":          repo["full_name"],
        "label":       repo["full_name"],
        "url":         repo["html_url"],
        "type":        kind,
        "stars":       repo.get("stargazers_count", 0),
        "description": (repo.get("description") or "").strip(),
        "language":    repo.get("language") or "",
        "updated":     (repo.get("updated_at") or "")[:10],
    }


def user_node(login):
    return {
        "id":          login,
        "label":       login,
        "url":         f"https://github.com/{login}",
        "type":        "user",
        "stars":       0,
        "description": "",
        "language":    "",
        "updated":     "",
    }


def build_graph(token, max_depth, check_prs=False):
    hdrs = {"Accept": "application/vnd.github+json"}
    if token:
        hdrs["Authorization"] = f"Bearer {token}"

    nodes, edges = {}, []

    print(f"Fetching {ORIGIN} …", file=sys.stderr)
    origin = gh_get(f"{GITHUB_API}/repos/{ORIGIN}", hdrs)
    if not origin:
        sys.exit(f"Could not fetch {ORIGIN}")
    canon = origin["full_name"]
    nodes[canon] = make_node(origin, "origin")

    def ensure_user(login):
        if login not in nodes:
            nodes[login] = user_node(login)
            edges.append({"source": canon, "target": login, "type": "user_link"})

    print(f"Fetching forks (depth={max_depth}) …", file=sys.stderr)
    skipped = 0
    for _, fork in fetch_forks(canon, hdrs, 1, max_depth, set()):
        if is_driveby(fork, upstream=canon if check_prs else None, headers=hdrs if check_prs else None):
            skipped += 1
            continue
        fn    = fork["full_name"]
        owner = fork["owner"]["login"]
        ensure_user(owner)
        if fn not in nodes:
            nodes[fn] = make_node(fork, "fork")
        edges.append({"source": owner, "target": fn, "type": "fork"})
    if skipped:
        print(f"  (dropped {skipped} drive-by forks)", file=sys.stderr)

    print("Searching related repos …", file=sys.stderr)
    for repo in search_repos("lispbm", hdrs):
        fn    = repo["full_name"]
        owner = repo["owner"]["login"]
        if fn not in nodes:
            nodes[fn] = make_node(repo, "related")
            ensure_user(owner)
            edges.append({"source": owner, "target": fn, "type": "mention"})

    print("Searching for repos that use lispbm …", file=sys.stderr)
    for repo in search_uses_repos(hdrs):
        fn    = repo["full_name"]
        owner = repo["owner"]["login"]
        if fn not in nodes:
            nodes[fn] = make_node(repo, "related")
            ensure_user(owner)
            edges.append({"source": owner, "target": fn, "type": "mention"})

    print(f"  → {len(nodes)} nodes, {len(edges)} edges", file=sys.stderr)
    return list(nodes.values()), edges, origin


# ── HTML template ──────────────────────────────────────────────────────────────

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SEO_TITLE</title>
<meta name="description" content="SEO_DESCRIPTION">
<meta name="keywords" content="SEO_KEYWORDS">
<link rel="canonical" href="SEO_URL">
<!-- Open Graph -->
<meta property="og:type"        content="website">
<meta property="og:url"         content="SEO_URL">
<meta property="og:title"       content="SEO_TITLE">
<meta property="og:description" content="SEO_DESCRIPTION">
<!-- Twitter Card -->
<meta name="twitter:card"        content="summary">
<meta name="twitter:title"       content="SEO_TITLE">
<meta name="twitter:description" content="SEO_DESCRIPTION">
<!-- JSON-LD -->
<script type="application/ld+json">SEO_JSONLD</script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0d1117; color: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }

  h1 { position: fixed; top: 14px; left: 16px; font-size: .95rem; font-weight: 600; opacity: .8; z-index: 10; }
  #info { position: fixed; top: 36px; left: 16px; font-size: .72rem; opacity: .45; z-index: 10; }
  #hint { position: fixed; top: 14px; right: 16px; font-size: .72rem; opacity: .45; z-index: 10; }

  #graph { position: fixed; top: 0; left: 0; width: 100%; height: 100%; overflow: visible; }

  .link { stroke-opacity: .5; fill: none; }
  .link-user_link { stroke: #a371f7; }
  .link-fork      { stroke: #58a6ff; }
  .link-mention   { stroke: #3fb950; stroke-dasharray: 5 3; }

  .node circle { cursor: pointer; }
  .node circle:hover { stroke: #fff !important; stroke-width: 2.5px !important; }
  .node text { font-size: 10px; fill: #8b949e; pointer-events: none; user-select: none; }

  #tooltip {
    position: fixed; pointer-events: none;
    background: #161b22; border: 1px solid #30363d; border-radius: 6px;
    padding: 10px 14px; font-size: .8rem; max-width: 300px; line-height: 1.6;
    box-shadow: 0 4px 24px rgba(0,0,0,.7); z-index: 30; display: none;
  }
  #tooltip .tip-name { color: #58a6ff; font-weight: 600; word-break: break-all; }
  #tooltip .tip-desc { color: #c9d1d9; margin-top: 4px; }
  #tooltip .tip-meta { color: #8b949e; font-size: .72rem; margin-top: 5px; }
  #tooltip .tip-hint { color: #3fb950; font-size: .72rem; margin-top: 3px; }

  #legend {
    position: fixed; bottom: 18px; left: 16px; font-size: .73rem;
    background: #161b22; border: 1px solid #30363d; border-radius: 6px;
    padding: 10px 14px; z-index: 10; line-height: 2;
  }
  .leg { display: flex; align-items: center; gap: 8px; }
  .leg-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
</style>
</head>
<body>
<h1>LispBM GitHub Ecosystem</h1>
<div id="info">GRAPH_INFO</div>
<div id="hint">scroll to zoom · drag to pan · drag nodes · click to open</div>
<svg id="graph"></svg>
<div id="tooltip"></div>
<div id="legend">
  <div class="leg"><div class="leg-dot" style="background:#f0c040"></div>Origin</div>
  <div class="leg"><div class="leg-dot" style="background:#a371f7"></div>User</div>
  <div class="leg"><div class="leg-dot" style="background:#58a6ff"></div>Fork</div>
  <div class="leg"><div class="leg-dot" style="background:#3fb950"></div>Related repo</div>
  <div class="leg" style="margin-top:4px">
    <svg width="26" height="10"><line x1="0" y1="5" x2="26" y2="5" stroke="#58a6ff" stroke-opacity=".7" stroke-width="1.5"></line></svg>
    fork edge
  </div>
  <div class="leg">
    <svg width="26" height="10"><line x1="0" y1="5" x2="26" y2="5" stroke="#3fb950" stroke-opacity=".7" stroke-dasharray="4 2" stroke-width="1.5"></line></svg>
    mention edge
  </div>
</div>

<script>
D3_INLINE
</script>
<script>
const graphData = GRAPH_DATA;

const COLOR = { origin: "#f0c040", user: "#a371f7", fork: "#58a6ff", related: "#3fb950" };
const radius = d => d.type === "user" ? 9 : Math.max(7, Math.sqrt((d.stars || 0) + 1) * 2.8);

const svg   = d3.select("#graph");
const W     = window.innerWidth;
const H     = window.innerHeight;
svg.attr("viewBox", `0 0 ${W} ${H}`);
const root  = svg.append("g");

// Zoom / pan
svg.call(
  d3.zoom().scaleExtent([0.05, 10])
    .on("zoom", e => root.attr("transform", e.transform))
);

// Arrow markers per edge type
const defs = svg.append("defs");
["fork", "mention"].forEach(t => {
  defs.append("marker")
    .attr("id", `arrow-${t}`)
    .attr("viewBox", "0 -4 8 8")
    .attr("refX", 8)
    .attr("refY", 0)
    .attr("markerWidth", 5)
    .attr("markerHeight", 5)
    .attr("orient", "auto")
    .append("path")
      .attr("d", "M0,-4L8,0L0,4")
      .attr("fill", t === "fork" ? "#58a6ff" : "#3fb950")
      .attr("opacity", .7);
});

// Force simulation
const sim = d3.forceSimulation(graphData.nodes)
  .force("link",      d3.forceLink(graphData.edges).id(d => d.id).distance(130))
  .force("charge",    d3.forceManyBody().strength(-280))
  .force("center",    d3.forceCenter(W / 2, H / 2))
  .force("collision", d3.forceCollide().radius(d => radius(d) + 10));

// Edges
const link = root.append("g").attr("class", "links")
  .selectAll("line")
  .data(graphData.edges)
  .join("line")
    .attr("class", d => `link link-${d.type}`)
    .attr("stroke-width", 1.3)
    .attr("marker-end", d => d.type === "user_link" ? null : `url(#arrow-${d.type})`);

// Nodes
const nodeG = root.append("g").attr("class", "nodes")
  .selectAll("g")
  .data(graphData.nodes)
  .join("g")
    .attr("class", "node")
    .call(
      d3.drag()
        .on("start", (e, d) => { if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
        .on("drag",  (e, d) => { d.fx = e.x; d.fy = e.y; })
        .on("end",   (e, d) => { if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; })
    );

nodeG.append("circle")
  .attr("r", radius)
  .attr("fill", d => COLOR[d.type])
  .attr("fill-opacity", d => d.type === "origin" ? 1 : 0.82)
  .attr("stroke", d => d3.color(COLOR[d.type]).darker(1.2))
  .attr("stroke-width", 1.5)
  .on("click",     (_, d) => window.open(d.url, "_blank"))
  .on("mouseover", (e, d) => showTip(e, d))
  .on("mousemove", e  => moveTip(e))
  .on("mouseout",  ()  => hideTip());

nodeG.append("text")
  .attr("dy", d => radius(d) + 13)
  .attr("text-anchor", "middle")
  .text(d => d.type === "user" ? d.label : (d.label.split("/")[1] || d.label));

// Tick: shorten line so arrow lands at node edge
sim.on("tick", () => {
  link
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => {
      const dx = d.target.x - d.source.x, dy = d.target.y - d.source.y;
      const len = Math.sqrt(dx*dx + dy*dy) || 1;
      return d.target.x - (dx / len) * (radius(d.target) + 6);
    })
    .attr("y2", d => {
      const dx = d.target.x - d.source.x, dy = d.target.y - d.source.y;
      const len = Math.sqrt(dx*dx + dy*dy) || 1;
      return d.target.y - (dy / len) * (radius(d.target) + 6);
    });
  nodeG.attr("transform", d => `translate(${d.x},${d.y})`);
});

// Tooltip
const tip = document.getElementById("tooltip");

function showTip(e, d) {
  const meta = [
    d.stars ? `⭐ ${d.stars}` : null,
    d.language || null,
    d.updated ? `updated ${d.updated}` : null,
  ].filter(Boolean).join(" · ");
  tip.innerHTML =
    `<div class="tip-name">${d.label}</div>` +
    (d.description ? `<div class="tip-desc">${d.description}</div>` : "") +
    (meta ? `<div class="tip-meta">${meta}</div>` : "") +
    `<div class="tip-hint">↗ click to open on GitHub</div>`;
  tip.style.display = "block";
  moveTip(e);
}
function moveTip(e) {
  const x = e.clientX + 16, y = e.clientY - 10;
  tip.style.left = (x + tip.offsetWidth > window.innerWidth ? e.clientX - tip.offsetWidth - 10 : x) + "px";
  tip.style.top  = (y + tip.offsetHeight > window.innerHeight ? window.innerHeight - tip.offsetHeight - 10 : y) + "px";
}
function hideTip() { tip.style.display = "none"; }
</script>
</body>
</html>
"""


D3_CDN = "https://d3js.org/d3.v7.min.js"


def fetch_d3():
    print("Fetching D3.js for offline embedding …", file=sys.stderr)
    r = requests.get(D3_CDN, timeout=30)
    if r.status_code != 200:
        sys.exit(f"Could not fetch D3.js from {D3_CDN} (HTTP {r.status_code})")
    return r.text


def generate_html(nodes, edges, origin, output, url=""):
    # ── graph data ──────────────────────────────────────────────────────────────
    data = json.dumps({"nodes": nodes, "edges": edges}, ensure_ascii=False)
    data = data.replace("<", "\\u003c").replace(">", "\\u003e")
    info = f"generated {time.strftime('%Y-%m-%d')}  ·  {len(nodes)} nodes  ·  {len(edges)} edges"

    # ── SEO fields ──────────────────────────────────────────────────────────────
    fork_count    = sum(1 for n in nodes if n["type"] == "fork")
    related_count = sum(1 for n in nodes if n["type"] == "related")
    user_count    = sum(1 for n in nodes if n["type"] == "user")
    origin_desc   = (origin.get("description") or "").strip()

    seo_title = f"LispBM GitHub Ecosystem — {fork_count} forks · {related_count} related repos · {user_count} contributors"
    seo_desc  = (
        f"Interactive graph of {fork_count} forks and {related_count} related GitHub repositories "
        f"in the LispBM ecosystem, across {user_count} contributors."
        + (f" LispBM: {origin_desc}" if origin_desc else "")
    )
    seo_keywords = (
        "LispBM, Lisp, embedded Lisp, ESP32, microcontroller, REPL, "
        "Lisp interpreter, GitHub forks, open source, svenssonjoel"
    )
    seo_url = url or origin.get("html_url", "")

    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": seo_title,
        "description": seo_desc,
        "url": seo_url,
        "about": {
            "@type": "SoftwareSourceCode",
            "name": origin.get("full_name", "LispBM"),
            "url": origin.get("html_url", ""),
            "description": origin_desc,
            "programmingLanguage": "Lisp",
        },
    }, ensure_ascii=False)

    # ── assemble ─────────────────────────────────────────────────────────────────
    d3_src = fetch_d3()
    html = (
        HTML_TEMPLATE
        .replace("SEO_TITLE",       seo_title)
        .replace("SEO_DESCRIPTION", seo_desc)
        .replace("SEO_KEYWORDS",    seo_keywords)
        .replace("SEO_URL",         seo_url)
        .replace("SEO_JSONLD",      jsonld)
        .replace("D3_INLINE",       d3_src)
        .replace("GRAPH_DATA",      data)
        .replace("GRAPH_INFO",      info)
    )
    with open(output, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {output}", file=sys.stderr)


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="Generate a D3 force-graph of the LispBM GitHub ecosystem.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("--token",  metavar="TOKEN", default=None,
                    help="GitHub personal access token (raises rate limit to 5000/hr). "
                         "Falls back to GITHUB_TOKEN env var if not set.")
    ap.add_argument("--output", metavar="FILE",  default="lispbm_graph.html",
                    help="Output HTML file (default: lispbm_graph.html in the repo root)")
    ap.add_argument("--depth",  metavar="N",     default=4, type=int,
                    help="Fork recursion depth (default: 4; use a token to avoid rate limits)")
    ap.add_argument("--url",       metavar="URL", default="",
                    help="Canonical URL of the published page (used in og:url and JSON-LD)")
    ap.add_argument("--check-prs", action="store_true",
                    help="Extra API call per fork to rescue forks that opened PRs upstream "
                         "(slower, recommended with --token)")
    args = ap.parse_args()

    import os
    token = args.token or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Warning: no token set — rate limited to 60 req/hr. Set GITHUB_TOKEN or use --token.", file=sys.stderr)

    nodes, edges, origin = build_graph(token, args.depth, args.check_prs)
    generate_html(nodes, edges, origin, args.output, args.url)


if __name__ == "__main__":
    main()
