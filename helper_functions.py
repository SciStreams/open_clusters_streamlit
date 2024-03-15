import streamlit as st

from collections import defaultdict

import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from plotly.subplots import make_subplots

import pandas as pd
import os

# Local
# @st.cache_data
# def load_data_clusters():

#     file = './Data/clusters.csv'
#     df = pd.read_csv(file)

#     return df

# @st.cache_data
# def load_data_members():

#     file = './Data/filtered_members_round.csv'
#     df = pd.read_csv(file)

#     return df

# Online
@st.cache_data
def load_data_clusters():
    file_url = "https://raw.githubusercontent.com/SciStreams/open_clusters_streamlit/main/data/clusters.csv"
    
    response = requests.get(file_url)
    
    if response.status_code == 200:

        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)
        return df
    else:
        st.error(f"Failed to load data. Status code: {response.status_code}")
        return None

@st.cache_data
def load_data_members():

    file_url = "https://raw.githubusercontent.com/SciStreams/open_clusters_streamlit/main/data/filtered_members_round.csv"
    
    response = requests.get(file_url)
    
    if response.status_code == 200:

        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)
        return df
    else:
        st.error(f"Failed to load data. Status code: {response.status_code}")
        return None

def extract_groups(df, kind):

    # Dictionary
    groups = defaultdict(list)

    kind_map = {
        'Open Clusters': 'o',
        'Globular Clusters': 'g',
        'Moving Groups': 'm'
    }
    
    kind_ = kind_map[kind]

    for name in df['name'][df['kind']==f'{kind_}']:
        # Group name
        group_name = name.split('_')[0]

        groups[group_name].append(name)

    return groups


def individual_object(df, kind, catalogue):

    kind_map = {
        'Open Clusters': 'o',
        'Globular Clusters': 'g',
        'Moving Groups': 'm'
    }
    

    kind_ = kind_map[kind]

    mask_kind = df['kind'] == kind_
    

    if catalogue is None:
        mask_catalogue = pd.Series(True, index=df.index)

    else:
        mask_catalogue = df['name'].str.startswith(tuple(catalogue))

    df_individual = df[mask_kind & mask_catalogue]

    return df_individual


def make_circle(center_lon, center_lat, radius):
    # Define the angles for the circle
    angles = np.linspace(0, 2*np.pi, 100)

    # Calculate the coordinates of the circle points
    circle_lon = center_lon + radius * np.cos(angles)
    circle_lat = center_lat + radius * np.sin(angles)

    # Create trace for the circle
    circle_trace = go.Scatter(
        x=circle_lon,
        y=circle_lat,
        mode='lines',
        line=dict(color='#dd3497', width=2),
        showlegend=False,
        name='',
        #fill='toself',  # Fills the area enclosed by the circle
        #name='Circle'
    )

    return circle_trace

def plot_object(df_members, cat_type=None, selected_sub_cat=None, cat_names=None, filtered_df_1_probable=None, remove_non_members=None, draw_circle=None):

    fig = px.scatter(df_members, x='l', y='b', labels={'l': 'Galactic Longitude', 'b': 'Galactic Latitude'})
    fig.update_traces(marker=dict(color='#878787'))

    #circle = plot_circle(center_lon, center_lat, radius)

    if remove_non_members and filtered_df_1_probable is not None:
        fig = px.scatter(df_members, x='l', y='b', labels={'l': 'Galactic Longitude', 'b': 'Galactic Latitude'})
        fig.update_traces(marker=dict(size=5, color='#dd3497'))#non members
        fig.add_scatter(x=filtered_df_1_probable['l'], y=filtered_df_1_probable['b'], mode='markers', 
                    marker=dict(color='#878787'),name='', showlegend=False) #name='Selected Sub-categories' ; name='' to remove empty trace 1 in hover 
        if draw_circle is not None:
            # Add circle to the plot
            fig.add_trace(draw_circle)
        #fig.update_layout(autosize=False, width=800, height=300, margin=dict(l=40, r=40, t=40, b=40))

    #fig.update_layout(title=f"Test")


    # This plots only cluster positions, not members
    if cat_type in ["Open Clusters", "Globular Clusters", "Moving Groups"]:
        #st.dataframe(df_members)
        fig = px.scatter(df_members, x='l', y='b', labels={'l': 'Galactic Longitude', 'b': 'Galactic Latitude'},
                     color='log_age_84', color_continuous_scale='Viridis',
                     color_continuous_midpoint=df_members['log_age_84'].median())
        fig.update_traces(hovertemplate='Galactic Longitude: %{x}<br>Galactic Latitude: %{y}<br>Name: %{text}', 
                  text=df_members['name'])
        fig.update_traces(marker=dict(size=4))
        fig.update_layout(title=f"{cat_type}")

    # This plots all cluster members
    if cat_type == "All Objects":

        fig.update_traces(marker=dict(size=2))
        fig.update_traces(hovertemplate='Galactic Longitude: %{x}<br>Galactic Latitude: %{y}<br>Name: %{text}', 
                      text=df_members['name'])

        # Dynamical title for plot
        combine_names = ', '.join(map(str, cat_names))
        if len(cat_names) == 1:
            selected_cats = 'Selected Catalogue: ' + combine_names
        else:
            selected_cats = 'Selected Catalogues: ' + combine_names
        fig.update_layout(title=f"{selected_cats}")


        if selected_sub_cat is not None:
            # get all catalogue cluster points

            fig = px.scatter(df_members, x='l', y='b', labels={'l': 'Galactic Longitude', 'b': 'Galactic Latitude'})
            fig.update_traces(marker=dict(size=1, color='#878787'))


            df_members_sorted = df_members[df_members['name'].isin(selected_sub_cat)].sort_values(by='name')
            
            # will update individual cluster on catalog cluster plot (highlights)
            fig.add_scatter(x=df_members_sorted['l'], y=df_members_sorted['b'], mode='markers', 
                        marker=dict(color='#fc4e2a'), hovertemplate='Galactic Longitude: %{x}<br>Galactic Latitude: %{y}<br>Name: %{text}', 
                        text=df_members_sorted['name'],name='', showlegend=False) #name='Selected Sub-categories' ; name='' to remove empty trace 1 in hover 
            
        
            fig.update_traces(hovertemplate='Galactic Longitude: %{x}<br>Galactic Latitude: %{y}<br>Name: %{text}', 
                          text=df_members['name'])
            selected_cats = 'Selected Catalogues: ' + ', '.join(map(str, cat_names))
            fig.update_layout(title=f"{selected_cats}")



    return fig
    #st.plotly_chart(fig)



