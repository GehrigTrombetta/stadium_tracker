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
    def load_league(filepath, list_key, team_col, venue_col, lat_col, lon_col, league_name):
        with open(filepath, 'r') as f:
            data = json.load(f)
        df = pd.json_normalize(data[list_key])
        df = df.rename(columns={lat_col: 'lat', lon_col: 'lon', team_col: 'team', venue_col: 'venue'})
        df['league'] = league_name
        df['logo'] = df['png'] if 'png' in df.columns else None
        return df[['league', 'team', 'venue', 'logo', 'lat', 'lon']]

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
        frames.append(load_league(path, 'venues', 'team', 'name',
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

# ── Main page controls ────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    league = st.selectbox("League", sorted(lg['league'].unique()))
with col2:
    teams = sorted(lg.loc[lg['league'] == league, 'team'].tolist())
    team  = st.selectbox("Team", teams)

n   = st.slider("Closest teams per league", min_value=1, max_value=5, value=1)
run = st.button("Find closest stadiums", type="primary")

# ── Main output ───────────────────────────────────────────────────────────
if run:
    row = lg.loc[(lg['league'] == league) & (lg['team'] == team)]

    ref_lat = row['lat'].values[0]
    ref_lon = row['lon'].values[0]

    df = lg.copy()
    df['distance_mi'] = haversine_vectorized(ref_lat, ref_lon, df['lat'], df['lon'])

    LEAGUE_ORDER = ['NBA', 'NFL', 'MLB', 'NHL', 'MLS', 'WNBA']

    results = (
        df[df['league'] != league]
        .sort_values('distance_mi')
        .groupby('league')
        .head(n)
        .reset_index(drop=True)
    )
    map_results = results[['lat', 'lon']].copy()
    results['league'] = pd.Categorical(results['league'], categories=LEAGUE_ORDER, ordered=True)
    results = results.sort_values(['league', 'distance_mi'])

    st.subheader(f"Closest stadiums to **{team}** ({league})")

    for lg_name, group in results.groupby('league', observed=True):
        for _, r in group.iterrows():
            img_col, text_col = st.columns([1, 16])
            with img_col:
                if pd.notna(r.get('logo')):
                    st.image(r['logo'], width=64)
                else:
                    st.write("🏟️")
            with text_col:
                st.write(f"**{lg_name} |** {r['team']} | {r['venue']} | {r['distance_mi']} miles")

    # Optional: map of all selected results + reference team
    st.markdown("---")
    st.markdown("#### 🗺️ Map")
    ref_point = row[['lat', 'lon']].copy()
    map_df = pd.concat([
        ref_point,
        map_results
    ]).rename(columns={'lat': 'latitude', 'lon': 'longitude'}).dropna(subset=['latitude', 'longitude'])
    st.map(map_df, zoom=6)