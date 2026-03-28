import json
import numpy as np
import pandas as pd
import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Stadium Finder", page_icon="🏟️", layout="centered")
st.title("🏟️ Closest Stadiums Finder")
st.caption("Pick a team and find the nearest venues in every other league.")

# ── Data loading (cached so the files are only read once) ─────────────────
@st.cache_data
def load_all_leagues():
    def load_league(filepath, list_key, team_col, lat_col, lon_col, league_name):
        with open(filepath, 'r') as f:
            data = json.load(f)
        df = pd.json_normalize(data[list_key])
        df = df.rename(columns={lat_col: 'lat', lon_col: 'lon', team_col: 'team'})
        df['league'] = league_name
        return df[['league', 'team', 'lat', 'lon']]

    leagues = [
        ('stadiumdata/nba_stadiums.json',  'NBA'),
        ('stadiumdata/nfl_stadiums.json',  'NFL'),
        ('stadiumdata/mlb_stadiums.json',  'MLB'),
        ('stadiumdata/nhl_stadiums.json',  'NHL'),
        ('stadiumdata/mls_stadiums.json',  'MLS'),
        ('stadiumdata/wnba_stadiums.json', 'WNBA'),
    ]
    frames = []
    for path, name in leagues:
        frames.append(load_league(path, 'venues', 'team',
                                  'coordinates.latitude', 'coordinates.longitude', name))
    return pd.concat(frames, ignore_index=True)

# ── Haversine ─────────────────────────────────────────────────────────────
def haversine_vectorized(lat1, lon1, lat2, lon2):
    R = 3958.8
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi    = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
    return np.round(2 * R * np.arcsin(np.sqrt(a)), 3)

# ── Load data ─────────────────────────────────────────────────────────────
try:
    lg = load_all_leagues()
except FileNotFoundError as e:
    st.error(f"Could not load stadium data: {e}")
    st.stop()

# ── Sidebar controls ─────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Options")
    league = st.selectbox("League", sorted(lg['league'].unique()))
    teams  = sorted(lg.loc[lg['league'] == league, 'team'].tolist())
    team   = st.selectbox("Team", teams)
    n      = st.slider("Closest teams per league", min_value=1, max_value=5, value=1)
    run    = st.button("Find closest stadiums", type="primary")

# ── Main output ───────────────────────────────────────────────────────────
if run:
    row = lg.loc[(lg['league'] == league) & (lg['team'] == team)]

    ref_lat = row['lat'].values[0]
    ref_lon = row['lon'].values[0]

    df = lg.copy()
    df['distance_mi'] = haversine_vectorized(ref_lat, ref_lon, df['lat'], df['lon'])

    results = (
        df[df['league'] != league]
        .sort_values('distance_mi')
        .groupby('league')
        .head(n)
        .sort_values(['league', 'distance_mi'])
        .reset_index(drop=True)
    )

    st.subheader(f"Closest stadiums to **{team}** ({league})")

    for lg_name, group in results.groupby('league'):
        st.markdown(f"#### {lg_name}")
        display = group[['team', 'distance_mi']].rename(
            columns={'team': 'Team', 'distance_mi': 'Distance (mi)'}
        )
        st.dataframe(display, use_container_width=True, hide_index=True)

    # Optional: map of all selected results + reference team
    st.markdown("---")
    st.markdown("#### 🗺️ Map")
    ref_point = row[['lat', 'lon']].copy()
    map_df = pd.concat([
        ref_point,
        results[['lat', 'lon']]
    ]).rename(columns={'lat': 'latitude', 'lon': 'longitude'})
    st.map(map_df, zoom=3)