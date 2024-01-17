# Import Libraries
import pandas as pd
import geopandas
import folium
import branca.colormap as cm
from shapely.geometry import Point
import numpy as np
import asyncio
import pathlib
from pyppeteer import launch
import nest_asyncio
import os


def plot_setores_in_map(gdf, map):
    """Given a GeoDataFrame with a column named 'GEOMETRIA' and rows that represent Setores, add the polygons to map

    Parameters
    ----------
    gdf : GeoDataFrame
        _description_
    map : folium.Map
        _description_
    """
    for _, r in gdf.iterrows():
        geo_j = folium.GeoJson(data=r['GEOMETRIA'], style_function=lambda x: {"color": 'black', "weight": 1,"fillColor": 'grey', "fillOpacity": 0.4})
        geo_j.add_to(map)


def plot_markers_in_map(map, geometria_fichas, inside_icon='home'):
    """ Adicionar no mapa os pontos definidos na coluna latlong de geometria_fichas com um marcador que contem o simbolo inside_icon

    Parameters
    ----------
    map : _type_
        _description_
    geometria_fichas : _type_
        _description_
    inside_icon : str, optional
        _description_, by default 'home'
    """
    if inside_icon =='pav':
        cmap = cm.LinearColormap(['#c2e0b6', '#0e4120'], 
                                    vmin=geometria_fichas['NPVTO_CSA'].min(), 
                                    vmax=geometria_fichas['NPVTO_CSA'].max())
        cmap.caption = 'Número de Pavimentos'
        svg_style = '<style>svg#legend {font-size: 14px; background-color: white;}</style>'
        # map.get_root().html.add_child(folium.Element(svg_style))
        # cmap.add_to(map)
        
    for _, r in geometria_fichas.iterrows():
        
        icons = {'child': 'child',
                 'old': 'person-cane',
                 'probl': 'triangle-exclamation',
                 'acab': 'star',
                 'pav': 'building',
                 'pcd': 'wheelchair'}
        
        # .YlGn.to_step(9).scale(geometria_fichas['NPVTO_CSA'].min(), geometria_fichas['NPVTO_CSA'].max())
        
        cor=r['COR']
        if inside_icon == 'home':
            home_icon = f'<i class="fa fa-{inside_icon}" aria-hidden="true" style="position:absolute; color:white; font-size:7pt; padding:0; margin:0;top:3px;left:3px"></i>'
            set_icon = 'map-marker'
        elif inside_icon == 'pav':
            cor = cmap(r['NPVTO_CSA'])
            home_icon = ''
            set_icon = icons[inside_icon]
        else:
            home_icon = ''
            set_icon = icons[inside_icon]
            
        marker_icon = f'<i class="fa fa-{set_icon}" style="position:relative; font-size:20pt; color:{cor};">{home_icon}</i>'
        outline_icon = f'<i class="fa fa-{set_icon}" style="position:relative; font-size:21pt; color:black;"></i>'
        # icon = plugins.BeautifyIcon(prefix='fa', icon="child", icon_shape="marker", background_color=cor, border=1, border_color='black')
        divicon = folium.DivIcon(icon_anchor=(7,22), html=f'<div style="background-color: transparent; ">{marker_icon}</div>')
        
        
        my_marker = folium.Marker(icon=divicon)
        border_marker = folium.Marker(icon=folium.DivIcon(icon_anchor=(8,23), html=f'<div style="background-color: transparent; ">{outline_icon}</div>'))
        
        geo_j = folium.GeoJson(data=r['latlong'], marker=my_marker)
        geo_j2 = folium.GeoJson(data=r['latlong'], marker=border_marker)
        # folium.Marker(location=[r['GPS_LAT_FICHA'], r['GPS_LONG_FICHA']], icon=icon).add_to(my_map2)
        # folium.Marker(location=[r['GPS_LAT_FICHA'], r['GPS_LONG_FICHA']], icon=divicon).add_to(my_map2)
        
        geo_j2.add_to(map)
        geo_j.add_to(map)

def create_latlong_col(df, lat_col='GPS_LAT_FICHA', long_col='GPS_LONG_FICHA'):
    
    list_latlong = []
    for _, r in df.iterrows():
        list_latlong.append(Point(r[long_col], r[lat_col]))
    df['latlong'] = list_latlong
    
