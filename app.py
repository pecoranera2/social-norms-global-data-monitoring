# -*- coding: utf-8 -*-
"""Social Norms Global Data Repository
Run: streamlit run app.py
"""
import html
import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
INPUTS = os.path.join(HERE, "inputs")

# colours and font
COL_INK, COL_INK2, COL_MUTED = "#0b0b0b", "#52514e", "#6b6a63"
COL_SURFACE, COL_LAND, COL_LINE = "#fcfcfb", "#eeede8", "#e1e0d9"
FONT = "Georgia, 'Times New Roman', Times, serif"

WVS = "World Values Survey"
SOURCES = [WVS, "Arab Barometer", "Afrobarometer", "Asian Barometer", "Latinobarometro", "Eurobarometer"]
SRC_COL = {WVS: "#3d3d3a", "Arab Barometer": "#d55e00", "Latinobarometro": "#009e73",
           "Afrobarometer": "#e69f00", "Asian Barometer": "#cc79a7", "Eurobarometer": "#5b5ea6"}
SRC_LABEL = {WVS: "World Values Survey", "Latinobarometro": "Latinobarómetro"}
SRC_SHORT = {WVS: "WVS", "Arab Barometer": "Arab", "Afrobarometer": "Afro", "Asian Barometer": "Asian",
             "Latinobarometro": "Latino", "Eurobarometer": "Euro"}
SRC_ROUND = {WVS: "Wave 7 · 2017-2023", "Arab Barometer": "Wave 8 · 2024", "Afrobarometer": "Round 9 · 2023",
             "Asian Barometer": "Wave 6 · 2021-2023", "Latinobarometro": "2024",
             "Eurobarometer": "Special EB · 2023-2024"}
CLUSTERS = ["Social and gender norms", "Trust", "Participation"]
RAMP = {1: "#d8d7d0", 2: "#a8a79f", 3: "#76756e", 4: "#3d3d3a"}


def lab(s):
    return SRC_LABEL.get(s, s)


