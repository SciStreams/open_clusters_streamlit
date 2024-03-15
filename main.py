import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from helper_functions import load_data_clusters, load_data_members, extract_groups, individual_object,\
							 plot_object, add_plot_title, plot_circle, make_circle, plot_cmd, papers_citation

with st.sidebar:
	sel_options = st.radio("Select Options", ['Sample of Clusters', 'References'])



if sel_options == "Sample of Clusters":
	st.header("Improving the open cluster census")


	df = load_data_clusters()
	#st.dataframe(df)
	#st.write(df.columns)


	df_members = load_data_members()
	#st.write(df_members.columns)


	#st.write(df['kind'].unique()) # what is "d"-62--too distant and "r"-17--rejected 
	with st.sidebar:
		kind = st.radio("Cluster Type", ("Open Clusters", "Globular Clusters", "Moving Groups"))

	    # Check if kind has changed
		if st.session_state.get('kind') != kind:
			# Clear previous_catalogue_selection if kind has changed
			st.session_state['catalogue_selection'] = None

		# Update session state with the current kind
		st.session_state['kind'] = kind

		if 'catalogue_selection' not in st.session_state:
			st.session_state['catalogue_selection'] = None
		previous_catalogue_selection = st.session_state['catalogue_selection']
	if kind != "Globular Clusters":
		with st.sidebar:
			age = st.slider("Log Age (84)", min(df['log_age_84']), max(df['log_age_84']), (min(df['log_age_84']), max(df['log_age_84'])))


	if kind == "Open Clusters":
		df_filtered = df[ (df['kind']=='o') & (df['log_age_84']>=age[0]) & (df['log_age_84']<=age[1]) ]
	if kind == "Globular Clusters": #Vasiliev&Baumgardt21
		df_filtered = df[ (df['kind']=='g') ]
	if kind == "Moving Groups":
		df_filtered = df[ (df['kind']=='m') & (df['log_age_84']>=age[0]) & (df['log_age_84']<=age[1]) ]


	
	groups = extract_groups(df_filtered, kind)
	with st.sidebar:
		if previous_catalogue_selection is not None:
			catalogue_selection = st.multiselect("Catalogue", groups.keys(), default=previous_catalogue_selection)
		else:
			catalogue_selection = st.multiselect("Catalogue", groups.keys())
		st.session_state['catalogue_selection'] = catalogue_selection

		if catalogue_selection:
			catalogue = catalogue_selection
		else:
			catalogue = None

	# it catalogue is None, then cat_df gets all objects with selected 'kind' type
	cat_df = individual_object(df_filtered, kind, catalogue)
	
	cat_names = cat_df['name'].tolist()

	with st.sidebar:
		sub_cat = st.multiselect( 'Objects in this catalogue', cat_df['name'].unique())

	if kind == "Globular Clusters":
		st.write("*No info. on Age*")
	plot_here = st.empty()
	fig_kind = plot_object(df_filtered, f"{kind}")
	plot_here.plotly_chart(fig_kind)

	# We plot only if catalogue is selected
	if catalogue:
		filtered_df = df_members[df_members['name'].isin(cat_names)]

		fig_1 = plot_object(filtered_df, "All Objects", None, catalogue)
		plot_here.plotly_chart(fig_1)


	if sub_cat:
		with st.sidebar:
			remove_non_members = st.checkbox("Mark non-members with pink (prob. memb. <50%)")
			if len(sub_cat) == 1:
				show_jacobi_radius = st.checkbox("Show Jacobi radius")
			else:
				show_jacobi_radius = st.checkbox("Show Jacobi radius", disabled=True)


		# Filter the DataFrame based on selected sub_cat
		filtered_df_1 = df_members[df_members['name'].isin(sub_cat)]
		#if len(sub_cat) == 1:
		if remove_non_members or show_jacobi_radius:
			filtered_df_1_probable =  df_members[(df_members['probability']>=0.50) & df_members['name'].isin(sub_cat)]

		plot_here_2 = st.empty()
		fig_2 = plot_object(filtered_df_1)

		plt_title = add_plot_title(sub_cat)

		fig_2.update_layout(title=f"{plt_title}")
		#st.plotly_chart(fig_2)
		plot_here_2.plotly_chart(fig_2)

		fig_1 = plot_object(filtered_df, "All Objects", sub_cat, catalogue)
		plot_here.plotly_chart(fig_1)
		
		#st.dataframe(filtered_df)
		#st.dataframe(cat_df[cat_df['name'].isin(sub_cat)].T, width=500) #ang_radius_jacobi
		#st.dataframe(filtered_df_1)

		if len(sub_cat) == 1 and show_jacobi_radius:
			for_rad = cat_df[cat_df['name'].isin(sub_cat)]
			center_lon = for_rad['l'].tolist()
			center_lat = for_rad['b'].tolist()
			radius = for_rad['ang_radius_jacobi'].tolist()
			circle = make_circle(center_lon, center_lat, radius)
		#st.write(circle)
		#f = plot_circle(center_lon, center_lat, radius)
		#st.plotly_chart(f)

		if remove_non_members:
			fig_2 = plot_object(df_members=filtered_df_1, filtered_df_1_probable=filtered_df_1_probable, remove_non_members="True")
			fig_2.update_layout(title=f"{plt_title}")
			plot_here_2.plotly_chart(fig_2)

		if len(sub_cat) == 1 and show_jacobi_radius:
			fig_2 = plot_object(df_members=filtered_df_1, filtered_df_1_probable=filtered_df_1_probable, remove_non_members="True", draw_circle=circle)
			fig_2.update_layout(title=f"{plt_title}")
			plot_here_2.plotly_chart(fig_2)
			st.write("*Since we are not using projections, circle with Jacobi radius can appear as elipse.*")

		#circle = plot_circle(center_lon, center_lat, radius)

		# Show info of this cluster:
		cat_df = cat_df.round(2)
		transposed_df = cat_df[cat_df['name'].isin(sub_cat)].T
		if "Unnamed: 0" in transposed_df.index:
		    transposed_df = transposed_df.drop("Unnamed: 0")

		# name as header
		transposed_df.columns = transposed_df.iloc[0]
		transposed_df = transposed_df.drop("name")
		combine_names = ', '.join(map(str, sub_cat))
		

		with st.sidebar:
			details_table = st.checkbox("Display Details For Selected Object(s)")
		if details_table:
			st.dataframe(transposed_df, use_container_width=True)

		# Additional Plots
		#st.dataframe(filtered_df_1)

		with st.sidebar:
			display_cmd = st.checkbox("Display Color-Magnitude Diagram")
		
		if display_cmd:
			st.subheader(f"Information on: {combine_names}")
			f = plot_cmd(filtered_df_1)
			st.plotly_chart(f)
			if len(filtered_df_1['name'].unique()) > 10:
				st.write('*Colors will restart cycle because you selected more than 10 Objects.*')


