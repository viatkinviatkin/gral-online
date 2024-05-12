from pyproj import Transformer, Proj, CRS

import json

wkt ='''
PROJCRS["GSK-2011 / Gauss-Kruger zone 7",
    BASEGEOGCRS["GSK-2011",
        DATUM["Geodezicheskaya Sistema Koordinat 2011",
            ELLIPSOID["GSK-2011",6378136.5,298.2564151,
                LENGTHUNIT["metre",1]]],
        PRIMEM["Greenwich",0,
            ANGLEUNIT["degree",0.0174532925199433]],
        ID["EPSG",7683]],
    CONVERSION["6-degree Gauss-Kruger zone 7",
        METHOD["Transverse Mercator",
            ID["EPSG",9807]],
        PARAMETER["Latitude of natural origin",0,
            ANGLEUNIT["degree",0.0174532925199433],
            ID["EPSG",8801]],
        PARAMETER["Longitude of natural origin",39,
            ANGLEUNIT["degree",0.0174532925199433],
            ID["EPSG",8802]],
        PARAMETER["Scale factor at natural origin",1,
            SCALEUNIT["unity",1],
            ID["EPSG",8805]],
        PARAMETER["False easting",7500000,
            LENGTHUNIT["metre",1],
            ID["EPSG",8806]],
        PARAMETER["False northing",0,
            LENGTHUNIT["metre",1],
            ID["EPSG",8807]]],
    CS[Cartesian,2],
        AXIS["northing (X)",north,
            ORDER[1],
            LENGTHUNIT["metre",1]],
        AXIS["easting (Y)",east,
            ORDER[2],
            LENGTHUNIT["metre",1]],
    USAGE[
        SCOPE["Topographic mapping (medium scale)."],
        AREA["Russian Federation - onshore 36°E to 42°E"],
        BBOX[41.43,36,69.23,42]]]
'''

# Создание объекта CRS из WKT определения
crs_gsk2011 = CRS.from_string(wkt)
crs_3857  = CRS.from_string('''PROJCRS["WGS 84 / Pseudo-Mercator",
    BASEGEOGCRS["WGS 84",
        DATUM["World Geodetic System 1984",
            ELLIPSOID["WGS 84",6378137,298.257223563,
                LENGTHUNIT["metre",1]]],
        PRIMEM["Greenwich",0,
            ANGLEUNIT["degree",0.0174532925199433]],
        ID["EPSG",4326]],
    CONVERSION["Popular Visualisation Pseudo-Mercator",
        METHOD["Popular Visualisation Pseudo Mercator",
            ID["EPSG",1024]],
        PARAMETER["Latitude of natural origin",0,
            ANGLEUNIT["degree",0.0174532925199433],
            ID["EPSG",8801]],
        PARAMETER["Longitude of natural origin",0,
            ANGLEUNIT["degree",0.0174532925199433],
            ID["EPSG",8802]],
        PARAMETER["False easting",0,
            LENGTHUNIT["metre",1],
            ID["EPSG",8806]],
        PARAMETER["False northing",0,
            LENGTHUNIT["metre",1],
            ID["EPSG",8807]]],
    CS[Cartesian,2],
        AXIS["easting (X)",east,
            ORDER[1],
            LENGTHUNIT["metre",1]],
        AXIS["northing (Y)",north,
            ORDER[2],
            LENGTHUNIT["metre",1]],
    USAGE[
        SCOPE["unknown"],
        AREA["World - 85°S to 85°N"],
        BBOX[-85.06,-180,85.06,180]],
    ID["EPSG",3857]]''')
# Создание экземпляра Transformer для конвертации координат из GSK-2011 в WGS84
transformer = Transformer.from_crs(crs_gsk2011, "EPSG:4326")


# Создание экземпляра Transformer для конвертации координат
##transformer = Transformer.from_proj('+proj=geocent +ellps=GSK2011 +units=m +no_defs +type=crs', '+proj=merc +a=6378137 +b=6378137 +lat_ts=0 +lon_0=0 +x_0=0 +y_0=0 +k=1 +units=m +nadgrids=@null +wktext +no_defs')



# TODO: чтение файла неправильное

# Чтение данных из файла

def tranform_method(id, file):
    with open(file, 'r') as file:
        lines = file.readlines()

    ncols = int(lines[0].split()[1])
    nrows = int(lines[1].split()[1])
    xllcorner = int(lines[2].split()[1])
    yllcorner = int(lines[3].split()[1])
    cellsize = int(lines[4].split()[1])

    # ncols         2376
    # nrows         1698
    # xllcorner     5810440
    # yllcorner     7538130
    # cellsize      10

    # Создание двумерного массива
    grid = []
    lines = lines[6:]
    lines.reverse()
    local_max = 0
    local_min = float("inf")

    for i in range(6, len(lines)):
        if i < 6: continue
   
        line_array = [float(item) for item in lines[i].split()]
   
        if sum(line_array) == 0:
            xllcorner += cellsize
            continue
   
        for j in range(len(line_array)):
            if line_array[j] == 0: continue
        
            cur_max = max(line_array)
            cur_min = min([num for num in line_array if num != 0])
            if cur_max > local_max: local_max = cur_max
        
            if cur_min < local_min: local_min = cur_min
            
            lon, lat = transformer.transform(xllcorner, yllcorner + j*cellsize)
            grid.append([lon, lat , line_array[j]])

        xllcorner += cellsize

        # Открываем файл для записи
    with open(f'{id}.json', 'w') as file:
        json.dump(grid, file)
