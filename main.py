from typing import List, Tuple

from turfpy.measurement import boolean_point_in_polygon
from geojson import Point, Polygon, Feature


class UserVenue:
    ID_INDEX = 0
    LAT_INDEX = 1
    LONG_INDEX = 2

    @staticmethod
    def read_data(file_address, model_class):
        data = []
        with open(file_address, 'r') as file:
            for line in file.readlines()[2:]:
                record_data = [column.strip() for column in line.split("|")]
                not_standard = False
                for column in record_data:
                    if len(column) == 0:
                        not_standard = True
                if not_standard:
                    continue
                data.append(model_class(
                    identifier=int(record_data[UserVenue.ID_INDEX]),
                    lat=float(record_data[UserVenue.LAT_INDEX]),
                    long=float(record_data[UserVenue.LONG_INDEX]),
                ))
        return data


class User(UserVenue):
    def __init__(self, identifier, long, lat):
        self.identifier = identifier
        self.long = long
        self.lat = lat


class Venue(UserVenue):
    def __init__(self, identifier, long, lat):
        self.identifier = identifier
        self.long = long
        self.lat = lat


def limit_data_by_location(polygon_coords: List[List[Tuple]], model_records):
    polygon = Polygon(polygon_coords)
    result = []
    for record in model_records:
        if boolean_point_in_polygon(Feature(geometry=Point((record.long, record.lat))), polygon):
            result.append(record)
    return result


calgary_coords = [[
    (-114.325419, 51.214159),  # long, lat
    (-113.865366, 51.214159),
    (-113.865366, 50.847729),
    (-114.325419, 50.847729),
]]

users = User.read_data("users.dat", User)
calgary_users = limit_data_by_location(calgary_coords, users)
venues = User.read_data("venues.dat", User)
calgary_venues = limit_data_by_location(calgary_coords, venues)

print(f"total number of users: {len(users)}")
print(f"number of users in Calgary: {len(calgary_users)}")
print(f"total number of venues: {len(venues)}")
print(f"number of venues in Calgary: {len(calgary_venues)}")
