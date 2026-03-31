import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns

df = pd.read_csv('netflix_cleaned.csv')
df['date_added'] = pd.to_datetime(df['date_added'])
df['duration'] = pd.to_numeric(df['duration'])

st.set_page_config(page_title='Netflix Dashboard', layout='wide')

selected_type = st.sidebar.selectbox('Type', options=['Movie', 'TV Show'])

# min_year = int(df[df.type==selected_type]['release_year'].min())
# max_year = int(df[df.type==selected_type]['release_year'].max())
# year_range = st.sidebar.slider('Year range', min_year, max_year, (min_year, max_year))

all_countries=df.country.str.rstrip(',').str.get_dummies(sep=', ').columns
selected_country=st.sidebar.selectbox('country',options=all_countries)

# if selected_type=='Movie':
#     all_genres=df[df.type==selected_type]['listed_in'].str.get_dummies(sep=', ').drop(columns=['Movies']).columns
# else:
#     all_genres=df[df.type==selected_type]['listed_in'].str.get_dummies(sep=', ').drop(columns=['TV Shows']).columns
# selected_genre=st.sidebar.selectbox('genre',options=all_genres)

filtered_df=df[(df.type==selected_type)&(df.country.str.contains(selected_country))]

tab1,tab2=st.tabs(['overview','plots'])
with tab1:
    st.dataframe(filtered_df[['title','director','rating','lead_actor','supporting_actor']])
    col1,col2,col3=st.columns(3)
    col1.metric('number of titles',len(filtered_df))
    col2.metric('number of directors',filtered_df[filtered_df.director!='N/A']['director'].nunique())
    col3.metric('average duration',round(number=filtered_df['duration'].mean(),ndigits=0))
with tab2:
    col1, col2 = st.columns(2)

    top_genres=filtered_df['listed_in'].str.rstrip(',').str.get_dummies(sep=', ').sum().to_frame(name='Titles').reset_index().head()
    top_genres.columns=['Genre','Titles']
    fig1=px.pie(data_frame=top_genres,names='Genre',values='Titles',color_discrete_sequence=['#221f1f', '#b20710', '#e50914','#f5f5f1'])

    top_lead=filtered_df.groupby('lead_actor')['title'].count().sort_values(ascending=False).head(5).reset_index()
    top_lead.columns = ['Actor', 'Appearances']
    fig2=px.bar(top_lead,x='Appearances',y='Actor',title='Top 5 Lead Actors',orientation='h',color_discrete_sequence=['#221f1f', '#b20710', '#e50914','#f5f5f1'])

    mask = {
    'TV-PG': 'Older Kids',
    'TV-MA': 'Adults',
    'TV-Y7-FV': 'Older Kids',
    'TV-Y7': 'Older Kids',
    'TV-14': 'Teens',
    'R': 'Adults',
    'TV-Y': 'Kids',
    'NR': 'Adults',
    'PG-13': 'Teens',
    'TV-G': 'Kids',
    'PG': 'Older Kids',
    'G': 'Kids',
    'UR': 'Adults',
    'NC-17': 'Adults'
    }
    top_ratings=filtered_df.groupby(filtered_df.rating.map(mask))['title'].count().reset_index()
    top_ratings.columns=['Rating','Titles']
    fig3=px.pie(data_frame=top_ratings,names='Rating',values='Titles',color_discrete_sequence=['#221f1f', '#b20710', '#e50914','#f5f5f1'])

    top_supprt=filtered_df.groupby('supporting_actor')['title'].count().sort_values(ascending=False).head(5).reset_index()
    top_supprt.columns = ['Actor', 'Appearances']
    fig4=px.bar(top_supprt,x='Appearances',y='Actor',title='Top 5 Supporting Actors',orientation='h',color_discrete_sequence=['#221f1f', '#b20710', '#e50914','#f5f5f1'])

    with col1:
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.plotly_chart(fig2, use_container_width=True)
        st.plotly_chart(fig4, use_container_width=True)


