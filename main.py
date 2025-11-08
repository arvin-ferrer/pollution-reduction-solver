import streamlit as st
import pandas as pd
import numpy as np
from utils.simplex import SimplexSolver
from time import sleep
from utils.createTableau import createTableau
st.set_page_config(layout="wide", page_title="Test")
@st.cache_data

def loadData():
    # loads CSV data.
    try:
        projectsDF = pd.read_csv('data/projects_matrix.csv')
        targetsDF = pd.read_csv('data/pollutant_targets.csv')
        
        # get the 10 pollutant names from the targets file
        pollutantCols = targetsDF['Pollutant'].tolist()
        
        return projectsDF, targetsDF, pollutantCols
    except FileNotFoundError as e:
        # show error on main page if files not found
        st.error(f"Error loading data: {e}. Make sure 'data' folder and CSV files exist.")
        return None, None, None
# clearing selections
def clearSelections():
    st.session_state.project_selector = []

# loading the dataframe
projectsDF, targetsDF, pollutantCols = loadData()

# streamlit sidebar controls
with st.sidebar:
    st.title("Controls")
    st.markdown("Select mitigation projects and run the solver.")
    
    if projectsDF is not None:
        st.header("1. Select Projects")
        
        project_names_list = projectsDF['Project Name'].tolist()
        
        selected_project_names = st.multiselect(
            "Choose projects to include:",
            options=project_names_list,
            default=project_names_list, # "check all the projects"  by default
            key='project_selector'
        )

        st.button(
            'Reset', 
            on_click=clearSelections,
            help="Deselects all projects.",
            use_container_width=True
        )
        
        st.markdown("---")

        # start button to start solving
        solve_button = st.button(
            "Solve",
            type="primary", 
            use_container_width=True
        )
        st.markdown("---")
        st.header("2. Project Inspector")

        project_to_inspect = st.selectbox(
           "Select a project to view its data:",
        options=project_names_list
        )

        if project_to_inspect:
           projectData = projectsDF[projectsDF['Project Name'] == project_to_inspect]
           st.dataframe(projectData, use_container_width=True)
        else:
           st.error("Data files not found.")
        st.markdown("---")
        st.subheader("About")
        st.info("This app was built for CMSC150 Final Project. \n\n"
            "**Author:** Arvin Ferrer\n\n"
            "**Section:** AB2L")


# main Display page
st.title("City Pollution Reduction Solver")

