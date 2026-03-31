import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns

st.set_page_config(page_title='Streaming Dashboard', layout='wide')
selected_platform = st.sidebar.selectbox('Platform', options=['NETFLIX', 'DISNEY'])
st.title(f'{selected_platform} Dashboard')
color = ['#006E99', '#003B6F', '#C9A84C', '#F5E6C8', '#FFFFFF']  if selected_platform=='DISNEY' else ['#221f1f', '#b20710', '#e50914','#f5f5f1']
image = 'https://www.logo.wine/a/logo/Disney%2B/Disney%2B-Logo.wine.svg' if selected_platform=='DISNEY' else 'https://www.logo.wine/a/logo/Netflix/Netflix-Logo.wine.svg'
st.image(image,width=200)

df = pd.read_csv('disney_cleaned.csv') if selected_platform=='DISNEY' else pd.read_csv('netflix_cleaned.csv')
df['date_added'] = pd.to_datetime(df['date_added'])
df['duration'] = pd.to_numeric(df['duration'])
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

tab1,tab2,tab3=st.tabs(['overview','plots','insights'])
with tab1:
    st.dataframe(filtered_df[['title','director','rating','lead_actor','supporting_actor']])
    col1,col2=st.columns(2)
    col1.metric('number of titles',len(filtered_df))
    col2.metric('average duration',round(number=filtered_df['duration'].mean(),ndigits=0))
with tab2:
    col1, col2 = st.columns(2)

    top_genres=filtered_df['listed_in'].str.rstrip(',').str.get_dummies(sep=', ').sum().to_frame(name='Titles').reset_index()
    top_genres.columns=['Genre','Titles']
    fig1=px.treemap(data_frame=top_genres,path=['Genre'],values='Titles',color_discrete_sequence=color,title='Top Genres')

    top_lead=filtered_df.groupby('lead_actor')['title'].count().sort_values(ascending=False).head(5).reset_index()
    top_lead.columns = ['Actor', 'Appearances']
    fig2=px.bar(top_lead,x='Appearances',y='Actor',title='Top 5 Lead Actors',orientation='h',color_discrete_sequence=color)

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
    fig3=px.pie(data_frame=top_ratings,names='Rating',values='Titles',color_discrete_sequence=color,title='Top Ratings')

    top_supprt=filtered_df.groupby('supporting_actor')['title'].count().sort_values(ascending=False).head(5).reset_index()
    top_supprt.columns = ['Actor', 'Appearances']
    fig4=px.bar(top_supprt,x='Appearances',y='Actor',title='Top 5 Supporting Actors',orientation='h',color_discrete_sequence=color)

    titles_year=filtered_df.groupby('release_year')['title'].count().sort_index().reset_index()
    titles_year.columns=['Year','Titles']
    fig5=px.area(titles_year,x='Year',y='Titles',title='Titles Time Distribution',color_discrete_sequence=color)

    top_directors=filtered_df[filtered_df['director']!='N/A'].groupby('director')['title'].count().sort_values(ascending=False).head(5).reset_index()
    top_directors.columns = ['Director', 'Titles']
    fig6=px.bar(top_directors,x='Titles',y='Director',title='Top 5 Directors',orientation='h',color_discrete_sequence=color)

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

    top_countries=df[df.type==selected_type].country.str.rstrip(',').str.get_dummies(sep=', ').sum().sort_values(ascending=False)[:10].to_frame().reset_index()
    top_countries.columns=['Country','Titles']
    fig7=px.bar(data_frame=top_countries,
       x='Country',
       y='Titles',
       title=f'Top 10 Countries on {selected_platform}',
       color_discrete_sequence=color)

    fig8=px.bar_polar(r=df[df.type==selected_type].groupby(df.date_added.dt.month_name())['title'].count().values,
             theta=df[df.type==selected_type].groupby(df.date_added.dt.month_name())['title'].count().index,
             color_discrete_sequence=color,
             title=f'Most Active Months on {selected_platform}')         

    with col1:
        st.plotly_chart(fig7, use_container_width=True)
        # st.plotly_chart(fig3, use_container_width=True)
        # st.plotly_chart(fig5, use_container_width=True)     
    with col2:
        st.plotly_chart(fig8, use_container_width=True)
        # st.plotly_chart(fig4, use_container_width=True)
        # st.plotly_chart(fig6, use_container_width=True)
