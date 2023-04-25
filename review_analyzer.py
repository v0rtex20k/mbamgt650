import review_parser
import geopandas as gpd
from typing import Tuple
from shapely import Point
from functools import cache
import matplotlib.pyplot as plt
from geopy import Nominatim, Location

GEO = Nominatim(user_agent="mbamgt650")
SCALE = 10**4

@cache
def get_lat_lon(loc_str: str)-> Point:
    if loc_str is not None:
        loc_str = loc_str\
            .lower()\
            .replace(',', ', ')\
            .replace('.', ' ')\
            .replace("massachusetts", "MA")\
            .replace("mass", "MA")\
            .replace("ma", "MA")\
            .strip().replace('  ', ' ')
        
        if ',' not in loc_str:
            if "MA" in loc_str:
                loc_str.replace("MA", ", MA")
            loc_str += ", MA"

        global GEO
        try: # 235818, 900566
             # -71.061 42.355
            loc: Location = GEO.geocode(loc_str, country_codes=["US"], exactly_one=True)
            if -73.508142 <= loc.longitude <= -69.928393\
            and 41.237964 <= loc.latitude <= 42.886589:
                return Point(int((round(loc.longitude, 1) * 10**4) + (0.94643 * (10**6))),
                             int((round(loc.latitude, 1)  * 10**4) + (4.77020 * (10**5))))
        except:
            print(f"Could not find location: \"{loc_str}\"")


def score_vs_location(reviews):
    scores, geo_points = [], []
    for r in reviews:
        if r.origin == "indeed" and r.location is not None:
            if (p := get_lat_lon(r.location)) is not None:
                scores.append(r.score)
                geo_points.append(p)

    map_path = review_parser.load_map()
    print(map_path)
    map = gpd.read_file(map_path)

    df = gpd.GeoDataFrame(scores, geometry=geo_points)


    fig, ax = plt.subplots(figsize=(10,5))
    df.plot(ax=ax, 
            markersize=20, 
            color='red', 
            marker='o', 
            label='Neg')

    map.plot(ax=ax)
    plt.show()

def main():
    all_reviews = review_parser.load_reviews()
    score_vs_location(all_reviews)


def translate(x, y):
    return int((x * 10**4) + (0.94643 * (10**6))), int((y * 10**4) + (4.7702 * (10**5)))

if __name__ == "__main__":
    # print(translate(-71.061, 42.355))
    # print("(235818, 900566)")
    main()