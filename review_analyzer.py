import review_parser
import numpy as np
from shapely import Point
import matplotlib.pyplot as plt
from collections import defaultdict
import seaborn as sns
import datetime as dt

def sanitize(loc_str: str)-> str:
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


        return loc_str.replace(', MA', '').capitalize()

def rescale(z):
    return (z - (m := np.min(z))) / (np.max(z) - m)

def score_vs_location(reviews):
    data = defaultdict(list)
    
    for r in reviews:
        if r.origin == "indeed" and (p := sanitize(r.location)) is not None:
            data[p].append(r.score)

    data = {city: np.round(np.array(scores).mean(), 2) for city, scores in sorted(data.items(), key=lambda item: item[0])}
    
    for name in ["Ma", "Newton corporate office, office of the coo", "Multiple"]:
        del data[name]

    my_cmap = plt.get_cmap("RdYlGn") # type: ignore

    plt.bar(list(data.keys()), (y := np.array(list(data.values()))), color=my_cmap(rescale(y)), width = 0.7)
    plt.title("Indeed Reviews by Location")
    plt.xticks(rotation=90, ha='right')

    y_values = ["0 stars", "1 star", "2 stars", "3 stars", "4 stars", "5 stars"]
    y_axis = np.arange(0, 6, 1)
    plt.yticks(y_axis, y_values)

    plt.subplots_adjust(bottom=0.3)

    plt.show()

def score_vs_date(reviews):
    indeed_data = defaultdict(list)
    glassdoor_data = defaultdict(list)
    
    for r in reviews:
        if r.origin == "indeed":
            indeed_data[r.date].append(r.score)
        if r.origin == "glassdoor":
            glassdoor_data[r.date].append(r.score)

    indeed_data = {date: np.round(np.array(scores).mean(), 2) for date, scores in sorted(indeed_data.items(), key=lambda item: item[0])}
    glassdoor_data = {date: np.round(np.array(scores).mean(), 2) for date, scores in sorted(glassdoor_data.items(), key=lambda item: item[0])}

    fig, axs = plt.subplots(2,2)

    with sns.color_palette("RdYlGn"):
        # plt.title("All Reviews by Date")
        # plt.xticks(rotation=90, ha='right')
        ix, iy = np.array(list(indeed_data.keys())), np.array(list(indeed_data.values()))
        iz = np.divide(np.cumsum(iy), np.arange(1, len(iy)+1))

        gx, gy = np.array(list(glassdoor_data.keys())), np.array(list(glassdoor_data.values()))
        gz = np.divide(np.cumsum(gy), np.arange(1, len(gy)+1))

        axs[0,0].set_title("Indeed Reviews vs Time")
        axs[0,1].set_title("Glassdoor Reviews vs Time")
        axs[0,0].plot(ix, iy, color="indigo")
        axs[1,0].plot(ix, iz, color="gray")

        axs[0,1].plot(gx, gy, color="green")
        axs[1,1].plot(gx, gz, color="gray")
        axs[1,0].set_yticks(np.arange(3, 6, 1), ["3 stars", "4 stars", "5 stars"])
        axs[1,1].set_yticks(np.arange(1, 5, 1), ["1 star", "2 stars", "3 stars", "4 stars"])

        for x in range(0,2):
            for y in range(0,2):
                axs[x,y].set_xticks([dt.datetime(2000+i, 1, 1).timestamp() for i in range(11,24)],
                        [f"20{j}" for j in range(11,24)])
            


        plt.show()

def main():
    all_reviews = review_parser.load_reviews()
    score_vs_location(all_reviews)
    # score_vs_date(all_reviews)


if __name__ == "__main__":
    main()