# only proceed if data was loaded and not null
if projectsDF is not None:
    
    # solver execution (initialize the simplex)
    if solve_button:
        if not selected_project_names:
            st.warning("Please select at least one project from the sidebar.")
        else:
            with st.spinner("Running Simplex Algorithm..."):
                sleep(3)
                try:
                    st.header("2. Solver Results")
                    
                    # initializing tabs
                    tab1, tab2, tab3 = st.tabs(["Optimal Solution", "Simplex Iterations", "Input data"])

                    # fIltering the project name from the selected project names
                    filteredDF = projectsDF[projectsDF['Project Name'].isin(selected_project_names)].copy()
                    filteredDF['Project Name'] = pd.Categorical(filteredDF['Project Name'], categories=selected_project_names, ordered=True)
                    filteredDF = filteredDF.sort_values('Project Name')
                    costVectorC = filteredDF['Costs'].values
                    pollutantMatrix =  filteredDF[pollutantCols].values 
                    targetPollutants = targetsDF.set_index('Pollutant').loc[pollutantCols, 'Target'].values
                    n = len(costVectorC)

                    tableau = createTableau(costVectorC, pollutantMatrix.T, targetPollutants)
                    solver = SimplexSolver()
                    result = solver.solve(tableau, numVars=n, costVectorC=costVectorC)

                   # displaying the result for tab 1
                    with tab1:
                        tableauZ = result['finalTableau'][-1, -1]
                        
                        if result['status'] == 'Infeasible' or tableauZ < -1e9:
                            # st.error("The problem is not feasible.")
                            st.badge("Failed", icon='❌', color='red')
                            st.write("The selected combination of projects doesn't meet the required pollutant reduction targets.")
                        
                        elif result['status'] == 'Optimal':
                            # st.success("Optimal Solution Found")
                            st.badge("Success", icon=':material/check:', color='green') 
                            # create DataFrame using costs from the basic solution
                            solutionDF = pd.DataFrame({
                                'Mitigation Project':   filteredDF['Project Name'].tolist(),
                                'Project Units (x_i)': result['basicSolution'],
                                'Total Cost': result['basicSolution'] * costVectorC
                            })
                            
                            # creating the Chart DataFrame to be use for chart visualization
                            chartDF = solutionDF[solutionDF['Project Units (x_i)'] > 1e-6].copy()

                            # creating the metrics
                            col1, col2 = st.columns(2)
                            col1.metric("Minimum Total Cost (Z)", f"${result['Z']:,.2f}")
                            col2.metric("Projects Implemented", f"{len(chartDF)}")
                            
                            st.subheader("Visual Solution")
                            
                            c1, c2 = st.columns(2)
                            
                            # creating charts from the chart dataframe
                            with c1:
                                st.write("Project Units Implemented")
                                st.bar_chart(chartDF, x='Mitigation Project', y='Project Units (x_i)')
                            with c2:
                                st.write("Cost Breakdown")
                                st.vega_lite_chart(chartDF, {
                                    'mark': {'type': 'arc', 'tooltip': True},
                                    'encoding': {
                                        'theta': {
                                            'field': 'Total Cost', 
                                            'type': 'quantitative', 
                                            'stack': True
                                        },
                                        'color': {
                                            'field': 'Mitigation Project', 
                                            'type': 'nominal',
                                            'title': 'Project'
                                        },
                                        'tooltip': [
                                            {'field': 'Mitigation Project', 'type': 'nominal'},
                                            {'field': 'Total Cost', 'type': 'quantitative', 'format': '$,.2f'}
                                        ]
                                    }
                                }, use_container_width=True)

                            # format the dataframe for Table Display 
                            solutionDFnew = chartDF.copy()
                            solutionDFnew['Project Units (x_i)'] = solutionDFnew['Project Units (x_i)'].map('{:,.4f}'.format)
                            solutionDFnew['Total Cost'] = solutionDFnew['Total Cost'].map('${:,.2f}'.format)
                             
                            st.subheader("Final Project Implementation (Table)")
                            # all_cols = solutionDFnew.columns.tolist()
                            # options = st.multiselect("Select columns to display:", all_cols, default=all_cols)                            # st.dataframe(solutionDFnew, use_container_width=True)
                            # st.dataframe(options, use_container_width=True)
                            st.dataframe(solutionDFnew, use_container_width=True)
                            # setup download button 
                            @st.cache_data
                            def convert_df_to_csv(df):
                                # use the formatted dataframe for the CSV
                                return df.to_csv(index=False).encode('utf-8')

                            csvData = convert_df_to_csv(solutionDFnew)
                            
                            st.download_button(
                                label="Download Solution as CSV",
                                data=csvData,
                                file_name="project_solution.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                    with tab2:
                        st.subheader("Simplex Iterations (Step-by-Step)")
                        
                        tableauList = result.get('tableauList', [])
                        # objRow = result.get('objectiveRowList', [])
                        
                        if not tableauList:
                            st.warning("Iteration list not found in solver result.")
                        else:
                            st.info(f"The solver found the solution in {len(tableauList) - 1} iterations.")
                            with st.expander("Show/Hide All Iteration Tableaus"):
                                for i, tableauSteps in enumerate(tableauList):
                                    st.markdown(f"**Iteration {i}**")
                                    # if i < len(objRow):
                                    #     st.write("Objective Row:")
                                    #     st.dataframe(pd.DataFrame(objRow[i]).T)
                                    st.dataframe(pd.DataFrame(tableauSteps))
                                    st.markdown("---")
                    with tab3:
                            # st.markdown("---")
                        with st.expander("Show Input Data Files", expanded=True):
                            
                            st.subheader("Projects Matrix (`projects_matrix.csv`)")
                            st.dataframe(projectsDF, use_container_width=True)
                            
                            st.subheader("Pollutant Targets (`pollutant_targets.csv`)")
                            st.dataframe(targetsDF, use_container_width=True)

                except Exception as e:
                    st.error(f"An error occurred during solving: {e}")
                    import traceback
                    st.exception(e)
    else:
        # default message on the main page before solving
        st.info("Select projects from the sidebar and click 'Solve' to see the results.")

    # show Input Data 
    # st.markdown("---")
    # with st.expander("Show Input Data Files", expanded=False):
        
    #     st.subheader("Projects Matrix (`projects_matrix.csv`)")
    #     st.dataframe(projectsDF, use_container_width=True)
        
    #     st.subheader("Pollutant Targets (`pollutant_targets.csv`)")
    #     st.dataframe(targetsDF, use_container_width=True)