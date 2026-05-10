import kagglehub
import pandas as pd
import os

filename = "tvshows.jsonl"
path = kagglehub.dataset_download("lakhindarpal/asian-drama-dataset")
dramas = pd.read_json(os.path.join(path, filename), lines=True)

# TODO have functions for the printing portions to call in clean_data()


def clean_data(dataset):
    # save the english names of drama
    dataset["title_en"] = dataset["titles"].apply(lambda x: x.get("english") if isinstance(x, dict) else None)

    # turn the string value of the scores into floats
    dataset["score_value"] = pd.to_numeric(
        dataset["score"].apply(lambda x: x.get("value") if isinstance(x, dict) else None),
        errors="coerce"
    )
    # same for the number of votes
    dataset["score_votes"] = pd.to_numeric(
        dataset["score"].apply(lambda x: x.get("votes") if isinstance(x, dict) else None),
        errors="coerce"
    )
    # same for the number of episodes
    if "episodes" in dataset.columns:
        dataset["episodes_num"] = pd.to_numeric(dataset["episodes"], errors="coerce")
    else:
         dataset["episodes_num"] = None
    # saving the year the drama came out
    dataset["year"] = pd.to_datetime(dataset["date"], errors="coerce").dt.year

    # if there is no name for the platform mark as "Unknown"
    if "network" in dataset.columns:
        dataset["network_name"] = dataset["network"].apply(lambda x: x.get("name") if isinstance(x, dict) else "Unknown")
    else:
        dataset["network_name"] = "Unknown"

    # gather the genre(s) for the drama in a list
    dataset["drama_genres"] = dataset["genres"].apply(
        lambda items: [g.get("name") for g in items if isinstance(g, dict)]
        if isinstance(items, list) else []
    )

    # after careful consideration, these are our finalists
    keep_cols = [
        "id", "title_en", "country", "type", "year",
        "score_value", "score_votes", "episodes_num",
        "network_name", "rating", "synopsis", "drama_genres", "cover"
    ]

    # easier dataset to use for the dashboard
    profile_df = dataset[keep_cols]
    return profile_df
