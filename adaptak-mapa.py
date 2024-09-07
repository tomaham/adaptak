import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
#from pyproj import Transformer

#transformer = Transformer.from_crs("EPSG:5514", "EPSG:4326", always_xy=True)

gdf = pd.read_csv("gastroWithCoords.csv").fillna("")

gdf['tags'] = gdf['Tagy'].apply(lambda x: [tag.strip().lower() for tag in x.split(',')])
all_tags = sorted(set([tag for sublist in gdf['tags'] for tag in sublist]))


#st.write(all_tags)

gdf['lon'] = gdf['lon'].astype(float)
gdf['lat'] = gdf['lat'].astype(float)
gdf['poznámka'] = gdf['poznámka'].astype(str)

brno_coords = [49.2000, 16.6100] # center

##################################################################################

st.title("Adapťák mapy")
st.write("Kde se dá kolem najíst a napít?")


# Display the folium map using the st_folium component



c1, c2 = st.columns([5, 2])

selected_tags = c1.multiselect("Výběrem zúžíte zobrazené", all_tags,
                               help='Jestli trochu víte, co (ne) chcete ...')

if selected_tags:
    df_filtered = gdf[gdf['tags'].apply(lambda tags: all(tag in tags for tag in selected_tags))]
else:
    df_filtered = gdf

rrecommend = df_filtered.sample(n=1)

name = rrecommend.iloc[0]['podniky']
tags = rrecommend.iloc[0]['Tagy']
note = "<br> <br>".join(gdf[gdf['podniky'] == name]['poznámka'].tolist())
people = "<br>".join(gdf[gdf['podniky'] == name]['zaměstnanci'].tolist())

c2.markdown("**Náhodně doporučujeme**")
c2.markdown("## "+name+"")
c2.markdown('*'+tags+"*")
c2.html("<div>"+note+"</div>")
c2.html("<div style='font-size:80%;'>"+people+"</div>")

# Create a folium map centered on Brno
m = folium.Map(location=brno_coords, zoom_start=14)

marker_info = {}
for id, row in df_filtered.iterrows():
    if row['lon'] != 0:
        # st.write(row['podniky'],row['yy'],row['xx'])
        popup = "<div>" + row['podniky'] + "<a target='_' href='" + row['Mapa'] + "'> M </a></div>"

        if row['podniky'] == name:
              color = 'red'
        else:
              color = 'blue'
        #color='blue'

        marker = folium.Marker(
            location=[row['lat'], row['lon']],
            popup=popup,
            icon=folium.Icon(color=color),
            tooltip="Klikněte pro další info"
        ).add_to(m)
        # st.write(row['lat'],row['lon'])

        marker_info[str(marker)] = popup
    else:
        pass
        # st.write(id)
        # marker.add_to(m)


with c1:
    map_object = st_folium(m, width=725, returned_objects=[]) #  width=725
#st.write("Popup:", map_object["last_object_clicked_popup"])
#st.write("Tooltip:", map_object["last_object_clicked_tooltip"])





#st.write(marker_info)

# Check if a marker was clicked, and display information
#if map_object is not None and map_object['last_object_clicked'] is not None:
#    # Get the name of the clicked marker and retrieve the corresponding description
##    clicked_marker = str(map_object['last_object_clicked'])
#    description = marker_info.get(clicked_marker, "No description available.")
#    st.write(f"**POI Description:** {description}")



