import streamlit as st
import kagglehub
import pandas as pd
import os
from work import clean_data
import plotly.express as px
from recs import personalized_recommendations

@st.cache_data(show_spinner=False)
def load_data():
    path = kagglehub.dataset_download("lakhindarpal/asian-drama-dataset")
    filenames = ["dramas.jsonl", "movies.jsonl", "tvshows.jsonl", "specials.jsonl"]

    data = []
    # load in all the different datasets
    for filename in filenames:
        df = pd.read_json(os.path.join(path, filename), lines=True)
        data.append(clean_data(df))

    # combine the data
    combination = pd.concat(data, ignore_index=True)
    return combination

def main():
    df = load_data()
    filtered_df = df.copy()

    tab1, tab2, tab3 = st.tabs([
        "About",
        "Relationships",
        "Recommendations"
    ])

    with tab1:
        st.markdown(
            """
            <style>
                .about-hero {
                    padding: 2.2rem 2rem;
                    border-radius: 24px;
                    background: linear-gradient(135deg, rgba(17,24,39,0.96), rgba(88,28,135,0.88));
                    color: white;
                    margin-bottom: 1.5rem;
                    box-shadow: 0 18px 50px rgba(15, 23, 42, 0.25);
                }
                .about-pill {
                    display: inline-block;
                    padding: 0.35rem 0.75rem;
                    border-radius: 999px;
                    background: rgba(255,255,255,0.14);
                    margin-right: 0.5rem;
                    margin-bottom: 0.5rem;
                    font-size: 0.88rem;
                }
                .feature-card {
                    padding: 1rem 1.1rem;
                    border-radius: 18px;
                    background: rgba(255,255,255,0.72);
                    border: 1px solid rgba(15,23,42,0.08);
                    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
                    height: 100%;
                }
                .section-title {
                    margin-top: 0.5rem;
                    margin-bottom: 0.5rem;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="about-hero">
                <h1 style="margin-bottom:0.4rem;">Welcome to Drama Fanatic</h1>
                <p style="font-size:1.05rem; max-width: 52rem; line-height: 1.55;">
                    Explore Asian drama data through interactive charts, compare genres and ratings,
                    track trends over time, and find personalized recommendations based on what you like.
                </p>
                <div>
                    <span class="about-pill">Interactive dashboards</span>
                    <span class="about-pill">Genre and rating analysis</span>
                    <span class="about-pill">Country and trend views</span>
                    <span class="about-pill">Personalized recommendations</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        intro_col1, intro_col2 = st.columns([1.4, 1])
        with intro_col1:
            st.markdown("### What this app offers")
            st.write(
                "This app helps you explore drama datasets in a few different ways. "
                "You can study how ratings differ by genre, compare country-level genre preferences, "
                "see how scores change over time, and get recommendations tailored to your tastes."
            )
            st.write(
                "The charts are interactive, so you can filter by genre, country, year range, rating, "
                "and more before diving into the visuals."
            )

        with intro_col2:
            st.markdown("### How to use it")
            st.markdown(
                """
                1. Open **Relationships** to explore rating, country, and time-based charts.
                2. Use the filters on the left to narrow the data to what you care about.
                3. Open **Recommendations** to enter your preferences and see matching dramas.
                4. Expand cards or hover charts to inspect details.
                """
            )

        st.markdown("### Main features")
        feature_col1, feature_col2, feature_col3 = st.columns(3)

        with feature_col1:
            st.markdown(
                """
                <div class="feature-card">
                    <h4>Relationships</h4>
                    <p><strong>Genre vs Rating:</strong> Box plots show which genres are rated highest and how consistent they are.</p>
                    <p><strong>Country vs Preferences:</strong> Stacked bars compare genre dominance across countries.</p>
                    <p><strong>Time Trends:</strong> Line charts reveal how ratings and popularity shift across years.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with feature_col2:
            st.markdown(
                """
                <div class="feature-card">
                    <h4>Recommendation Explorer</h4>
                    <p>Filter by genres, favorite actor, minimum rating, length preference, and year range.</p>
                    <p>The app ranks dramas using genre overlap, actor matches, and text similarity from tags and synopsis keywords.</p>
                    <p>Results appear as cards with posters, ratings, genres, and a short description.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with feature_col3:
            st.markdown(
                """
                <div class="feature-card">
                    <h4>Dataset Source</h4>
                    <p>The data comes from the Kaggle Asian drama dataset used by this project.</p>
                    <p>
                        <a href="https://www.kaggle.com/datasets/lakhindarpal/asian-drama-dataset" target="_blank">
                            Open the Kaggle dataset
                        </a>
                    </p>
                    <p>Includes dramas, movies, TV shows, and specials.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("### Quick guide")
        guide_col1, guide_col2 = st.columns(2)
        with guide_col1:
            st.info("Use the Relationships tab to answer questions like: which genres rate best, which countries favor certain genres, and how scores change over time.")
        with guide_col2:
            st.info("Use the Recommendations tab to build a personalized shortlist of dramas that match your taste, then review the cards for posters and details.")

    # Genre ↔ Rating Relationship
    with tab2:
        st.subheader("Genre vs Score Distribution")
        fc1, vc1 = st.columns([1, 2])
        # filter data
        with fc1:
            st.markdown("**Filters**")

            genre_options = (df["drama_genres"].explode().dropna().sort_values().unique().tolist())
            type_options = (df["type"].dropna().sort_values().unique().tolist())
            rating_options = (df["rating"].dropna().unique().tolist())

            selected_genres = st.multiselect("Genre", genre_options, default=[])
            selected_types = st.multiselect("Media type", type_options, default=type_options)
            selected_ratings = st.multiselect("Rating", rating_options, default=[])

            # Score range slider
            try:
                min_score = float(df["score_value"].min())
                max_score = float(df["score_value"].max())
            except Exception:
                min_score, max_score = 0.0, 10.0

            range_min, range_max = st.slider(
                "Score range",
                min_score,
                max_score,
                (min_score, max_score),
                step=0.1,
                key="score_range",
            )

        local_df = filtered_df.copy()
        if selected_types:
            local_df = local_df[local_df["type"].isin(selected_types)]
        if selected_ratings:
            local_df = local_df[local_df["rating"].isin(selected_ratings)]
        if selected_genres:
            local_df = local_df[
                local_df["drama_genres"].apply(
                    lambda genres: isinstance(genres, list) and any(g in genres for g in selected_genres)
                )
            ]

        local_df = local_df[(local_df["score_value"] >= range_min) & (local_df["score_value"] <= range_max)]

        # visualize data
        with vc1:
            box_df = (
                local_df[["drama_genres", "score_value", "rating"]]
                .dropna(subset=["drama_genres", "score_value"])
                .explode("drama_genres")
                .dropna(subset=["drama_genres"])
                .copy()
            )

            # Keep only the most common genres to reduce clutter
            if not box_df.empty:
                top_genres = box_df["drama_genres"].value_counts().nlargest(12).index.tolist()
                box_df = box_df[box_df["drama_genres"].isin(top_genres)]

            if not box_df.empty:
                fig_box = px.box(
                    box_df,
                    x="drama_genres",
                    y="score_value",
                    color="rating",
                    points="outliers",
                    title="Score Distribution by Genre",
                    labels={
                        "drama_genres": "Genre",
                        "score_value": "Score",
                        "rating": "Content Rating",
                    },
                    height=500,
                )
                fig_box.update_layout(xaxis_tickangle=-35)
                st.plotly_chart(fig_box, use_container_width=True)
            else:
                st.info("No data available for genre box plot with current filters.")

        st.subheader("Country vs Drama Preferenes")
        fc2, vc2 = st.columns([1, 2])

        with fc2:
            st.markdown("**Filters**")

            country_options = sorted(df["country"].dropna().unique().tolist())
            # default to top 6 countries if many
            default_countries = country_options[:6]
            selected_countries = st.multiselect("Country", country_options, default=default_countries)

            years = df["year"].dropna().astype(int)
            if not years.empty:
                y_min, y_max = int(years.min()), int(years.max())
            else:
                y_min, y_max = 2000, 2024
            year_range = st.slider("Year range", y_min, y_max, (y_min, y_max), key="year_range_countries")

            genre_options2 = df["drama_genres"].explode().dropna().sort_values().unique().tolist()
            selected_genres2 = st.multiselect("Genres to include", genre_options2, default=genre_options2[:6])

        # build filtered dataset for the stacked bar
        local2 = filtered_df.copy()
        # apply year filter
        if "year" in local2.columns:
            local2 = local2[local2["year"].notna()]
            local2 = local2[local2["year"].astype(int).between(year_range[0], year_range[1])]

        # apply country filter
        if selected_countries:
            local2 = local2[local2["country"].isin(selected_countries)]

        # explode genres and apply genre filter
        stack_df = local2.dropna(subset=["drama_genres"]).explode("drama_genres")
        if selected_genres2:
            stack_df = stack_df[stack_df["drama_genres"].isin(selected_genres2)]

        with vc2:
            if stack_df.empty:
                st.info("No data for selected country/year/genre filters")
            else:
                grp = (
                    stack_df.groupby(["country", "drama_genres"]).size().reset_index(name="count")
                )
                fig_stacked = px.bar(
                    grp,
                    x="country",
                    y="count",
                    color="drama_genres",
                    title="Country vs Genre Preferences (counts)",
                    labels={"count": "Count", "country": "Country", "drama_genres": "Genre"},
                    height=500,
                )
                fig_stacked.update_layout(barmode="stack", xaxis_tickangle=-30)
                st.plotly_chart(fig_stacked, use_container_width=True)

        st.subheader("Time Trends")
        fc3, vc3 = st.columns([1, 2])

        with fc3:
            st.markdown("**Trends Filters**")

            # genres to include in trend (empty = all)
            trend_genres = df["drama_genres"].explode().dropna().sort_values().unique().tolist()
            selected_trend_genres = st.multiselect("Genres (show lines per genre)", trend_genres, default=[])

            # year range
            years_all = df["year"].dropna().astype(int)
            if not years_all.empty:
                ty_min, ty_max = int(years_all.min()), int(years_all.max())
            else:
                ty_min, ty_max = 2000, 2024
            trend_years = st.slider("Year range", ty_min, ty_max, (ty_min, ty_max), key="year_range_trends")

            metric = st.selectbox("Metric", ["Average score", "Count of titles"])

        # prepare data
        trend_df = filtered_df.copy()
        if "year" in trend_df.columns:
            trend_df = trend_df[trend_df["year"].notna()]
            trend_df = trend_df[trend_df["year"].astype(int).between(trend_years[0], trend_years[1])]

        if selected_trend_genres:
            # explode and filter
            trend_df = trend_df.dropna(subset=["drama_genres"]).explode("drama_genres")
            trend_df = trend_df[trend_df["drama_genres"].isin(selected_trend_genres)]
        else:
            # if no genre selected, keep as-is (aggregate across all)
            pass

        with vc3:
            if trend_df.empty:
                st.info("No data for selected trend filters")
            else:
                if metric == "Average score":
                    if selected_trend_genres:
                        grp = trend_df.groupby([trend_df["year"].astype(int), "drama_genres"])["score_value"].mean().reset_index(name="avg_score")
                        fig = px.line(grp, x="year", y="avg_score", color="drama_genres", markers=True, title="Average Score Over Time")
                    else:
                        grp = trend_df.groupby(trend_df["year"].astype(int))["score_value"].mean().reset_index(name="avg_score")
                        fig = px.line(grp, x="year", y="avg_score", markers=True, title="Average Score Over Time")
                else:
                    # Count of titles
                    if selected_trend_genres:
                        grp = trend_df.groupby([trend_df["year"].astype(int), "drama_genres"]).size().reset_index(name="count")
                        fig = px.line(grp, x="year", y="count", color="drama_genres", markers=True, title="Count of Titles Over Time")
                    else:
                        grp = trend_df.groupby(trend_df["year"].astype(int)).size().reset_index(name="count")
                        fig = px.line(grp, x="year", y="count", markers=True, title="Count of Titles Over Time")

                fig.update_layout(xaxis=dict(tickmode="linear"))
                st.plotly_chart(fig, use_container_width=True)

    # Recommendation Explorer
    with tab3:
        st.header("Recommendation Explorer 🎯")
        st.markdown("Tell us what you like, and we'll find your next favorite drama!")

        # Input form
        form_col1, form_col2 = st.columns(2)

        with form_col1:
            st.subheader("Your Preferences")

            # Genres
            all_genres = df["drama_genres"].explode().dropna().sort_values().unique().tolist()
            liked_genres = st.multiselect("Genres you like", all_genres, default=[])

            # Actor
            favorite_actor = st.text_input("Favorite actor (optional)")

            # Rating
            min_rating = st.slider("Minimum rating", 0.0, 10.0, 6.0, key="rec_min_rating")

        with form_col2:
            st.subheader("Other Preferences")

            # Length
            max_eps = st.slider("Max episodes (for length)", 1, 200, 50, key="rec_max_episodes")

            # Year range
            all_years = df["year"].dropna().astype(int)
            if not all_years.empty:
                y_min, y_max = int(all_years.min()), int(all_years.max())
            else:
                y_min, y_max = 2000, 2024
            year_min, year_max = st.slider("Year range", y_min, y_max, (y_min, y_max), key="rec_year_range")

        # Get recommendations button
        if st.button("Find Recommendations", type="primary"):
            if not liked_genres and not favorite_actor:
                st.warning("Please select at least one genre or actor")
            else:
                recs_df = personalized_recommendations(
                    df,
                    liked_genres=liked_genres if liked_genres else None,
                    favorite_actor=favorite_actor if favorite_actor else None,
                    min_rating=min_rating,
                    max_episodes=max_eps,
                    year_range=(year_min, year_max),
                    top_k=12
                )

                if recs_df.empty:
                    st.info("No recommendations found. Try adjusting your preferences.")
                else:
                    st.subheader(f"Top {len(recs_df)} Recommendations")

                    # Display as cards in a grid
                    cols = st.columns(3)
                    for idx, (_, row) in enumerate(recs_df.iterrows()):
                        col = cols[idx % 3]

                        with col:
                            with st.container(border=True):
                                left_col, right_col = st.columns([1, 2])

                                with left_col:
                                    # Poster
                                    if row.get("cover"):
                                        try:
                                            st.image(row["cover"], width=120)
                                        except Exception:
                                            st.write("📺 No poster available")
                                    else:
                                        st.write("📺 No poster available")

                                with right_col:
                                    # Title and rating
                                    st.markdown(f"**{row.get('title_en', 'Unknown')}**")
                                    rating = row.get("score_value") or 0
                                    eps = row.get("episodes_num") or 0
                                    st.markdown(f"⭐ {rating:.1f} | {int(eps)} eps")

                                    # Genres
                                    genres = row.get("drama_genres", [])
                                    if isinstance(genres, list) and genres:
                                        genre_str = ", ".join(str(g) for g in genres[:3])
                                        if len(genres) > 3:
                                            genre_str += f", +{len(genres)-3}"
                                        st.caption(genre_str)

                                    # Synopsis preview
                                    synopsis = row.get("synopsis") or ""
                                    if synopsis:
                                        preview = (synopsis[:120] + "...") if len(synopsis) > 120 else synopsis
                                        st.write(preview)

                                    # Year
                                    year = row.get("year") or "Unknown"
                                    st.caption(f"📅 {year}")


if __name__ == "__main__":
    st.set_page_config(
        page_title="Drama Fanatic",
        page_icon=":tv:",
        layout="wide",)
    main()
