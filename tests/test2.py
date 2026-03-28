import json
import numpy as np
import pandas as pd

def load_league(filepath, list_key, team_col, lat_col, lon_col, league_name):
    """Load a league JSON file and normalize it into a standard DataFrame."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    df = pd.json_normalize(data[list_key])
    df = df.rename(columns={
        lat_col: 'lat',
        lon_col: 'lon',
        team_col: 'team'
    })
    df['league'] = league_name
    return df[['league', 'team', 'lat', 'lon']]

# Load each league - adjust parameters to match each file's structure
nba = load_league('stadiumdata/nba_stadiums.json', 'venues', 'team', 'coordinates.latitude', 'coordinates.longitude', 'NBA')
nfl = load_league('stadiumdata/nfl_stadiums.json', 'venues', 'team', 'coordinates.latitude', 'coordinates.longitude', 'NFL')
mlb = load_league('stadiumdata/mlb_stadiums.json', 'venues', 'team', 'coordinates.latitude', 'coordinates.longitude', 'MLB')
nhl = load_league('stadiumdata/nhl_stadiums.json', 'venues', 'team', 'coordinates.latitude', 'coordinates.longitude', 'NHL')
mls = load_league('stadiumdata/mls_stadiums.json', 'venues', 'team', 'coordinates.latitude', 'coordinates.longitude', 'MLS')
wnba = load_league('stadiumdata/wnba_stadiums.json', 'venues', 'team', 'coordinates.latitude', 'coordinates.longitude', 'WNBA')

# Combine all leagues into one DataFrame
lg = pd.concat([nba, nfl, mlb, nhl, mls, wnba], ignore_index=True)

# Vectorized haversine distance
def haversine_vectorized(lat1, lon1, lat2, lon2):
    R = 3958.8  # Earth's radius in miles
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
    return np.round(2 * R * np.arcsin(np.sqrt(a)), 3)

# Ask user for a reference NFL team
lg_name = input("Enter a league (NBA, NFL, MLB, NHL, MLS, WNBA): ")
team_name = input(f"Enter the {lg_name} team name: ")
head_num = input("How many closest teams to show per league? (hit enter for 1): ")
if head_num == "":
    head_num = 1
else:
    head_num = int(head_num)

row = lg.loc[(lg['team'] == team_name) & (lg['league'] == lg_name)]

if row.empty:
    print(f"Team '{team_name}' not found. Check spelling and try again.")
else:
    ref_lat = row['lat'].values[0]
    ref_lon = row['lon'].values[0]

    lg['distance'] = haversine_vectorized(ref_lat, ref_lon, lg['lat'], lg['lon'])

    print(f"\nClosest teams to {team_name} by league:")
    results = (
        lg[['league', 'team', 'distance']]
        .sort_values('distance')
        .groupby('league')
        .head(1)
        .sort_values(['league', 'distance'])
    )
    for league, group in results.groupby('league'):
        if league != lg_name:
            print(f"\n{league}")
            print(group[['team', 'distance']].to_string(index=False))

