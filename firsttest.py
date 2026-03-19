import json
import numpy as np
import pandas as pd

# Load JSON
with open('stadiumdata/nba_stadiums.json', 'r') as f:
    data = json.load(f)

# Flatten nested coordinates into columns
df = pd.json_normalize(data['venues'])
df = df.rename(columns={
    'state_province': 'state',
    'coordinates.latitude': 'lat',
    'coordinates.longitude': 'lon'
})

# Basic access patterns

teams = df[['team', 'lat', 'lon']]

# Vectorized haversine distance
def haversine_vectorized(lat1, lon1, lat2, lon2):
    R = 3958.8  # Earth's radius in miles
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
    return np.round(2 * R * np.arcsin(np.sqrt(a)), 3)

# Ask user for a reference team
team_name = input("Enter an NBA team name: ")
row = df.loc[df['team'] == team_name]

if row.empty:
    print(f"Team '{team_name}' not found. Check spelling and try again.")
else:
    ref_lat = row['lat'].values[0]
    ref_lon = row['lon'].values[0]

    df['miles_from_ref'] = haversine_vectorized(ref_lat, ref_lon, df['lat'], df['lon'])

    print(f"\nDistances from {team_name}:")
    print()
    print(df[['team', 'arena', 'state', 'city', 'miles_from_ref']].sort_values('miles_from_ref').head(5).to_string(index=False))