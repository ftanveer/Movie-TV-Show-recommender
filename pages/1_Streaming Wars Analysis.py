import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


###### Reading Files #########

df_stream = pd.read_csv("df_stream_dir.csv")

###### UX Design #########
def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://img.freepik.com/free-vector/white-abstract-background-design_23-2148825582.jpg?w=1060&t=st=1676006788~exp=1676007388~hmac=5bf80d83aa2bb6bff49a4a7f3d610bc6bfed5d38d68740f9386afaceced56924");
             background-attachment: fixed;
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_bg_from_url()

sns.set_theme()

st.markdown("<h1 style='text-align: center; color: black;'>Streaming Services Analysis</h1>", unsafe_allow_html=True)

st.markdown("#### Objective:")
st.write("Netflix has been a monopoly in the streaming services industry, but now the landscape is shifting and new "
        "platforms are rising up to the competition. We shall look into these different streaming services and "
        "how their contents are different"
        "")



st.write("We shall look into the distribution of content popularity that is not produced in the US ")

fig, axes = plt.subplots(3, 3, figsize=(18, 10))

fig.suptitle(' 3 x 3 axes Box plot with data')

g1 = sns.kdeplot(ax=axes[0, 0], data=df_stream[(df_stream["US"] == 0) & (df_stream["streaming_service"] == 'netflix')],
                 x='imdb_score')
g1.set_title('Netflix')
g1.set(xlabel=None)

g2 = sns.kdeplot(ax=axes[0, 1], data=df_stream[(df_stream["US"] == 0) & (df_stream["streaming_service"] == 'amazon')],
                 x='imdb_score')
g2.set_title('amazon')
g2.set(xlabel=None)

g3 = sns.kdeplot(ax=axes[0, 2], data=df_stream[(df_stream["US"] == 0) & (df_stream["streaming_service"] == 'disney')],
                 x='imdb_score')
g3.set_title('disney')
g3.set(xlabel=None)

g4 = sns.kdeplot(ax=axes[1, 0],
                 data=df_stream[(df_stream["US"] == 0) & (df_stream["streaming_service"] == 'crunchyroll')],
                 x='imdb_score')
g4.set_title('crunchyroll')
g4.set(xlabel=None)

g5 = sns.kdeplot(ax=axes[1, 1], data=df_stream[(df_stream["US"] == 0) & (df_stream["streaming_service"] == 'hulu')],
                 x='imdb_score')
g5.set_title('hulu')
g5.set(xlabel=None)

g6 = sns.kdeplot(ax=axes[1, 2], data=df_stream[(df_stream["US"] == 0) & (df_stream["streaming_service"] == 'hbo')],
                 x='imdb_score')
g6.set_title('hbo')
g6.set(xlabel=None)

g7 = sns.kdeplot(ax=axes[2, 0],
                 data=df_stream[(df_stream["US"] == 0) & (df_stream["streaming_service"] == 'darkmatter')],
                 x='imdb_score')
g7.set_title('darkmatter')

g8 = sns.kdeplot(ax=axes[2, 1],
                 data=df_stream[(df_stream["US"] == 0) & (df_stream["streaming_service"] == 'paramount')],
                 x='imdb_score')
g8.set_title('paramount')

g9 = sns.kdeplot(ax=axes[2, 2], data=df_stream[(df_stream["US"] == 0) & (df_stream["streaming_service"] == 'rakuten')],
                 x='imdb_score')
g9.set_title('rakuten')

st.write(fig)

st.write("How do these streaming services allocate their budgets for their content? We have below a scatterplot "
         "for the budgets of each content grouped by their streaming services."
         "Disney and HBO are the big players when it comes to high budget TV shows/Movies ")

df_budg = df_stream.dropna(subset = ['budget']).copy()
df_budg['budget'] = pd.to_numeric(df_budg['budget'])

df_budg_2 = df_budg[df_budg['budget'] != 0].copy()

decades = pd.cut(df_budg_2["release_year"], bins = [1900, 2000, 2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020],
                labels = ['1900s','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018','2019'])

df_budg_2.insert(5,'decades',decades)


fig2, ax2 = plt.subplots(figsize =(15,15) )
cmap = sns.light_palette("seagreen", as_cmap=True)
ax_budget = sns.stripplot(data = df_budg_2, x = 'streaming_service', y = 'budget', hue = 'decades', palette='coolwarm_r')

st.write(fig2)

#st.pyplot(fig_2.figure)


### Top Country for each streaming service ###

def get_top_countries(text):
    first = text.split(",")[0]

    top_countries = ['US', "JP", "IN", "GB", "KR", "CA", "CN", "FR", "AU", "ES", "DE", "MX"]

    if first in top_countries:
        primary = first
    else:
        primary = 'Other'

    return primary

topstream = df_stream.copy()
topstream['primary_country'] = topstream['production_countries'].apply(get_top_countries)
topstream_grouped = topstream.groupby(['streaming_service', 'primary_country']).size().reset_index(name='counts')
topstream_grouped['percentage of movies'] = topstream_grouped['counts']/topstream_grouped.groupby("streaming_service")['counts'].transform('sum')*100


topstream_grouped = topstream_grouped.astype({"primary_country":'category'})

topstream_grouped["primary_country"] = topstream_grouped["primary_country"].cat.rename_categories({"US": "USA", "MX":"Mexico", "KR": "Korea", "JP":"Japan", "IN": "India", "GB":"Britain",
                                     "FR" : "France", "ES":"Spain", "DE":"Germany", "CN":"China", "CA":"Canada", "AU":"Australia" })

### Plotting country contents in each streaming service###
fig_3, ax_3 = plt.subplots(figsize = (12,12))

labels = topstream_grouped[topstream_grouped["streaming_service"] == "netflix"]["primary_country"]
sizes = topstream_grouped[topstream_grouped["streaming_service"] == "netflix"]["percentage of movies"]


sns.set_palette('muted')
ax_3.pie(sizes, labels = labels,  startangle=90, radius=1, counterclock=False, wedgeprops=dict(width=0.3, edgecolor='black'))



centre_circle = plt.Circle((0,0),0.75,color='black', fc='white',linewidth=1.25)
fig_3 = plt.gcf()
fig_3.gca().add_artist(centre_circle)




legend_elements = [f"{labels}: {round(sizes,2)}" for labels, sizes in zip(labels, sizes)]

ax_3.legend(legend_elements, loc='upper right', bbox_to_anchor=(0.0, 1.0), fontsize=10)

plt.title("Netflix")

st.write(fig_3)