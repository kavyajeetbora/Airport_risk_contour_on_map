import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from shapely.geometry import Point, LineString
import geopandas as gpd
import folium
import geojsoncontour
import json
import branca
from tqdm import tqdm
import time


def convert_to_utm(x,y, epsg_code):
    '''
    Converts wgs84 coordinate system to utm coordinates.
    Takes the coordinates x,y in degrees and given the epsg code of the location.
    Note: epsg code shall be in this format: epsg:5243 and type shall be string
    '''
    point = gpd.GeoSeries([Point(x, y)],crs="epsg:4326").to_crs(epsg_code).values[0]
    return point.x,point.y

def calculate_risk_contours(runway, A, epsg_code, contour_config):
    '''
    Calculates the geometric likelihood of an accident due to flight takeoffs for a given runway
    
    Inputs
    --------
    A - Constants for airport 
    coordinates - location of start and end point of a runway
    DI - distance interval for contours
    DL - maximum distance of the contour to be plotted in meterms
    AI = interval for angles
    AL = maximum angle of the contour
    '''

    DI = contour_config["DI"] ## Distance interval
    DL = contour_config["DL"] ## Distance Limit
    AI = contour_config["AI"] ## Angle interval 
    AL = contour_config["AL"] ## Angle Limit
    
    ## 1. Extract the coordinates from user input
    x1,y1 = runway["A"]
    x2,y2 = runway["B"]
    P = runway["P"]
        
    ## 2. Line string for the runway
    runway = LineString([Point(x1,y1), Point(x2,y2)]) 
    
    ## 3. Convert the coordinates of the airport runway to utm:
    x1_utm, y1_utm = convert_to_utm(x1,y1, epsg_code=f"epsg:{epsg_code}")
    x2_utm, y2_utm = convert_to_utm(x2,y2, epsg_code=f"epsg:{epsg_code}")
       
    ## 4. Find the direction of the airplane takoff w.r.t. geographical north
    slope = (y2_utm-y1_utm)/(x2_utm-x1_utm)
    a = np.degrees(np.arctan(slope))
    if a < 0: 
        a = 180 + a

    r = Point((x1,y1)).distance(Point((x2,y2)))
    
    ## 5. find the absolute direction of the takeoff
    dts = [0,180]
    distances = []
    for dt in dts:
        dx,dy = x1 + r*np.cos(np.radians(dt+a)), y1 + r*np.sin(np.radians(dt+a))
        distances.append(runway.distance(Point(dx,dy)))

    dt = dts[np.argmax(distances)]
    
    ## 6. Create the meshgrid with input values:
    radius = np.arange(0+DI,DL+DI,DI)
    angle = np.arange(-AL,AL+AI,AI)
    
    R,T = np.meshgrid(radius,angle)
    X = x1_utm + R*np.cos(np.radians(dt+a+T))
    Y = y1_utm + R*np.sin(np.radians(dt+a+T))    
    
    ## 7. Calculate the geometric risk due airplane takeoff
    Z = P * A["k"] * np.exp(-(R/A["r0"]+np.abs(T)/A["theta0"]))
    
    return X,Y,Z

def plot_airport_risk(airport_runways, contour_config):

    '''
    plots the risk union of multiple contours on an interactive map.

    INPUTS
    ----------
    1. runway's end to end coordinates 
    2. runway's location epsg code for utm coordinates
    3. contour config - maximum distance of the contour, max angle, distance and angle intervals
    4. project name (optional)

    OUTPUT
    ------
    1. interactive plot in html format containing the risk contours over an interactive map
    '''

    ## 1. INITIAL INPUTS FOR LEGEND
    ## ------------------------------------------

    print("Initializing the inputs for legend....")
    L1,L2 = 3,10
    values = [10**-i for i in range(L1,L2)][::-1]
    colors = ['black', 'darkgreen', 'yellow', 'red', 'purple', 'cyan']
    color_dict = {}
    for level,c in zip(range(-(L2-1),-L1,1), colors):
        color_dict[level]=c

    labels = [-1*int("{:.0e}".format(x).split("e-0")[1]) for x in values]
    print("Done")

    ## 2. Create the individual plots for each runways and convert them to geodataframe
    ## ----------------------------------------------------------------------------------
    print('Plotting the contour maps for given runways...')

    gdfs = []    
    for r, runway in tqdm(airport_runways["runways"].items(), unit=" Runway"):
        ## Calculate the contour matrix
        X,Y,Z = calculate_risk_contours(runway, airport_runways["A"], airport_runways["epsg"], contour_config)
        ## plot the contour
        contour_utm = plt.contourf(X,Y,Z, levels=values, colors=colors, vmin=min(values), vmax=max(values))
        ## Convert the contour to geojson then to geodataframe
        geojson = geojsoncontour.contourf_to_geojson(contourf=contour_utm)
        geojson = json.loads(geojson)
        gdf = gpd.GeoDataFrame.from_features(geojson, crs=f"epsg:{airport_runways['epsg']}")
        gdf["title"] = [x for x in range(-(L2-1),-L1,1)]
        gdf.drop(["stroke","stroke-opacity","stroke-width"], axis=1, inplace=True)
        gdfs.append(gdf)

    print("Done")

    ## 3. Compute the union of the all the contours of each runways 
    ## ----------------------------------------------------------------------------------

    print("Superimposing all the contours and determining the union...")
    while len(gdfs) != 1:
        gdfs[0] = gpd.overlay(gdfs[0], gdfs[1], how="union", keep_geom_type=True)
        gdfs[0]['title'] = np.max(gdfs[0][["title_1","title_2"]].fillna(-99).values, axis=1)
        gdfs[0]["fill"] = gdfs[0]["title"].apply(lambda x: color_dict[x])
        gdfs[0] = gdfs[0][["geometry", "title", "fill"]]
        del gdfs[1]
    
    final_gdf = gdfs[0].to_crs("epsg:4326")

    ## convert the geodataframe to geojson for plotting
    geojson = json.loads(final_gdf.to_json())

    print("Done")


    ## 4. Plot the union of contour on an interactive map and also add the legend 
    ## ----------------------------------------------------------------------------------
    print("Plotting the resultant contours on interactive map...")
    center_coordinates = list(airport_runways["runways"].values())[0]["A"][::-1]

    ## 4.1 Create the basemap
    contour_map = folium.Map(center_coordinates, zoom_start=12, tiles="OpenStreetMap")

    ## 4.2 Add the contour to the base map
    folium.GeoJson(
        geojson,
        style_function=lambda x: {
            'color':     x['properties']['fill'],
            'opacity':   1,
            'weight': 0
        }
    ).add_to(contour_map)

    ## 4.3 Add the legend for the interactive map
    colormap = branca.colormap.LinearColormap(
        colors=colors,
        vmin=min(labels),vmax=max(labels)
    ).to_step(
        len(colors),
        index=labels
    )

    colormap.caption = "Geometric Risk in 10 to the power:"
    contour_map.add_child(colormap)
    print("Done")

    ## save the map with the given project name
    contour_map.save(f"{airport_runways['title']}.html")
    print("Saved the interactive map successfully")

    return contour_map       

    