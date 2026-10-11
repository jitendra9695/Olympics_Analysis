import streamlit as st
import pandas as pd
import numpy as np
import preprocessor, helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import gaussian_kde

df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')

df = preprocessor.preprocess(df, region_df) 

st.sidebar.title("Olympics Analysis")
st.sidebar.image('https://static.vecteezy.com/system/resources/thumbnails/036/105/753/small_2x/sankt-petersburg-russia-01-02-2024-olympic-rings-olympic-games-logo-illustration-free-vector.jpg')

user_menu = st.sidebar.radio(
  'Select an option',
  ("Medal Tally", "Overall Analysis", "Country-wise Analysis", "Athlete wise Analysis")
) 

if user_menu == 'Medal Tally':
  st.sidebar.header("Medal Tally")
  years,country = helper.country_year_list(df)

  selected_year = st.sidebar.selectbox("Select Year", years)
  selected_country = st.sidebar.selectbox("Select Country", country)

  medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

  if selected_country == 'Overall' and selected_year == 'Overall':
    st.title("Overall Tally")
  if selected_country == 'Overall' and selected_year != 'Overall':
    st.title("Medal Tally in "+ str(selected_year)+" Olympics")
  if selected_country != 'Overall' and selected_year == 'Overall':
    st.title(selected_country + " Overall performance")
  if selected_country != 'Overall' and selected_year != 'Overall':
    st.title(selected_country +" performance in "+ str(selected_year) + " Olympics")
  st.table(medal_tally)

if user_menu == 'Overall Analysis':
  editions = df['Year'].unique().shape[0]-1
  cities = df['City'].unique().shape[0]
  sports = df['Sport'].unique().shape[0]
  events = df['Event'].unique().shape[0]
  athlets = df['Name'].unique().shape[0]
  nations = df['region'].unique().shape[0]

  st.title("Top Statistics")
  col1,col2,col3 = st.columns(3)

  with col1:
    st.header("Editions")
    st.title(editions)
  with col2:
    st.header("Hosts")
    st.title(cities)
  with col3:
    st.header("Sports")
    st.title(sports)

  col1, col2, col3 = st.columns(3)
  with col1:
    st.header("Events")
    st.title(events)
  with col2:
    st.header("Nations")
    st.title(nations)
  with col3:
    st.header("Athletes")
    st.title(athlets)

  nations_over_time = helper.data_over_time(df, 'region')
  fig = px.line(nations_over_time, x="Year", y='count')
  st.title("Participating Nations over the years")
  st.plotly_chart(fig)

  events_over_time = helper.data_over_time(df, 'Event')
  fig = px.line(events_over_time, x='Year', y='count')
  st.title("Events over the years")
  st.plotly_chart(fig)

  atheletes_over_time = helper.data_over_time(df, 'Name')
  fig = px.line(atheletes_over_time, x='Year', y='count')
  st.title("Atheletes over the years")
  st.plotly_chart(fig)

  st.title("No. of Events over time(Every Sport)")
  fig,ax = plt.subplots(figsize=(20,20))
  x = df.drop_duplicates(['Year', 'Sport', 'Event'])
  ax = sns.heatmap(x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype('int'), annot=True)
  st.pyplot(fig)

  st.title("Most Successful Atheletes")
  sport_list = df['Sport'].unique().tolist()
  sport_list.sort()
  sport_list.insert(0, 'Overall')

  selected_sport = st.selectbox("Select a Sport", sport_list)

  x = helper.most_successful(df, selected_sport)
  st.table(x)

if user_menu == 'Country-wise Analysis':
  st.sidebar.title("Country-wise Analysis")

  country_list = df['region'].dropna().unique().tolist()
  country_list.sort()

  selected_country = st.sidebar.selectbox('Select a country', country_list)

  country_df = helper.yearwise_medal_tally(df, selected_country)
  fig = px.line(country_df, x='Year', y='Medal')
  st.title(selected_country + " Medal Tally over the years")
  st.plotly_chart(fig)

  st.title(selected_country + " excels in the following sports")

  pt = helper.country_event_heatmap(df, selected_country)
  fig, ax = plt.subplots(figsize=(20,20))
  ax = sns.heatmap(pt, annot=True)
  st.pyplot(fig)

  st.title("Top 10 athletes of "+ selected_country)
  top10_df = helper.most_successful_countrywise(df, selected_country)
  st.table(top10_df)

if user_menu == 'Athlete wise Analysis':
  athlete_df = df.drop_duplicates(subset=['Name', 'region'])

  x1 = athlete_df['Age'].dropna()
  x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
  x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
  x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

  datasets = [x1, x2, x3, x4]
  labels = [ 'Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist' ]

  # Calculate density for each group
  plot_data = []

  for data, label in zip(datasets, labels):
      ages = data.to_numpy(dtype=float)
      age_range = np.linspace(ages.min(), ages.max(), 300)
      density = gaussian_kde(ages)(age_range)

      plot_data.append(pd.DataFrame({
          'Age': age_range,
          'Density': density,
          'Category': label
      }))

  final_df = pd.concat(plot_data, ignore_index=True)

  # Create graph using Plotly Express
  fig = px.line(
      final_df,
      x='Age',
      y='Density',
      color='Category',
  )
  fig.update_layout(autosize=False, width=1000, height=600)
  st.title("Age Distribution of Athletes and Medalists")
  st.plotly_chart(fig)

  sport_list = df['Sport'].unique().tolist()
  sport_list.sort()
  sport_list.insert(0, 'Overall')

  st.title("Height VS Weight")
  selected_sport = st.selectbox("Select a Sport", sport_list)
  temp_df = helper.weight_v_height(df,selected_sport)
  fig, ax = plt.subplots()

  ax = sns.scatterplot(x=temp_df["Weight"], y=temp_df['Height'],hue=temp_df['Medal'], style=temp_df['Sex'], s=60  )
  st.pyplot(fig)

  st.title('Men Vs Women Participation Over the Years')
  final = helper.men_vs_women(df)
  fig = px.line(final, x='Year', y=['Male', 'Female'])

  fig.update_layout(autosize=False, width=1000, height=600)
  st.plotly_chart(fig)

