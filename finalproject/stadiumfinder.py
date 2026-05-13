import json
import requests as rq
import numpy as np
import pandas as pd
import streamlit as st
import folium as fl
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Data loading
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
        ('data/nba_stadiums.json',  'NBA'),
        ('data/nfl_stadiums.json',  'NFL'),
        ('data/mlb_stadiums.json',  'MLB'),
        ('data/nhl_stadiums.json',  'NHL'),
        ('data/mls_stadiums.json',  'MLS'),
        ('data/wnba_stadiums.json', 'WNBA'),
    ]
    frames = []
    for path, name in leagues:
        frames.append(load_league(path, 'venues', 'team', 'name',
                                  'coordinates.latitude', 'coordinates.longitude', name))
    return pd.concat(frames, ignore_index=True)

# Haversine
def haversine_vectorized(lat1, lon1, lat2, lon2):
    R = 3958.8
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi    = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
    return np.round(2 * R * np.arcsin(np.sqrt(a)), 3)

# Location formatter
def format_location(location):
    STATE_ABBREVS = {
        "Arizona": "AZ", "Arkansas": "AR",
        "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
        "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
        "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
        "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME",
        "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
        "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
        "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
        "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
        "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
        "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
        "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
        "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
        "Ontario": "ON", "Quebec": "QC", "British Columbia": "BC", "Alberta": "AB",
        "Manitoba": "MB", "Saskatchewan": "SK", "Nova Scotia": "NS",
        "New Brunswick": "NB", "Newfoundland and Labrador": "NL",
        "Prince Edward Island": "PE", "Northwest Territories": "NT",
        "Nunavut": "NU", "Yukon": "YT",
    }
    replacements = {
        "Washington, District of Columbia": "Washington, D.C.",
    }
    for original, replacement in replacements.items():
        location = location.replace(original, replacement)
    for full, abbrev in STATE_ABBREVS.items():
        if location.endswith(full):
            location = location[: -len(full)] + abbrev
            break
    return location

# Reverse geocoder
@st.cache_data
def reverse_geocode_locations(coords):
    geolocator = Nominatim(user_agent="stadium_finder")
    reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)
    locations = []
    for lat, lon in coords:
        try:
            loc = reverse(f"{lat}, {lon}", language="en")
            addr = loc.raw.get('address', {})
            city  = addr.get('city') or addr.get('town') or addr.get('village', '')
            state = addr.get('state', '')
            locations.append(f"{city}, {state}")
        except Exception:
            locations.append('')
    return locations

# Google geocoder
def google_geocode(address):
    try:
        resp = rq.get(
            "https://cent.ischool-iot.net/api/google/geocode",
            params={"location": address},
            headers={"X-API-KEY": "6381204ae3a51f855620260f"},
            timeout=10
        )
        data = resp.json()
        results_list = data.get("results", [])
        if results_list:
            loc = results_list[0]["geometry"]["location"]
            return loc["lat"], loc["lng"]
    except Exception:
        pass
    return None, None

# League colours, order & emoji
LEAGUE_COLORS = {
    'NBA':  'red',
    'NFL':  'green',
    'MLB':  'blue',
    'NHL':  'orange',
    'MLS':  'pink',
    'WNBA': 'purple',
}

LEAGUE_EMOJI = {
    'NBA':  '🏀',
    'NFL':  '🏈',
    'MLB':  '⚾',
    'NHL':  '🏒',
    'MLS':  '⚽',
    'WNBA': '🏀',
}

LEAGUE_ORDER       = ['WNBA', 'MLS', 'NHL', 'NFL', 'MLB', 'NBA']
OTHER_LEAGUE_ORDER = ['NBA', 'MLB', 'NFL', 'NHL', 'MLS', 'WNBA']

def with_emoji(league):
    return f"{LEAGUE_EMOJI.get(league, '')} {league}"

def strip_emoji(label):
    for league in LEAGUE_EMOJI:
        if label == with_emoji(league):
            return league
    return label