st.set_page_config(page_title="Social Norms Global Data Repository", layout="wide")
st.markdown(
    f"""
    <style>
    html, body, [class*="css"], .stMarkdown, .stMarkdown p, .stCaption, h1, h2, h3, label p,
    button p, [data-testid="stSidebarNav"] span, .stSelectbox div {{ font-family: {FONT} !important; }}
    .block-container {{ padding-top: 2rem; }}
    h1, h2, h3 {{ font-family: {FONT}; color: {COL_INK}; }}
    .lede {{ color: {COL_INK2}; font-size: 1.08rem; margin: -0.4rem 0 0.8rem 0; }}
    .grp {{ margin: 1.3rem 0 0.5rem 0; font-size: 1.1rem; font-weight: 600; color: {COL_INK};
            border-bottom: 1px solid {COL_LINE}; padding-bottom: 0.3rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(min(290px,100%), 1fr)); gap: 0.6rem; }}
    .card {{ border: 1px solid {COL_LINE}; border-radius: 8px; padding: 0.6rem 0.75rem; background: #fff; }}
    .name {{ font-size: 0.95rem; line-height: 1.25; margin-bottom: 0.5rem; color: {COL_INK}; }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 4px; }}
    .chip {{ font-size: 0.72rem; color: #fff; border-radius: 999px; padding: 1px 8px; }}
    button[data-testid="stBaseButton-pillsActive"] {{ background:{COL_INK}; color:#fff; border-color:{COL_INK}; }}
    button[data-testid="stBaseButton-pillsActive"] p {{ color:#fff; }}
    .stats {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 0.6rem; }}
    .stat {{ background:#fff; border:1px solid {COL_LINE}; border-top:5px solid {COL_INK}; border-radius:8px;
             padding:0.6rem 0.8rem; }}
    .stat .n {{ font-size:1.5rem; font-weight:600; color:{COL_INK}; line-height:1.2; }}
    .stat .l {{ font-size:0.9rem; color:{COL_INK}; }}
    .stat .s {{ font-size:0.78rem; color:{COL_MUTED}; }}
    .scard {{ border: 1px solid {COL_LINE}; border-top: 5px solid {COL_INK}; border-radius: 8px;
              padding: 0.6rem 0.85rem 0.4rem; background: #fff; }}
    .scard h4 {{ font-family: {FONT}; font-size: 1.02rem; margin: 0 0 0.1rem 0; padding: 0; color: {COL_INK}; }}
    .scard .meta {{ font-size: 0.78rem; color: {COL_MUTED}; margin-bottom: 0.4rem; }}
    .scard .tp {{ font-size: 0.78rem; color: {COL_MUTED}; margin: 0.5rem 0 0.15rem 0; text-transform: uppercase;
                  letter-spacing: 0.03em; }}
    .scard ul {{ margin: 0 0 0.2rem 1rem; padding: 0; }}
    .scard li {{ font-size: 0.9rem; line-height: 1.3; color: {COL_INK}; margin: 0.1rem 0; }}
    .scard .none {{ font-size: 0.88rem; color: {COL_MUTED}; font-style: italic; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def _mtime(path):
    return os.path.getmtime(path)


@st.cache_data
def _read(path, mtime):
    return pd.read_csv(path)


def load(path):
    return _read(path, _mtime(path))


# variable lists
bar = load(os.path.join(INPUTS, "barometer_variables_latest.csv"))
wvs = load(os.path.join(DATA, "wvs_wave7_variables.csv")).rename(
    columns={"Cluster": "cluster", "Topic": "topic", "Variable": "variable"})
wvs["source"] = WVS
variables = pd.concat([bar[["cluster", "topic", "variable", "source"]],
                       wvs[["cluster", "topic", "variable", "source"]]], ignore_index=True).drop_duplicates()
variables["order"] = range(len(variables))
first = variables.groupby("variable").order.min()
variables["v_order"] = variables.variable.map(first)
variables["t_order"] = variables.groupby(["cluster", "topic"]).order.transform("min")
variables["n_src"] = variables.variable.map(variables.groupby("variable").source.nunique())

countries = load(os.path.join(DATA, "latest_countries.csv"))
N_COUNTRIES = countries.groupby("source").iso3.nunique().to_dict()


def geo(fig, h=500):
    fig.update_geos(projection_type="natural earth", showframe=False, showcoastlines=False, showland=True,
                    landcolor=COL_LAND, showcountries=True, countrycolor="#d8d7d0", showocean=False,
                    bgcolor=COL_SURFACE, lataxis_range=[-58, 82])
    fig.update_layout(height=h, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor=COL_SURFACE, dragmode=False,
                      font=dict(family=FONT, color=COL_INK, size=13),
                      legend=dict(orientation="h", yanchor="top", y=0.02, xanchor="left", x=0.0,
                                  bgcolor="rgba(0,0,0,0)"))
    return fig


# pages
def overview_page():
    st.title("Social Norms Global Data Repository")
    st.markdown('<p class="lede">Social and gender norms, trust and participation in the latest round of the '
                "World Values Survey and five regional barometers.</p>", unsafe_allow_html=True)

    tiles = "".join(
        f'<div class="stat" style="border-top-color:{SRC_COL[s]}"><div class="n">{N_COUNTRIES.get(s, 0)}</div>'
        f'<div class="l">{lab(s)}</div><div class="s">countries · {SRC_ROUND[s]}</div></div>' for s in SOURCES)
    st.markdown(f'<div class="stats">{tiles}</div>', unsafe_allow_html=True)
    st.markdown("")

    pick = st.pills("Survey", ["All"] + SOURCES, default="All", key="map_pick",
                    format_func=lambda s: "All surveys" if s == "All" else lab(s),
                    label_visibility="collapsed") or "All"

    fig = go.Figure()
    if pick == "All":
        n = countries.groupby(["iso3", "country"]).source.agg(list).reset_index()
        n["k"] = n.source.map(len).clip(upper=4)
        for k in (1, 2, 3, 4):
            g = n[n.k == k]
            if g.empty:
                continue
            fig.add_trace(go.Choropleth(
                locations=g.iso3, z=[1] * len(g), locationmode="ISO-3", colorscale=[[0, RAMP[k]], [1, RAMP[k]]],
                showscale=False, marker_line_color=COL_SURFACE, marker_line_width=0.6,
                text=[f"<b>{c}</b><br>" + "<br>".join(lab(s) for s in ss) for c, ss in zip(g.country, g.source)],
                hovertemplate="%{text}<extra></extra>",
                name={1: "1 survey", 2: "2 surveys", 3: "3 surveys", 4: "4 or more"}[k]))
        st.caption(f"{countries.iso3.nunique()} countries in at least one survey.")
    else:
        g = countries[countries.source == pick]
        fig.add_trace(go.Choropleth(
            locations=g.iso3, z=[1] * len(g), locationmode="ISO-3", colorscale=[[0, SRC_COL[pick]], [1, SRC_COL[pick]]],
            showscale=False, marker_line_color=COL_SURFACE, marker_line_width=0.6, text=g.country,
            hovertemplate="<b>%{text}</b><extra></extra>", name=lab(pick)))
        st.caption(f"{lab(pick)} · {SRC_ROUND[pick]} · {len(g)} countries")
    geo(fig, 520)
    fig.update_layout(showlegend=pick == "All")
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False, "scrollZoom": False})

    if pick != "All":
        with st.expander(f"Countries in {lab(pick)}"):
            st.write(", ".join(sorted(countries[countries.source == pick].country)))

    st.divider()
    tiles = ""
    for cl in CLUSTERS:
        v = variables[variables.cluster == cl]
        shared = v[v.n_src > 1].variable.nunique()
        tiles += (f'<div class="stat"><div class="n">{v.variable.nunique()}</div><div class="l">{cl}</div>'
                  f'<div class="s">variables · {shared} in two or more surveys</div></div>')
    st.markdown(f'<div class="stats" style="grid-template-columns:repeat(auto-fill,minmax(min(240px,100%),1fr))">{tiles}</div>',
                unsafe_allow_html=True)

    st.divider()
    st.subheader("Notes")
    st.markdown(NOTES)


def clusters_page():
    st.header("Variables by cluster")
    cl = st.pills("Cluster", CLUSTERS, default=CLUSTERS[0], key="cl_pick", label_visibility="collapsed") or CLUSTERS[0]
    view = st.segmented_control("View", ["By survey", "By variable"], default="By survey", key="cl_view",
                                label_visibility="collapsed") or "By survey"
    v = variables[variables.cluster == cl]
    topics = v.drop_duplicates("topic").sort_values("t_order").topic.tolist()

    if view == "By survey":
        cards = []
        for s in SOURCES:
            x = v[v.source == s]
            body = ""
            if x.empty:
                body = '<div class="none">No variables in this cluster.</div>'
            for t in topics:
                y = x[x.topic == t].sort_values(["n_src", "v_order"], ascending=[False, True])
                if y.empty:
                    continue
                body += f'<div class="tp">{html.escape(t)}</div><ul>'
                body += "".join(f"<li>{html.escape(n)}</li>" for n in y.variable)
                body += "</ul>"
            cards.append(f'<div class="scard" style="border-top-color:{SRC_COL[s]}"><h4>{lab(s)}</h4>'
                         f'<div class="meta">{SRC_ROUND[s]} · {N_COUNTRIES.get(s, 0)} countries · '
                         f'{x.variable.nunique()} variable{"" if x.variable.nunique() == 1 else "s"}</div>{body}</div>')
        st.markdown(f'<div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(min(330px,100%),1fr))">'
                    f'{"".join(cards)}</div>', unsafe_allow_html=True)
    else:
        src = st.pills("Survey", ["All"] + SOURCES, default="All", key="cl_src",
                       format_func=lambda s: "All surveys" if s == "All" else lab(s),
                       label_visibility="collapsed") or "All"
        if src != "All":
            v = v[v.variable.isin(v[v.source == src].variable)]
        st.caption(f"{v.variable.nunique()} variables.")
        parts = []
        for t in topics:
            g = v[v.topic == t]
            if g.empty:
                continue
            parts.append(f'<div class="grp">{html.escape(t)}</div><div class="grid">')
            for name, y in sorted(g.groupby("variable"), key=lambda kv: (-kv[1].n_src.iloc[0], kv[1].v_order.iloc[0])):
                chips = "".join(f'<span class="chip" style="background:{SRC_COL[s]}">{SRC_SHORT[s]}</span>'
                                for s in SOURCES if s in set(y.source))
                parts.append(f'<div class="card"><div class="name">{html.escape(name)}</div>'
                             f'<div class="chips">{chips}</div></div>')
            parts.append("</div>")
        st.markdown("".join(parts), unsafe_allow_html=True)


# overview notes
NOTES = """
- **Latest round only.** World Values Survey wave 7 (2017-2023); Arab Barometer wave 8 (2024); Afrobarometer
  round 9 (2023); Asian Barometer wave 6 (2021-2023); Latinobarómetro 2024; Eurobarometer: Special EB on gender
  stereotypes (2024) and Special EB on discrimination (2023).
- **Matching** is by question wording; some matches are close rather than identical.
"""


st.navigation([
    st.Page(overview_page, title="Overview", url_path="overview", default=True),
    st.Page(clusters_page, title="Variables by cluster", url_path="clusters"),
]).run()
