import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('notes.csv')[:109]

df['date_event_st'] = pd.to_datetime(df['date_event_st'], format="%Y/%m/%d")
df['date_event_en'] = pd.to_datetime(df['date_event_en'], format="%Y/%m/%d")

# tili = 60.43, osso = 59.25, ozer = 57.65, nico = 55.20, semy = 54.2, petr = 53.05, vodo = 51.82

station_order = ["tili", "osso", "ozer", "nks", "semy", "pet", "vod"][::-1]
df['name'] = pd.Categorical(df['name'], categories=station_order, ordered=True)
df.sort_values(by='name', inplace=True)

color_map = {'0': 'blue', '1': 'orange'}
df['color'] = df['lowhigh'].map(color_map)
print(df)

fig, ax = plt.subplots(figsize=(10, 4))

for _, row in df.iterrows():
    ax.plot([row['date_event_st'], row['date_event_en']], [row['name'], row['name']], color=row['color'], linewidth=20, alpha=0.5)

ax.set_xlabel('Time')
ax.set_ylabel('Station Name')

plt.savefig("map.png", dpi=300, bbox_inches="tight")
plt.show()
