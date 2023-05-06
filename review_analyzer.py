import review_parser
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
import seaborn as sns
import datetime as dt
import matplotlib.gridspec as gridspec

from transformers import pipeline

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

def sentiment_analysis(reviews):
    sentiment_pipeline = pipeline("sentiment-analysis", model="finiteautomata/bertweet-base-sentiment-analysis")
    emotional_pipeline = pipeline(model="bhadresh-savani/distilbert-base-uncased-emotion")
    data, scores = [], []

    for review in reviews:
        content = review.content if review.content is not None and len(review.content) > 0 else ""
        pros = review.pros if review.pros is not None and len(review.pros) > 0 else ""
        cons = review.cons if review.cons is not None and len(review.cons) > 0 else ""

        if 0 < (t := len(content)) < 512:
            data.append(content[:min(t, 512)])
            scores.append(review.score)
        if 0 < (p := len(pros)) < 512:
            data.append(pros[:min(p, 512)])
            scores.append(review.score)
        if 0 < (c := len(cons)) < 512:
            data.append(pros[:min(c, 512)])
            scores.append(review.score)

    def __apply_pipelines(*pipelines):
        __results = []
        for pipeline in pipelines:
            d = pipeline(data)
            __results.append(set(zip(data, scores, [dd["label"] for dd in d])))
        
        return __results

    results = __apply_pipelines(sentiment_pipeline, emotional_pipeline)

    sentiment_label_counts = Counter([l for (c,s,l) in results[0]])
    emotional_label_counts = Counter([l for (c,s,l) in results[1]])
    score_counts = Counter([str(int(score)) for score in scores])

    # Create 2x2 sub plots
    gs = gridspec.GridSpec(nrows=2, ncols=2, hspace=0.75)
    
    plt.figure()

    ax = plt.subplot(gs[0, 0]) # row 0, col 0
    plt.bar(["NEG", "NEU", "POS"],
            np.array([
                sentiment_label_counts["NEG"],
                sentiment_label_counts["NEU"],
                sentiment_label_counts["POS"]
            ]), color=['tomato', 'silver', 'yellowgreen'], width=0.75)
    plt.title("Sentiment Counts")


    ax = plt.subplot(gs[0, 1]) # row 0, col 1
    plt.bar(["anger", "fear", "sadness", "surprise", "joy", "love"],
            np.array([
                emotional_label_counts["anger"],
                emotional_label_counts["fear"],
                emotional_label_counts["sadness"],
                emotional_label_counts["surprise"],
                emotional_label_counts["joy"],
                emotional_label_counts["love"],
            ]), color=['red', 'lime', "navy", "yellow", "goldenrod", "pink"], width=0.75)
    plt.title("Emotional Counts")
    plt.xticks(rotation=45, ha='right')

    ax = plt.subplot(gs[1,:]) # row 1, both columns
    plt.bar(["1 star", "2 stars", "3 stars", "4 stars", "5 stars"],
            np.array([
                score_counts["1"],
                score_counts["2"],
                score_counts["3"],
                score_counts["4"],
                score_counts["5"],
            ]), color=['red', 'orange', "yellow", "green", "blue"], width=0.75)
    plt.title("Score Counts")

    # y_axis = np.arange(0, 6, 1)
    # plt.yticks(y_axis, y_values)

    # plt.subplots_adjust(bottom=0.5)

    plt.show()

def main():
    all_reviews = review_parser.load_reviews()
    # score_vs_location(all_reviews)
    # score_vs_date(all_reviews)
    print(sentiment_analysis(all_reviews))


if __name__ == "__main__":
    main()