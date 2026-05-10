from typing import Optional, List
import pandas as pd


def personalized_recommendations(df: pd.DataFrame, liked_genres: Optional[List[str]] = None,
                                  favorite_actor: Optional[str] = None, min_rating: float = 0.0,
                                  max_episodes: Optional[int] = None, year_range: Optional[tuple] = None,
                                  top_k: int = 10) -> pd.DataFrame:
    """
    Get personalized recommendations based on user preferences.

    Args:
        df: Input dataframe
        liked_genres: List of genres user likes
        favorite_actor: Actor name to search for
        min_rating: Minimum rating threshold
        max_episodes: Maximum episode count (for length preference)
        year_range: Tuple of (year_min, year_max)
        top_k: Number of recommendations to return
    Returns:
        DataFrame with top-k recommendations and similarity scores
    """
    q = df.copy()

    # Apply filters
    if min_rating > 0:
        q = q[q["score_value"].fillna(0) >= min_rating]

    if max_episodes is not None:
        q = q[q["episodes_num"].fillna(0) <= max_episodes]

    if year_range is not None:
        q = q[q["year"].fillna(0).astype(float).between(year_range[0], year_range[1])]

    if not q.empty:
        q = q.reset_index(drop=True)

        # If we have liked genres, compute genre-based similarity
        if liked_genres:
            # Simple genre match scoring
            def genre_score(row):
                genres = row.get("drama_genres")
                if isinstance(genres, list):
                    matches = sum(1 for g in genres if g in liked_genres)
                    return matches / len(liked_genres) if liked_genres else 0
                return 0

            q["genre_sim"] = q.apply(genre_score, axis=1)
        else:
            q["genre_sim"] = 0.5

        # Actor matching
        if favorite_actor:
            def actor_score(row):
                cast = row.get("cast")
                if isinstance(cast, dict):
                    for key in ("main", "support", "guest"):
                        actors_list = cast.get(key, [])
                        if isinstance(actors_list, list):
                            for a in actors_list:
                                if isinstance(a, dict):
                                    name = a.get("name", "")
                                    if name and favorite_actor.lower() in name.lower():
                                        return 1.0
                return 0.0

            q["actor_sim"] = q.apply(actor_score, axis=1)
        else:
            q["actor_sim"] = 0.5

        # Combine scores
        q["combined_score"] = 0.6 * q["genre_sim"] + 0.4 * q["actor_sim"]
        q = q.sort_values("combined_score", ascending=False).head(top_k).copy()

        # Ensure we have all needed columns, filling with None if missing
        result_cols = ["title_en", "score_value", "drama_genres", "synopsis", "episodes_num", "year", "combined_score"]
        if "cover" in q.columns:
            result_cols.insert(4, "cover")
        else:
            # If cover is missing from q, add it as a column of None
            if top_k > 0 and len(q) > 0:
                q["cover"] = None
                result_cols.insert(4, "cover")

        available_cols = [c for c in result_cols if c in q.columns]

        return q[available_cols]

    return pd.DataFrame()


if __name__ == "__main__":
    # small demonstration when running this module directly (for dev).
    print("recs.py helper module — import into your app and use the functions.")
