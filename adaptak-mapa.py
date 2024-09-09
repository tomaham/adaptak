import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import base64
from pathlib import Path
#from pyproj import Transformer

#transformer = Transformer.from_crs("EPSG:5514", "EPSG:4326", always_xy=True)

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded
def img_to_html(img_path, width=30):
    img_html = "<img width='"+str(width)+"' src='data:image/png;base64,{}' class='img-fluid'>".format(
      img_to_bytes(img_path)
    )
    return img_html


gdf = pd.read_csv("gastroWithCoords.csv").fillna("")

gdf['tags'] = gdf['Tagy'].apply(lambda x: [tag.strip().lower() for tag in x.split(',')])
all_tags = sorted(set([tag for sublist in gdf['tags'] for tag in sublist]))


#st.write(all_tags)

gdf['lon'] = gdf['lon'].astype(float)
gdf['lat'] = gdf['lat'].astype(float)
gdf['poznámka'] = gdf['poznámka'].astype(str)

brno_coords = [49.2000, 16.6100] # center

##################################################################################

if "wide" in st.query_params:
    layout = "wide"
else:
    layout = "centered"

st.set_page_config(page_title="Gastromapa (Reli Adapťák 2024)", layout=layout)  # page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None


st.title("Adapťák Gastro Mapa")
st.write("Kde se dá kolem najíst a napít?")


# Display the folium map using the st_folium component

c1, c2 = st.columns([5, 2])

selected_tags = c1.multiselect("Výběrem zúžíte zobrazené", all_tags,
                               help='Jestli trochu víte, co (ne) chcete ...')

if selected_tags:
    df_filtered = gdf[gdf['tags'].apply(lambda tags: all(tag in tags for tag in selected_tags))]
else:
    df_filtered = gdf


if len(df_filtered) == 0:
    st.write("V té kombinaci tagů neumíme nic najít :( Zkuste změnit filtr.")
else:

    rrecommend = df_filtered.sample(n=1)

    name = rrecommend.iloc[0]['podniky']
    tags = rrecommend.iloc[0]['Tagy']
    note = "<br> <br>".join(gdf[gdf['podniky'] == name]['poznámka'].tolist())
    people = "<br>".join(gdf[gdf['podniky'] == name]['zaměstnanci'].tolist())

    c2.markdown("**Náhodně doporučujeme**")
    #c2.image("285659_marker_map_icon.png", width=20)  # title="Tento podnik je v mapě zvýrazněný jako červený."

    c2.html("<h2 style='margin:0px;padding:0px;'> "+img_to_html('285659_marker_map_icon.png',width=20) + name + "</h2>")

    c2.markdown('*'+tags+"*")
    c2.html("<div>"+note+"</div>")
    c2.html("<div style='font-size:80%;'><span style='font-size:80%;'>Doporučují:</span><br>"+people+"</div>")

    # Create a folium map centered on Brno
    m = folium.Map(location=brno_coords, zoom_start=14)

    marker_info = {}
    for id, row in df_filtered.iterrows():
        if row['lon'] != 0:
            # st.write(row['podniky'],row['yy'],row['xx'])

            notes = gdf[gdf['podniky'] == row['podniky']]['poznámka'].tolist()
            people = gdf[gdf['podniky'] == row['podniky']]['zaměstnanci'].tolist()

            np = zip(notes, people)
            sequence = [x[0]+"<br><span style='font-size:80%;'>"+x[1]+"</span>" for x in np]

            popup = "<div><b>" + row['podniky'] + "</b>"
            popup += "<p><em>"+ row['Tagy'] +"</em></p>"
            popup += "<div>"+ "<p>".join(sequence) +"</div>"
            #popup += "<div>"+ notes +"</div>"
            if 'http' in row['URL']:
                popup += "<p><a target='_' href='"+row['URL']+"' title='Web podniku'>WWW</a>"
            popup += "&nbsp;&nbsp;&nbsp;<a target='_' title='Na Mapy.cz' href='" + row['Mapa'] + "'> <img width='15' height='15' src='https://mapy.cz/img/favicon/ms-icon-144x144.png?2.65.5'> </a></p>"
            popup += "</div>"

            if row['podniky'] == name:
                  color = 'red'
            else:
                  color = 'blue'
            #color='blue'

            marker = folium.Marker(
                location=[row['lat'], row['lon']],
                popup=folium.Popup(popup,max_width=300),
                icon=folium.Icon(color=color, icon=row['Icon'], prefix='fa'),
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



