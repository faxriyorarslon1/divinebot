from geopy.geocoders import Nominatim

loc = Nominatim(user_agent="GetLoc")


def location_address(latitude, longitude):
    locname = loc.reverse(f"{latitude}, {longitude}")
    return locname.address



