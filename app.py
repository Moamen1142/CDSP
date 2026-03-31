import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title='Streaming Dashboard', layout='wide')
selected_platform = st.sidebar.selectbox('Platform', options=['NETFLIX', 'DISNEY'])
st.title(f'{selected_platform} Dashboard')

color = ['#006E99', '#003B6F', '#C9A84C', '#F5E6C8'] if selected_platform == 'DISNEY' else ['#221f1f', '#b20710', '#e50914', '#f5f5f1']
image = 'https://www.logo.wine/a/logo/Disney%2B/Disney%2B-Logo.wine.svg' if selected_platform == 'DISNEY' else 'https://www.logo.wine/a/logo/Netflix/Netflix-Logo.wine.svg'
st.sidebar.image(image, width=150)

@st.cache_data
def load_data(platform):
    df = pd.read_csv(f'{platform.lower()}_cleaned.csv')
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['duration'] = pd.to_numeric(
        df['duration'].str.replace(' min', '').str.replace(' Season.*', '', regex=True),
        errors='coerce'
    )
    return df

df = load_data(selected_platform)

selected_type = st.sidebar.selectbox('Type', options=['Movie', 'TV Show'])
all_countries = df['country'].str.split(', ').explode().dropna().unique()
all_countries = sorted(all_countries)
selected_country = st.sidebar.selectbox('Country', options=all_countries)

filtered_df = df[
    (df['type'] == selected_type) &
    (df['country'].str.contains(selected_country, na=False))
]

mask = {
    'TV-PG': 'Older Kids', 'TV-MA': 'Adults', 'TV-Y7-FV': 'Older Kids',
    'TV-Y7': 'Older Kids', 'TV-14': 'Teens', 'R': 'Adults',
    'TV-Y': 'Kids', 'NR': 'Adults', 'PG-13': 'Teens',
    'TV-G': 'Kids', 'PG': 'Older Kids', 'G': 'Kids',
    'UR': 'Adults', 'NC-17': 'Adults'
}

tab1, tab2, tab3 = st.tabs(['Overview', 'Plots', 'Insights'])

with tab1:
    st.dataframe(
        filtered_df[['title', 'director', 'rating', 'lead_actor', 'supporting_actor']],
        use_container_width=True,
        hide_index=True
    )
    col1, col2 = st.columns(2)
    col1.metric('Number of Titles', len(filtered_df))
    col2.metric('Average Duration (min)', round(filtered_df['duration'].mean(skipna=True), 0))

with tab2:
    col1, col2 = st.columns(2)

    top_genres = filtered_df['listed_in'].str.get_dummies(sep=', ').sum().reset_index()
    top_genres.columns = ['Genre', 'Titles']
    fig1 = px.treemap(top_genres, path=['Genre'], values='Titles', title='Top Genres', color_discrete_sequence=color)

    top_lead = filtered_df.groupby('lead_actor')['title'].count().sort_values(ascending=False).head(5).reset_index()
    top_lead.columns = ['Actor', 'Appearances']
    fig2 = px.bar(top_lead, x='Appearances', y='Actor', orientation='h', title='Top 5 Lead Actors', color_discrete_sequence=color)

    top_ratings = filtered_df.groupby(filtered_df['rating'].map(mask))['title'].count().reset_index()
    top_ratings.columns = ['Rating', 'Titles']
    fig3 = px.pie(top_ratings, names='Rating', values='Titles', title='Top Ratings', color_discrete_sequence=color)

    top_support = filtered_df.groupby('supporting_actor')['title'].count().sort_values(ascending=False).head(5).reset_index()
    top_support.columns = ['Actor', 'Appearances']
    fig4 = px.bar(top_support, x='Appearances', y='Actor', orientation='h', title='Top 5 Supporting Actors', color_discrete_sequence=color)

    titles_year = filtered_df.groupby('release_year')['title'].count().sort_index().reset_index()
    titles_year.columns = ['Year', 'Titles']
    fig5 = px.area(titles_year, x='Year', y='Titles', title='Titles Time Distribution', color_discrete_sequence=color)

    top_directors = filtered_df[filtered_df['director'] != 'N/A'].groupby('director')['title'].count().sort_values(ascending=False).head(5).reset_index()
    top_directors.columns = ['Director', 'Titles']
    fig6 = px.bar(top_directors, x='Titles', y='Director', orientation='h', title='Top 5 Directors', color_discrete_sequence=color)

    with col1:
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig3, use_container_width=True)
        st.plotly_chart(fig5, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)
        st.plotly_chart(fig4, use_container_width=True)
        st.plotly_chart(fig6, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)

    genre_polar = filtered_df['listed_in'].str.get_dummies(sep=', ').sum()
    fig7 = px.bar_polar(r=genre_polar.values, theta=genre_polar.index, title='Genre Distribution', color_discrete_sequence=color)

    rating_polar = filtered_df.groupby(filtered_df['rating'].map(mask))['title'].count()
    fig8 = px.bar_polar(r=rating_polar.values, theta=rating_polar.index, title='Ratings Distribution', color_discrete_sequence=color)

    with col1:
        st.plotly_chart(fig7, use_container_width=True)
    with col2:
        st.plotly_chart(fig8, use_container_width=True)
