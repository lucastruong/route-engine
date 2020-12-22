import requests

from src.problem.problem_location import ProblemLocation


def mapbox_directions(locations: list[ProblemLocation], access_token: str):
    url = 'https://api.mapbox.com/directions/v5/mapbox/driving/'
    visits = []
    for location in locations:
        visits.append(str(location.lng) + '%2C' + str(location.lat))

    # Remove duplicates from list
    coordinates = []
    [coordinates.append(x) for x in visits if x not in coordinates]

    link = url + '%3B'.join(coordinates) + '?alternatives=false&geometries=polyline&steps=false&access_token=' + access_token
    r = requests.get(link)

    if r.status_code != 200:
        return ''

    res = r.json()
    geometry = res['routes'][0]['geometry']

    return geometry
