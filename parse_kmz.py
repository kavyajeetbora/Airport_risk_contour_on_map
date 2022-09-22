from zipfile import ZipFile
from lxml import html
from shapely.geometry import Point, LineString

def extract_polygon(filename):
    '''
    Parses a google earth kmz file and looks for coordinates of polygon type
    then converts the coodinates to a shapely linestring file and returns it
    '''
    ## open the kmz file to disk
    try:
        with ZipFile(filename, 'r') as kmz:
            kml = kmz.open(kmz.filelist[0].filename, 'r').read()

    except FileNotFoundError as f:
        print("Invalid file")

    ## Read and extract the polygon coordinates in the kmz file:
    tree = html.fromstring(kml)
    polygon_text = tree.xpath("//coordinates/text()")[0].strip()
    polygon_text = polygon_text.replace(",0","") ## clean the polygon coordinates

    ## 
    points = []
    for txt in polygon_text.split(" "):
        long,lat = txt.split(",")
        points.append(Point(float(long),float(lat)))

    polygon = LineString(points)

    return polygon

