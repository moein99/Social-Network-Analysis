from typing import List, Tuple

from turfpy.measurement import boolean_point_in_polygon
from geojson import Point, Polygon, Feature


class User:
    ID_INDEX = 0
    LAT_INDEX = 1
    LONG_INDEX = 2

    def __init__(self, identifier, long, lat):
        self.identifier = identifier
        self.long = long
        self.lat = lat

    def get_string(self):
        return f'{self.identifier} {self.lat} {self.long}'

    @staticmethod
    def create_from_raw_inputs(inputs):
        return User(
            identifier=int(inputs[User.ID_INDEX]),
            lat=float(inputs[User.LAT_INDEX]),
            long=float(inputs[User.LONG_INDEX]),
        )

    @staticmethod
    def read_users(file_addr):
        result = []
        with open(file_addr, 'r') as file:
            for line in file.readlines():
                inputs = line.split()
                result.append(User(
                    identifier=inputs[User.ID_INDEX],
                    long=inputs[User.LONG_INDEX],
                    lat=inputs[User.LAT_INDEX]
                ))
        return result


class Venue:
    ID_INDEX = 0
    LAT_INDEX = 1
    LONG_INDEX = 2

    def __init__(self, identifier, long, lat):
        self.identifier = identifier
        self.long = long
        self.lat = lat

    def get_string(self):
        return f'{self.identifier} {self.lat} {self.long}'

    @staticmethod
    def create_from_raw_inputs(inputs):
        return Venue(
            identifier=int(inputs[Venue.ID_INDEX]),
            lat=float(inputs[Venue.LAT_INDEX]),
            long=float(inputs[Venue.LONG_INDEX]),
        )

    @staticmethod
    def read_venues(file_addr):
        result = []
        with open(file_addr, 'r') as file:
            for line in file.readlines():
                inputs = line.split()
                result.append(Venue(
                    identifier=inputs[Venue.ID_INDEX],
                    long=inputs[Venue.LONG_INDEX],
                    lat=inputs[Venue.LAT_INDEX]
                ))
        return result


class Rating:
    USER_ID_INDEX = 0
    VENUE_ID_INDEX = 1
    RATE_INDEX = 2

    def __init__(self, user_id, venue_id, rate):
        self.user_id = user_id
        self.venue_id = venue_id
        self.rate = rate

    def get_string(self):
        return f'{self.user_id} {self.venue_id} {self.rate}'

    @staticmethod
    def create_from_raw_inputs(inputs):
        return Rating(
            user_id=int(inputs[Rating.USER_ID_INDEX]),
            venue_id=int(inputs[Rating.VENUE_ID_INDEX]),
            rate=int(inputs[Rating.RATE_INDEX]),
        )

    @staticmethod
    def read_ratings(file_addr):
        result = []
        with open(file_addr, 'r') as file:
            for line in file.readlines():
                inputs = line.split()
                result.append(Rating(
                    user_id=inputs[Rating.USER_ID_INDEX],
                    venue_id=inputs[Rating.VENUE_ID_INDEX],
                    rate=inputs[Rating.RATE_INDEX]
                ))
        return result


class Checkin:
    ID_INDEX = 0
    USER_ID_INDEX = 1
    VENUE_ID_INDEX = 2
    LAT_INDEX = 3
    LONG_INDEX = 4
    CREATED_AT_INDEX = 5

    def __init__(self, identifier, user_id, venue_id, long, lat, created_at):
        self.identifier = identifier
        self.user_id = user_id
        self.venue_id = venue_id
        self.long = long
        self.lat = lat
        self.created_at = created_at

    def get_string(self):
        return f'{self.identifier} {self.user_id} {self.venue_id} {self.lat} {self.long} {self.created_at}'

    @staticmethod
    def create_from_raw_inputs(inputs):
        return Checkin(
            identifier=int(inputs[Checkin.ID_INDEX]),
            user_id=int(inputs[Checkin.USER_ID_INDEX]),
            venue_id=int(inputs[Checkin.VENUE_ID_INDEX]),
            lat=float(inputs[Checkin.LAT_INDEX]),
            long=float(inputs[Checkin.LONG_INDEX]),
            created_at=inputs[Checkin.CREATED_AT_INDEX],
        )


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
            data.append(model_class.create_from_raw_inputs(inputs=record_data))
    return data


def limit_data_by_location(polygon_coords: List[List[Tuple]], model_records):
    polygon = Polygon(polygon_coords)
    result = []
    for record in model_records:
        if boolean_point_in_polygon(Feature(geometry=Point((record.long, record.lat))), polygon):
            result.append(record)
    return result


def limit_records_by_user_venue(records, users, venues):
    user_ids = set([user.identifier for user in users])
    venues_ids = set([venue.identifier for venue in venues])
    result = []
    for record in records:
        if record.user_id in user_ids and record.venue_id in venues_ids:
            result.append(record)
    return result


def store_records(records, file_address):
    with open(file_address, 'w') as file:
        for record in records:
            file.write(f'{record.get_string()}\n')


def clean_data():
    san_francisco_coords = [[
        (-122.553454, 37.812965),
        (-122.359602, 37.817252),
        (-122.346337, 37.708571),
        (-122.523607, 37.708332)
    ]]

    place_name = "San Francisco"

    users = read_data("users.dat", User)
    venues = read_data("venues.dat", Venue)
    ratings = read_data("ratings.dat", Rating)
    checkins = read_data("checkins.dat", Checkin)

    san_francisco_users = limit_data_by_location(san_francisco_coords, users)
    san_francisco_venues = limit_data_by_location(san_francisco_coords, venues)
    san_francisco_ratings = limit_records_by_user_venue(ratings, san_francisco_users, san_francisco_venues)
    san_francisco_checkins = limit_records_by_user_venue(checkins, san_francisco_users, san_francisco_venues)

    print(f"total number of users: {len(users)}, users in {place_name}: {len(san_francisco_users)}")
    print(f"total number of venues: {len(venues)}, venues in {place_name}: {len(san_francisco_venues)}")
    print(f"total number of ratings: {len(ratings)}, ratings in {place_name}: {len(san_francisco_ratings)}")
    print(f"total number of checkins: {len(checkins)}, checkins in {place_name}: {len(san_francisco_checkins)}")

    store_records(san_francisco_users, "data/users.txt")
    store_records(san_francisco_venues, "data/venues.txt")
    store_records(san_francisco_ratings, "data/ratings.txt")
    store_records(san_francisco_checkins, "data/checkins.txt")

# calgary_coords = [[
#     (-114.325419, 51.214159),  # long, lat
#     (-113.865366, 51.214159),
#     (-113.865366, 50.847729),
#     (-114.325419, 50.847729),
# ]]

# alberta_coords = [[
#     (-119.921953, 53.212140),  # long, lat
#     (-114.548265, 49.017250),
#     (-110.021898, 49.002837),
#     (-110.021898, 59.994249),
#     (-119.997483, 60.005236),
# ]]

# california_coords = [[
#     (-124.371877, 41.990849),
#     (-119.975840, 41.999506),
#     (-120.002350, 38.986355),
#     (-114.594288, 34.996728),
#     (-114.700328, 32.729648),
#     (-117.205534, 32.551061),
#     (-125.953869, 35.580972)
# ]]
