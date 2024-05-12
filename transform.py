from pyproj import Transformer, Proj, CRS

import json

# Создание экземпляра Transformer для конвертации координат из декартовой в географическую
transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326")

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