# Main
def main():
    st.set_page_config(page_title="Stadium Finder", page_icon="🏟️", layout="centered")
    st.title("🏟️ Sports Stadiums Finder")
    st.caption("Pick a team or enter an address to find the nearest venues in every league.")

    # Load data
    try:
        lg = load_all_leagues()
    except FileNotFoundError as e:
        st.error(f"Could not load stadium data: {e}")
        st.stop()

    # Session state init
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'ref_team' not in st.session_state:
        st.session_state.ref_team = None
    if 'ref_row' not in st.session_state:
        st.session_state.ref_row = None
    if 'mode' not in st.session_state:
        st.session_state.mode = "Team"
    if 'selected_leagues' not in st.session_state:
        st.session_state.selected_leagues = OTHER_LEAGUE_ORDER
    if 'n' not in st.session_state:
        st.session_state.n = 1
    if 'ref_address_location' not in st.session_state:
        st.session_state.ref_address_location = ''

    # Mode selector
    mode = st.radio("Search by", ["Team", "Address"], horizontal=True)

    if mode == "Address":
        st.markdown("#### 📍 Enter your location")
        addr_col1, addr_col2 = st.columns(2)
        with addr_col1:
            street  = st.text_input("Street Address", placeholder="e.g. 110 Smith Drive")
            city    = st.text_input("City", placeholder="e.g. Syracuse")
        with addr_col2:
            state   = st.text_input("State", placeholder="e.g. NY")
            zipcode = st.text_input("Zip Code", placeholder="e.g. 13210")

        n_input = st.slider("Closest teams per league", min_value=1, max_value=32, value=st.session_state.n)
        st.markdown("#### ⛹ Pick leagues")
        selected_leagues_input_raw = st.multiselect(
            "Show leagues",
            options=[with_emoji(l) for l in OTHER_LEAGUE_ORDER],
            default=[with_emoji(l) for l in st.session_state.selected_leagues]
        )
        selected_leagues_input = [strip_emoji(l) for l in selected_leagues_input_raw]
        run = st.button("Find closest stadiums", type="primary")

        if run:
            st.session_state.n = n_input
            st.session_state.selected_leagues = selected_leagues_input

            parts = [p.strip() for p in [street, city, state, zipcode] if p.strip()]
            ref_label = ", ".join(parts)
            st.session_state.ref_address_location = ", ".join(p.strip() for p in [city, state] if p.strip())
            ref_lat, ref_lon = None, None

            full_address = ", ".join(p.strip() for p in [street, city, state, zipcode] if p.strip())
            ref_lat, ref_lon = google_geocode(full_address)

            if ref_lat is None:
                geolocator = Nominatim(user_agent="stadium_finder")
                attempts = [
                    f"{street}, {city}, {state} {zipcode}".strip(),
                    f"{street}, {city}, {state}".strip(),
                    f"{city}, {state} {zipcode}".strip(),
                    f"{city}, {state}".strip(),
                ]
                attempts = [", ".join(p.strip() for p in a.split(",") if p.strip()) for a in attempts]
                for attempt in attempts:
                    try:
                        loc = geolocator.geocode(attempt, country_codes='us')
                        if loc is not None:
                            ref_lat = loc.latitude
                            ref_lon = loc.longitude
                            break
                    except Exception as e:
                        st.error(f"Geocoding error: {e}")
                        st.stop()

            if ref_lat is None:
                st.error("Address not found. Try using a nearby major city, or check your spelling.")
                st.stop()

            df = lg.copy()
            df['distance_mi'] = haversine_vectorized(ref_lat, ref_lon, df['lat'], df['lon'])

            results = (
                df.sort_values('distance_mi')
                .groupby('league')
                .head(n_input)
                .reset_index(drop=True)
            )
            results['league'] = pd.Categorical(results['league'], categories=LEAGUE_ORDER, ordered=True)
            results = results.sort_values(['league', 'distance_mi'])

            st.session_state.results  = results
            st.session_state.ref_team = (ref_label, "Address")
            st.session_state.ref_row  = pd.DataFrame([{
                'lat': ref_lat, 'lon': ref_lon, 'venue': ref_label, 'league': 'Address'
            }])
            st.session_state.mode = "Address"

    else:
        st.markdown("#### 🏟️ Pick a team")
        col1, col2 = st.columns(2)
        with col1:
            league = strip_emoji(st.selectbox(
                "League",
                [with_emoji(l) for l in sorted(lg['league'].unique())]
            ))
        with col2:
            teams = sorted(lg.loc[lg['league'] == league, 'team'].tolist())
            team  = st.selectbox("Team", teams)

        n_input = st.slider("Closest teams per league", min_value=1, max_value=32, value=st.session_state.n)
        st.markdown("#### ⛹ Pick leagues")
        selected_leagues_input_raw = st.multiselect(
            "Show leagues",
            options=[with_emoji(l) for l in OTHER_LEAGUE_ORDER],
            default=[with_emoji(l) for l in st.session_state.selected_leagues]
        )
        selected_leagues_input = [strip_emoji(l) for l in selected_leagues_input_raw]
        run = st.button("Find closest stadiums", type="primary")

        if run:
            st.session_state.n = n_input
            st.session_state.selected_leagues = selected_leagues_input

            row = lg.loc[(lg['league'] == league) & (lg['team'] == team)]
            ref_lat = row['lat'].values[0]
            ref_lon = row['lon'].values[0]

            df = lg.copy()
            df['distance_mi'] = haversine_vectorized(ref_lat, ref_lon, df['lat'], df['lon'])

            other_leagues = (
                df[(df['league'] != league)]
                .sort_values('distance_mi')
                .groupby('league')
                .head(n_input)
                .reset_index(drop=True)
            )

            same_league = (
                df[(df['league'] == league) & (df['team'] != team)]
                .sort_values('distance_mi')
                .head(n_input - 1)
                .reset_index(drop=True)
            )

            results = pd.concat([other_leagues, same_league], ignore_index=True)
            results['league'] = pd.Categorical(results['league'], categories=LEAGUE_ORDER, ordered=True)
            results = results.sort_values(['league', 'distance_mi'])

            st.session_state.results  = results
            st.session_state.ref_team = (team, league)
            st.session_state.ref_row  = row
            st.session_state.mode     = "Team"

    # Display
    if st.session_state.results is not None:
        results    = st.session_state.results
        ref_row    = st.session_state.ref_row
        team_lbl, league_lbl = st.session_state.ref_team
        is_address = st.session_state.get('mode') == "Address"

        ref_lat = ref_row['lat'].values[0]
        ref_lon = ref_row['lon'].values[0]

        results = results[results['league'].isin(st.session_state.selected_leagues)]

        if is_address:
            st.subheader(f"Closest stadiums to **{team_lbl}**")
        else:
            st.subheader(f"Closest stadiums to the **{team_lbl}** ({league_lbl}), who play at {ref_row['venue'].values[0]}")

        coords       = list(zip(results['lat'], results['lon']))
        locations    = [format_location(l) for l in reverse_geocode_locations(coords)]
        if is_address:
            ref_location = st.session_state.get('ref_address_location', '')
        else:
            ref_location = format_location(reverse_geocode_locations([(ref_lat, ref_lon)])[0])

        if is_address:
            ref_display = pd.DataFrame([{
                'League':        '📍 You',
                'Team':          '—',
                'Venue':         team_lbl,
                'Location':      ref_location,
                'Distance (mi)': 0.0
            }])
        else:
            ref_display = pd.DataFrame([{
                'League':        league_lbl,
                'Team':          team_lbl,
                'Venue':         ref_row['venue'].values[0],
                'Location':      ref_location,
                'Distance (mi)': 0.0
            }])

        display_df = results[['league', 'team', 'venue', 'distance_mi']].copy()
        display_df.insert(3, 'Location', locations)
        display_df.columns = ['League', 'Team', 'Venue', 'Location', 'Distance (mi)']
        display_df = display_df.sort_values('Distance (mi)').reset_index(drop=True)
        display_df = pd.concat([ref_display, display_df], ignore_index=True)

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Distance (mi)": st.column_config.NumberColumn(format="%.1f mi")
            }
        )

        st.markdown("---")
        st.markdown("#### 🗺️ Map")

        m = fl.Map(tiles="OpenStreetMap")

        ref_color = LEAGUE_COLORS.get(league_lbl, 'gray')
        fl.Marker(
            location=[ref_lat, ref_lon],
            tooltip=f"{'📍' if is_address else '⭐'} {team_lbl}",
            popup=fl.Popup(f"<b>{team_lbl}</b><br>{ref_row['venue'].values[0]}", max_width=200),
            icon=fl.Icon(color=ref_color, icon='star', prefix='fa'),
        ).add_to(m)

        for _, r in results.iterrows():
            color = LEAGUE_COLORS.get(str(r['league']), 'gray')
            fl.Marker(
                location=[r['lat'], r['lon']],
                tooltip=f"{r['team']} ({r['league']}) — {r['distance_mi']} mi",
                popup=fl.Popup(
                    f"<b>{r['team']}</b><br>{r['venue']}<br><i>{r['league']}</i><br>{r['distance_mi']} mi",
                    max_width=200
                ),
                icon=fl.Icon(color=color, icon='home', prefix='fa'),
            ).add_to(m)

        all_lats = [ref_lat] + results['lat'].tolist()
        all_lons = [ref_lon] + results['lon'].tolist()
        m.fit_bounds(
            [[min(all_lats), min(all_lons)], [max(all_lats), max(all_lons)]],
            padding=(30, 30)
        )

        legend_html = """
        <div style="position:fixed;top:10px;right:10px;z-index:1000;font-size:13px;color:#333333;">
          <details style="background:white;padding:10px 14px;border-radius:8px;border:1px solid #ccc;">
            <summary style="cursor:pointer;font-weight:bold;color:#333333;">League Legend</summary>
            <br>
            <span style="color:gray">★</span> Selected Location<br>
            <span style="color:red">●</span> NBA &nbsp;
            <span style="color:green">●</span> NFL<br>
            <span style="color:blue">●</span> MLB &nbsp;
            <span style="color:orange">●</span> NHL<br>
            <span style="color:pink">●</span> MLS &nbsp;
            <span style="color:purple">●</span> WNBA
          </details>
        </div>
        """
        m.get_root().html.add_child(fl.Element(legend_html))
        st_folium(m, use_container_width=True, height=500)

if __name__ == "__main__":
    main()