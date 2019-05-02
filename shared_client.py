from abc import abstractmethod
from shared import *
import time
import requests
import random

# global variables
api_url = 'http://192.168.0.12:7000/{0}'
map_response = requests.get(api_url.format('map'))
world_map = map_response.json()
cell_length: int = world_map['cellLengthMillimeters']
refresh_rate_milliseconds: int = world_map['refreshRateMilliseconds']
start_row: int = world_map['startRow']
start_column: int = world_map['startColumn']
thresholdMillimeters = world_map['thresholdMillimeters']


def get_cell(row, column):
    cells = [c for c in world_map['cells'] if c['row'] == row and c['column'] == column]
    if len(cells) > 0:
        return cells[0]
    return None


def distance(current_row, current_column, trip_row,  trip_column):
    return abs(trip_column - current_column) + abs(trip_row - current_row)


def get_trip_location(trip: Trip):
    if trip:
        if trip.status == 'waiting':
            trip_row, trip_column = trip.start['row'], trip.start['column']
        elif trip.status == 'started':
            trip_row, trip_column = trip.end['row'], trip.end['column']
        else:
            trip_row, trip_column = None, None
    else:
        trip_row, trip_column = None, None
    return trip_row, trip_column