if sel_options == "References":
	st.header("References")
	st.markdown(
		"""Based on the research on '**Improving the open cluster census**' by Hunt et al.:\\
		1) [2020: Comparison of clustering algorithms applied to Gaia DR2 data](https://arxiv.org/pdf/2012.04267.pdf)\\
		2) [2023: An all-sky cluster catalogue with Gaia DR3](https://arxiv.org/pdf/2303.13424.pdf)\\
		3) [2024: Using cluster masses, radii, and dynamics to create a cleaned open cluster catalogue](https://arxiv.org/abs/2403.05143)
	""")

	st.write("")
	st.write(""" 
		Data made publicly accessible by [Hunt et al. (2024)](https://arxiv.org/abs/2403.05143). *See link in the comment section on their arXiv page.*
		""")
	st.write("""
	*For this app, we made several modifications to the original data in order to reduce the size of the 'members.csv' file as listed below.
	 To 'clusters.csv' only rounding to 2 decimal places was applied for display.*
	 """)
	st.write("**Modifications:**")
	st.write(" 1) Float values are rounded to 2 decimal places 'df.round(2)'.")
	st.write(" 2) Too distant and rejected objects are removed (where 'kind' equals to 'g' or 'r'). ")
	st.write(" 3) Column 'phot_variable_flag' values are converted: 'NOT_AVAILABLE' to 'nan' and 'VARIABLE' to 'Y' ")
	st.write(" 4) Most of the columns from the original data file are removed as we are not using them in this app. ")
	st.write("")

	st.write(""" 
		This Streamlit application is made by SciStreams, code of the app can be found on [**GitHub**](https://github.com/SciStreams).
		""")
	st.write("")
	st.write("If you find this app useful in your research, please cite original paper:")
	
	paper1, paper2, paper3 = papers_citation()

	tab3, tab2, tab1 = st.tabs(["Paper 3", "Paper 2", "Paper 1"])
	
	with tab3:
		st.code(paper3)
	with tab2:
		st.code(paper2)
	with tab1:
		st.code(paper1)


with st.sidebar:
	st.write("")
	st.write("")
	st.write("")
	st.write("")
	st.write("")
	st.write("")
	st.write("")
	st.write("")

	st.sidebar.info(
		"""This Streamlit app showcase data from series of research papers on "Improving the open cluster census" by [Hunt et al. (2024)](https://arxiv.org/abs/2403.05143)
		"""
		)


	col1, col2 = st.columns([0.7,0.2])
	with col1:

		st.markdown('''
	    <a href="https://scistreams.github.io">
	        <img src="https://scistreams.github.io/images/SciStreams.png" width="150" />
	    </a>''',
	    unsafe_allow_html=True
		)
		st.markdown('App made by [**SciStreams**](https://scistreams.github.io/)')