def add_plot_title(sub_cat):
    combine_names = ', '.join(map(str, sub_cat))
    if len(sub_cat) == 1:
        selected_obj = 'Selected Object: ' + combine_names
    else:
        selected_obj = 'Selected Objects: ' + combine_names

    return selected_obj



def plot_circle(center_lon, center_lat, radius):
    # Define the angles for the circle
    angles = np.linspace(0, 2*np.pi, 100)

    # Calculate the coordinates of the circle points
    circle_lon = center_lon + radius * np.cos(angles)
    circle_lat = center_lat + radius * np.sin(angles)

    # Plot the circle
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=circle_lon,
        y=circle_lat,
        mode='lines',
        line=dict(color='blue', width=2),
        fill='toself',  # Fills the area enclosed by the circle
        name='Circle'
    ))

    # Add center point
    fig.add_trace(go.Scatter(
        x=[center_lon],
        y=[center_lat],
        mode='markers',
        marker=dict(color='red', size=5),
        name='Center'
    ))

    # Set layout
    fig.update_layout(
        title='Circle with Given Radius',
        xaxis=dict(title='Galactic Longitude'),
        yaxis=dict(title='Galactic Latitude'),
        showlegend=False
    )

    # Show the plot
    return fig

    # Example usage
    #center_lon = 0  # Example center longitude
    #center_lat = 0  # Example center latitude
    #radius = 10     # Example radius
    #plot_circle(center_lon, center_lat, radius)


def plot_cmd(df):
    
    # if multiple objects are selected
    custom_colors = ['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99','#b15928']


    fig = px.scatter(df, x='bp_rp', y='phot_g_mean_mag', color='name',
                     labels={'bp_rp': 'BP - RP', 'phot_g_mean_mag': 'Phot G Mean Mag'},
                     color_discrete_sequence = custom_colors) #px.colors.qualitative.Safe) 

    # Update layout
    fig.update_layout(
        title="Color-magnitude diagram",
        xaxis_title="BP - RP",
        yaxis_title="Phot G Mean Mag",
        yaxis=dict(autorange="reversed")
    )

    return fig

def papers_citation():
    paper_3 = """ 

@ARTICLE{2024arXiv240305143H,
       author = {{Hunt}, Emily L. and {Reffert}, Sabine},
        title = "{Improving the open cluster census. III. Using cluster masses, radii, and dynamics to create a cleaned open cluster catalogue}",
      journal = {arXiv e-prints},
     keywords = {Astrophysics - Astrophysics of Galaxies, Astrophysics - Solar and Stellar Astrophysics},
         year = 2024,
        month = mar,
          eid = {arXiv:2403.05143},
        pages = {arXiv:2403.05143},
          doi = {10.48550/arXiv.2403.05143},
archivePrefix = {arXiv},
       eprint = {2403.05143},
 primaryClass = {astro-ph.GA},
       adsurl = {https://ui.adsabs.harvard.edu/abs/2024arXiv240305143H},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}

            """

    paper_2 ="""
@ARTICLE{2023A&A...673A.114H,
       author = {{Hunt}, Emily L. and {Reffert}, Sabine},
        title = "{Improving the open cluster census. II. An all-sky cluster catalogue with Gaia DR3}",
      journal = {\aap},
     keywords = {open clusters and associations: general, methods: data analysis, catalogs, astrometry, Astrophysics - Astrophysics of Galaxies, Astrophysics - Instrumentation and Methods for Astrophysics},
         year = 2023,
        month = may,
       volume = {673},
          eid = {A114},
        pages = {A114},
          doi = {10.1051/0004-6361/202346285},
archivePrefix = {arXiv},
       eprint = {2303.13424},
 primaryClass = {astro-ph.GA},
       adsurl = {https://ui.adsabs.harvard.edu/abs/2023A&A...673A.114H},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}
        """

    paper_1 = """ 
@ARTICLE{2021A&A...646A.104H,
       author = {{Hunt}, Emily L. and {Reffert}, Sabine},
        title = "{Improving the open cluster census. I. Comparison of clustering algorithms applied to Gaia DR2 data}",
      journal = {\aap},
     keywords = {methods: data analysis, open clusters and associations: general, astrometry, Astrophysics - Astrophysics of Galaxies, Astrophysics - Solar and Stellar Astrophysics},
         year = 2021,
        month = feb,
       volume = {646},
          eid = {A104},
        pages = {A104},
          doi = {10.1051/0004-6361/202039341},
archivePrefix = {arXiv},
       eprint = {2012.04267},
 primaryClass = {astro-ph.GA},
       adsurl = {https://ui.adsabs.harvard.edu/abs/2021A&A...646A.104H},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}

        """
    return paper_1, paper_2, paper_3