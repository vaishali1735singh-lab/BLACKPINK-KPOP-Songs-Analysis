import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------
# PAGE SETTINGS
# ---------------------------------------------------
st.set_page_config(
    page_title="BLACKPINK Comeback & Momentum Analysis",
    page_icon="🎵",
    layout="wide"
)

st.title("🎵 BLACKPINK Comeback & Momentum Analysis")
st.markdown(
    "Business Analytics Dashboard covering chart re-entry, comeback momentum, "
    "content attributes and fandom engagement."
)

# ---------------------------------------------------
# LOAD EXCEL FILE
# ---------------------------------------------------
FILE_NAME = "BLACKPINK_KPOP_Analysis.xlsx"

try:
    excel = pd.ExcelFile(FILE_NAME)
    sheets = excel.sheet_names
except Exception:
    st.error(
        f"Could not find {FILE_NAME}. "
        "Make sure the Excel file is in the same project repository."
    )
    st.stop()

# Load every sheet
data = {}
for sheet in sheets:
    try:
        data[sheet] = pd.read_excel(FILE_NAME, sheet_name=sheet)
    except Exception:
        data[sheet] = pd.DataFrame()

# ---------------------------------------------------
# HELPERS
# ---------------------------------------------------
def find_sheet(keyword):
    for name in sheets:
        if keyword.lower() in name.lower():
            return data[name]
    return pd.DataFrame()


def clean_number(value):
    try:
        return float(str(value).replace("%", "").strip())
    except Exception:
        return None


# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------
st.sidebar.header("🔎 Dashboard Filters")

main_df = data.get(sheets[0], pd.DataFrame()).copy()

# Song filter
song_col = next(
    (c for c in main_df.columns if str(c).lower() in ["songs", "song", "song name"]),
    None
)

if song_col:
    songs = sorted(main_df[song_col].dropna().astype(str).unique())
    selected_songs = st.sidebar.multiselect(
        "Song",
        songs,
        default=songs
    )
else:
    selected_songs = []

# Artist filter
artist_col = next(
    (c for c in main_df.columns if str(c).lower() == "artist"),
    None
)

if artist_col:
    artists = sorted(main_df[artist_col].dropna().astype(str).unique())
    selected_artists = st.sidebar.multiselect(
        "Artist",
        artists,
        default=artists
    )
else:
    selected_artists = []

# Apply filters
filtered_df = main_df.copy()

if song_col and selected_songs:
    filtered_df = filtered_df[
        filtered_df[song_col].astype(str).isin(selected_songs)
    ]

if artist_col and selected_artists:
    filtered_df = filtered_df[
        filtered_df[artist_col].astype(str).isin(selected_artists)
    ]

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------
st.subheader("📌 Key Performance Indicators")

kpi_df = find_sheet("11")

if kpi_df.empty:
    # Fallback: search for KPI sheet by column names
    for name, df in data.items():
        cols = [str(c).lower() for c in df.columns]
        if "kpi name" in cols and "kpi value" in cols:
            kpi_df = df
            break

kpis = {}

if not kpi_df.empty:
    name_col = next(
        (c for c in kpi_df.columns if str(c).lower() == "kpi name"),
        None
    )
    value_col = next(
        (c for c in kpi_df.columns if str(c).lower() == "kpi value"),
        None
    )

    if name_col and value_col:
        for _, row in kpi_df.iterrows():
            name = str(row[name_col]).strip()
            value = row[value_col]
            kpis[name] = value

# Get KPI values from Sheet 11
reentry = kpis.get("Re-Entry Frequency", 5)
momentum = kpis.get("Momentum Spike Score", 12.2)
retention = kpis.get("Post-Comeback Retention Days", 23.33)
rank_recovery = kpis.get("Rank Recovery Speed", 0.11013)
album_advantage = kpis.get("Album Comeback Advantage Index", 0.0374)
fandom = kpis.get("Fandom Intensity Proxy Score", 0.06448)

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("Re-Entry Frequency", reentry)
c2.metric("Momentum Spike Score", momentum)
c3.metric("Retention Days", retention)
c4.metric("Rank Recovery Speed", rank_recovery)
c5.metric("Album Comeback Advantage", f"{float(album_advantage)*100:.2f}%")
c6.metric("Fandom Intensity", fandom)

st.divider()

# ---------------------------------------------------
# POPULARITY ANALYSIS
# ---------------------------------------------------
st.subheader("📈 Popularity Analysis")

pop_col = next(
    (c for c in filtered_df.columns
     if "popularity" in str(c).lower()),
    None
)

