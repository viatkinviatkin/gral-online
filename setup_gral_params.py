from flask import Flask, request, jsonify, render_template
import os
import csv
from itertools import islice


DIR = os.path.dirname(__file__) #<-- absolute dir the script is in
COMPUTATION_DIR = os.path.join(DIR, 'tesproj/Computation/')
ARGS = {
    'source': {
        'x':552,
        'y':-325,
        'z':10,
        'H2S[kg/h]':2
    },
    'gral_domain': {
        'north':-280,
        'west': 480,
        'south':-380,
        'east':650
    }
}


def setup_params(arguments = None):
    source = os.path.join(COMPUTATION_DIR, 'point.dat')
    gral = os.path.join(COMPUTATION_DIR, 'gral.geb')
    arguments = ARGS
    # Читаем данные и модифицируем их
    with open(source, mode='r+', newline='') as file:
        keys = 'x,y,z,H2S[kg/h],--,--,--,exit vel.[m/s],diameter[m],Temp.[K],Source group,deposition parameters F2.5, F10,DiaMax,Density,VDep2.5,VDep10,VDepMax,Dep_Conc\n'
        default_values = '0,0,0,0,0,0,0,0,0.2,273,1,0,0,0,0,0,0,0,0'
        
        file.write('Useless header for gral\n') 
        file.write(keys)
        
        values = default_values.split(',')
        for i, key in enumerate(keys.split(',')):
            if not arguments['source'].get(key):
                continue
            
            values[i] = str(arguments['source'].get(key))
            
        file.write(','.join(values)+ '\n')
        
        # Обрезаем файл, если новые данные короче старых
        file.truncate()
    
    with open(gral, mode='r+', newline='') as file:   
        west = arguments['gral_domain'].get('west')
        east = arguments['gral_domain'].get('east')
        south = arguments['gral_domain'].get('south')
        north = arguments['gral_domain'].get('north')
         
        file.write(f'''10               !cell-size for cartesian wind field in GRAL in x-direction
10               !cell-size for cartesian wind field in GRAL in y-direction
2,1.01                !cell-size for cartesian wind field in GRAL in z-direction, streching factor for increasing cells heights with height
{round((east-west)/10)}            !number of cells for counting grid in GRAL in x-direction
{round((north-south)/10)}           !number of cells for counting grid in GRAL in y-direction
1                !Number of horizontal slices
1,                !Source groups to be computed seperated by a comma
{west}                !West border of GRAL model domain [m]
{east}                !East border of GRAL model domain [m]
{south}                !South border of GRAL model domain [m]
{north}                !North border of GRAL model domain [m]
''')
        file.truncate()
def customize(generator):
    for row in generator:
        row['a'] = int(row['a'])
        row['b'] = float(row['b']) * 100
        row['c'] = int(row['c'])
        yield row    
setup_params()