def map_markers_in_sections(setores_gdf, geometria_fichas, icon='home', save=False, save_path=''):
    
    my_map2 = folium.Map(location=[setores_gdf["centroid"].y.mean(), setores_gdf["centroid"].x.mean()], tiles="cartodb positron")
    # define zoom
    bounds = setores_gdf['geometry'].total_bounds
    my_map2.fit_bounds([[bounds[1],bounds[0]],[bounds[3], bounds[2]]])

    plot_setores_in_map(setores_gdf, my_map2)
    plot_markers_in_map(my_map2, geometria_fichas, inside_icon=icon)
    
    if save:
        my_map2.save(f'{save_path}.html')
        
    return my_map2

def html_to_png(html_file, png_file):
    
    nest_asyncio.apply()
    
    async def generate_pdf(url, png_path):
        browser = await launch({'defaultViewport': {'width':1440,'height':900}})
        page = await browser.newPage()
        
        await page.goto(url)
        await page.screenshot({'path': png_path, 'width':2880, 'height':1800}, clip={'x':0, 'y':100, 'width':1440, 'height':700})
        
        await browser.close()

    # Run the function
    
    url_path = pathlib.Path(html_file).as_uri()
    asyncio.get_event_loop().run_until_complete(generate_pdf(url_path, png_file))

def process_map_data(mapa_uma_area):
    
    # filter interesting columns
    area_df = mapa_uma_area.loc[:, ("ID_MAPA", "RHD_NOME", "RHD_SIGLA", "RHD_SETOR", "RHD_GRAU", "GEOMETRIA", "CENTRO_LAT", "CENTRO_LONG", "COR")]
    
    # transform geoJSON (in "GEOMETRIA") into a Polygon from geopandas
    area_df = area_df.reset_index(drop=True)
    gdf = geopandas.GeoDataFrame()
    for i, g in enumerate(area_df['GEOMETRIA']):
        row = geopandas.read_file(g, driver='GeoJson')
        gdf = pd.concat([gdf, row])

    gdf = gdf.reset_index(drop=True)
    area_df['geometry']=gdf
    
    # make it in a GeoDataFrame and create centroid points
    new_gdf = geopandas.GeoDataFrame(area_df)
    # new_gdf.plot()
    new_gdf["centroid"] = new_gdf.centroid.to_crs(epsg=4326)
    
    return new_gdf

def generate_mapa_setores(new_gdf, map_path = 'mapa_setores', regenerate=True):
    
    if not regenerate and os.path.exists(map_path):
        return map_path
    
    # Generate map with colored sectors and labels

    my_map = folium.Map(location=[new_gdf["centroid"].y.mean(), new_gdf["centroid"].x.mean()], tiles="cartodb positron")

    # set zoom acording to boundaries
    bounds = new_gdf['geometry'].total_bounds
    my_map.fit_bounds([[bounds[1],bounds[0]],[bounds[3], bounds[2]]])

    num_points=1000 # used to find best placement of label
    for _, r in new_gdf.iterrows():
        
        cor=r['COR']
        geo_j = folium.GeoJson(data=r['GEOMETRIA'], style_function=lambda x, fillColor=cor: {"color": 'black', "fillColor": fillColor, "fillOpacity": 1})
        
        
        random_points = [Point(np.random.uniform(r['geometry'].bounds[0], r['geometry'].bounds[2]), np.random.uniform(r['geometry'].bounds[1], r['geometry'].bounds[3]))
                        for _ in range(num_points)]
        inside_points = [point for point in random_points if r['geometry'].contains(point)]
        
        if inside_points:
            max_distance_point = max(inside_points, key=lambda p: r['geometry'].boundary.distance(p))
            folium.Marker(location = [max_distance_point.y, max_distance_point.x], icon=folium.DivIcon(icon_size=(5,5), icon_anchor=(10,10),html=f'<div style="font-size:14pt; font-color:black; font-weight:bold">{r["RHD_GRAU"]}</div>')).add_to(geo_j)
        geo_j.add_to(my_map)

    my_map.save(f'{map_path}.html')
    
    map_file=f'{map_path}.html'
    output_png = f'{map_path}.png'
    html_to_png(map_file, output_png)
    
    return output_png

def generate_points_mapa(new_gdf, geometria_fichas, map_path='mapa', icon='home', regenerate=True):
    
    if not regenerate and os.path.exists(map_path):
        return map_path
    
    # join data to get forms from specific area and colors associated with sectors

    # create map for moradias
    create_latlong_col(geometria_fichas, lat_col = 'GPS_LAT_FICHA', long_col = 'GPS_LONG_FICHA')
    map_markers_in_sections(new_gdf, geometria_fichas, save=True, save_path=map_path, icon=icon)
    
    map_file=f'{map_path}.html'
    output_png = f'{map_path}.png'
    html_to_png(map_file, output_png)
    
    return output_png