if song_col and pop_col and not filtered_df.empty:
    fig = px.bar(
        filtered_df,
        x=song_col,
        y=pop_col,
        title="Popularity by Song",
        text=pop_col
    )

    fig.update_layout(
        xaxis_title="Song",
        yaxis_title="Popularity Score",
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# CHART RANK ANALYSIS
# ---------------------------------------------------
st.subheader("🏆 Chart Rank Performance")

rank_col = next(
    (c for c in filtered_df.columns
     if "chart rank" in str(c).lower()),
    None
)

if song_col and rank_col and not filtered_df.empty:
    fig = px.bar(
        filtered_df,
        x=song_col,
        y=rank_col,
        title="Chart Rank by Song",
        text=rank_col
    )

    fig.update_layout(
        xaxis_title="Song",
        yaxis_title="Chart Rank",
        xaxis_tickangle=-45,
        yaxis_autorange="reversed"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# ALBUM TYPE ANALYSIS
# ---------------------------------------------------
st.subheader("💿 Album Type vs Popularity")

album_df = find_sheet("5")

if not album_df.empty:
    st.dataframe(album_df, use_container_width=True)

    album_pop_col = next(
        (c for c in album_df.columns
         if "avg. popularity" in str(c).lower()
         or "avg popularity" in str(c).lower()),
        None
    )

    album_type_col = next(
        (c for c in album_df.columns
         if "album type" in str(c).lower()),
        None
    )

    if album_type_col and album_pop_col:
        fig = px.bar(
            album_df,
            x=album_type_col,
            y=album_pop_col,
            title="Average Popularity: Single vs Album",
            text=album_pop_col
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# DURATION ANALYSIS
# ---------------------------------------------------
st.subheader("⏱️ Duration vs Popularity")

duration_df = find_sheet("6")

if not duration_df.empty:
    st.dataframe(duration_df, use_container_width=True)

    duration_col = next(
        (c for c in duration_df.columns
         if "duration range" in str(c).lower()),
        None
    )

    duration_pop_col = next(
        (c for c in duration_df.columns
         if "avg. popularity" in str(c).lower()
         or "avg popularity" in str(c).lower()),
        None
    )

    if duration_col and duration_pop_col:
        fig = px.bar(
            duration_df,
            x=duration_col,
            y=duration_pop_col,
            title="Average Popularity by Duration Range",
            text=duration_pop_col
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# CONTENT ATTRIBUTE ANALYSIS
# ---------------------------------------------------
st.subheader("🎵 Content Attributes & Momentum")

content_df = find_sheet("9")

if not content_df.empty:
    st.dataframe(content_df, use_container_width=True)

    level_col = next(
        (c for c in content_df.columns
         if "engagement level" in str(c).lower()),
        None
    )

    engagement_col = next(
        (c for c in content_df.columns
         if "engagement score" in str(c).lower()
         or "engagement" in str(c).lower()),
        None
    )

    if level_col and engagement_col:
        summary = (
            content_df.groupby(level_col, as_index=False)[engagement_col]
            .mean()
        )

        fig = px.bar(
            summary,
            x=level_col,
            y=engagement_col,
            title="Engagement by Level",
            text_auto=True
        )

        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# FANDOM INTENSITY LEADERBOARD
# ---------------------------------------------------
st.subheader("🏆 Fandom Intensity Leaderboard")

engagement_df = find_sheet("10")

if not engagement_df.empty:
    st.dataframe(
        engagement_df,
        use_container_width=True
    )

# ---------------------------------------------------
# COMEBACK / RE-ENTRY ANALYSIS
# ---------------------------------------------------
st.subheader("🔄 Comeback & Re-Entry Analysis")

reentry_df = find_sheet("2")

if not reentry_df.empty:
    st.dataframe(
        reentry_df,
        use_container_width=True
    )

    numeric_cols = reentry_df.select_dtypes(
        include="number"
    ).columns.tolist()

    if len(numeric_cols) > 0:
        first_numeric = numeric_cols[0]

        fig = px.bar(
            reentry_df,
            x=reentry_df.columns[0],
            y=first_numeric,
            title=f"{first_numeric} by Song"
        )

        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# EXECUTIVE SUMMARY
# ---------------------------------------------------
st.divider()
st.subheader("💡 Executive Summary")

st.markdown("""
### Key Business Insights

- BLACKPINK songs demonstrate strong popularity and chart performance.
- Re-entry behaviour provides an indicator of continued audience interest.
- Momentum spikes can help identify songs with strong comeback potential.
- Content and song characteristics can be compared against popularity and engagement.
- Fandom intensity provides a proxy for audience engagement around comeback activity.

### Business Recommendations

1. Monitor songs with strong re-entry behaviour for long-term audience interest.
2. Track momentum spikes to identify potential comeback opportunities.
3. Compare album and single performance when planning future releases.
4. Use engagement intensity as an additional indicator alongside chart rank and popularity.
5. Use the dashboard filters to investigate individual songs and artists.
""")

st.caption(
    "BLACKPINK K-pop Songs — Business Analytics Project"
)
