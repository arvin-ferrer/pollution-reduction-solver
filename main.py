import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from utils.simplex import SimplexSolver
from time import sleep

from utils.createTableau import createTableau
st.set_page_config(layout="wide", page_title="ReductionPlan")
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

# loading the dataframe
projectsDF, targetsDF, pollutantCols = loadData()

# streamlit sidebar controls
with st.sidebar:
    st.title("Controls")
    st.markdown("Select mitigation projects and run the solver.")
    
    if projectsDF is not None:
        st.header("1. Select Projects")
        
        project_names_list = projectsDF['Project Name'].tolist()
        def selectAll():
            st.session_state.project_selector = project_names_list

        def clearSelections():
            st.session_state.project_selector = []
            if 'solution_result' in st.session_state:
                st.session_state.solution_result = None

        selected_project_names = st.multiselect(
            "Choose projects to include:",
            options=project_names_list,
            default=project_names_list, # "check all the projects"  by default
            key='project_selector'
        )
        col1, col2 = st.columns(2)
        with col1:
            st.button(
                'Reset', 
                on_click=clearSelections, # Pass the function NAME
                help="Deselects all projects.",
                use_container_width=True
            )
        
        with col2:
            st.button(
                'Select All',
                on_click=selectAll, # Pass the function NAME
                help="Selects all projects.",
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
        # --- NEW METRICS ---
# --- END OF NEW METRICS ---
        if not selected_project_names:
            st.warning("Please select at least one project from the sidebar.")

        else:
            with st.spinner("Running Simplex Algorithm..."):
                sleep(3)
                try:
                    st.header("2. Solver Results")
                    
                    # initializing tabs
                    # tab1, tab2, tab3 = st.tabs(["Optimal Solution", "Simplex Iterations", "Input data"])

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
                    st.session_state.solution_result = {
                        "result": result,
                        "filteredDF": filteredDF,
                        "costVectorC": costVectorC,
                        "pollutantMatrix": pollutantMatrix,
                        "targetPollutants": targetPollutants,
                        "n_vars": n
                    }

                except Exception as e:
                    st.error(f"An error occurred during solving: {e}")
                    import traceback
                    st.exception(e)
    if 'solution_result' in st.session_state and st.session_state.solution_result is not None:
        result = st.session_state.solution_result["result"]
        filteredDF = st.session_state.solution_result["filteredDF"]
        costVectorC = st.session_state.solution_result["costVectorC"]
        pollutantMatrix = st.session_state.solution_result["pollutantMatrix"]
        targetPollutants = st.session_state.solution_result["targetPollutants"]
        n = st.session_state.solution_result["n_vars"]
                  # displaying the result for tab 1
        tab1, tab2, tab3 = st.tabs(["Optimal Solution", "Simplex Iterations", "Input data"])
        with tab1:
            tableauZ = result['finalTableau'][-1, -1]
            
            if result['status'] == 'Infeasible' or tableauZ < -1e9:
                # st.error("The problem is not feasible.")
                st.badge("Failed", icon='❌', color='red')
                st.write("The selected combination of projects doesn't meet the required pollutant reduction targets.")
                
                # st.subheader("Feasibility Analysis")
                # max_units = np.full(n, 20.0) # Assume 20 units for all
                # achieved_reduction = pollutantMatrix.T @ max_units
                
                # report_df = pd.DataFrame({
                #     'Pollutant': pollutantCols,
                #     'Target': targetPollutants,
                #     'Max Possible Reduction': achieved_reduction,
                #     'Shortfall': targetPollutants - achieved_reduction
                # })
                # report_df = report_df[report_df['Shortfall'] > 1e-6]
                # report_df['Shortfall'] = report_df['Shortfall'].map('{:,.2f}'.format)
                
                # st.warning("The following targets were missed:")
                # st.dataframe(report_df, use_container_width=True)

            elif result['status'] == 'Optimal':
                # st.success("Optimal Solution Found")
                st.badge("Success", icon=':material/check:', color='green') 
                # create DataFrame using costs from the basic solution
                solutionDF = pd.DataFrame({
                    'Mitigation Project':   filteredDF['Project Name'].tolist(),
                    'Project Units (x_i)': result['basicSolution'],
                    'Total Cost': result['basicSolution'] * costVectorC
                })
                        
                solution_vector = result['basicSolution']
                pollutant_matrix_full = st.session_state.solution_result["pollutantMatrix"] 
                
                achieved_reduction = solution_vector @ pollutant_matrix_full
                
                target_df_indexed = targetsDF.set_index('Pollutant')
                reduction_report = pd.DataFrame({
                    'Pollutant': pollutantCols,
                    'Required Target': target_df_indexed.loc[pollutantCols, 'Target'],
                    'Achieved Reduction': achieved_reduction
                })
                
                reduction_report_melted = reduction_report.melt('Pollutant', var_name='Type', value_name='Amount')

                chart = alt.Chart(reduction_report_melted).mark_bar().encode(
                    # X-axis is the Pollutant
                    x=alt.X('Pollutant', title='Pollutant'),
                    
                    # Y-axis is the Amount
                    y=alt.Y('Amount', title='Reduction (tons)'),
                    
                    # Color by Type (Target vs. Achieved)
                    color=alt.Color('Type', title='Metric'), 
                    xOffset='Type',
                    tooltip=['Pollutant', 'Type', 'Amount']
                ).properties(
                    title='Required Target vs. Achieved Reduction'
                ).interactive() # Makes it zoomable/pannable
                
                st.altair_chart(chart, use_container_width=True)
                
                
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
                st.markdown("---")
                st.subheader("Final Project Implementation (Table)")
                allCol = solutionDFnew.columns.tolist()
                options = st.multiselect("Select columns to display:", allCol, default=allCol)
                st.dataframe(solutionDFnew[options], use_container_width=True)

                # allCol = solutionDFnew.columns.tolist()
                # options = st.multiselect("Select columns to display:", allCol, default=allCol)                            # st.dataframe(solutionDFnew, use_container_width=True)
                # st.dataframe(options, use_container_width=True)
                # st.dataframe(solutionDFnew, use_container_width=True)
                # setup download button 
                # ... inside 'elif result['status'] == 'Optimal': ...
                        
                        # --- 1. CALCULATE ACHIEVED REDUCTION ---
                        # Get the raw solution vector and the pollutant matrix
               
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
            basicSolutions = result.get('basicSolutions', [])
            
            if not tableauList:
                st.warning("Iteration list not found in solver result.")
            else:
                st.info(f"The solver found the solution in {len(tableauList) - 1} iterations.")
                with st.expander("Show/Hide All Iteration Tableaus"):
                    for i, tableauSteps in enumerate(tableauList):
                        st.markdown(f"**Iteration {i}**")
                        if i < len(basicSolutions):
                            st.write("Basic Solution:")
                            st.dataframe(pd.DataFrame([basicSolutions[i]], columns=[f"x{j+1}" for j in range(len(basicSolutions[i]))]))       
                            st.dataframe(pd.DataFrame(tableauSteps))
                        st.markdown("---")
        with tab3:
                # st.markdown("---")
            with st.expander("Show Input Data Files", expanded=True):
                
                st.subheader("Projects Matrix (`projects_matrix.csv`)")
                st.dataframe(projectsDF, use_container_width=True)
                
                st.subheader("Pollutant Targets (`pollutant_targets.csv`)")
                st.dataframe(targetsDF, use_container_width=True)

                # except Exception as e:
                #     st.error(f"An error occurred during solving: {e}")
                #     import traceback
                #     st.exception(e)
    else:
        # default message on the main page before solving
        st.info("Select projects from the sidebar and click 'Solve' to see the results.")
        st.subheader("Problem Overview")

        # Get the number of projects the user has currently selected
        num_selected = len(selected_project_names)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Projects Available", len(projectsDF))
        col2.metric("Pollutants to Target", len(targetsDF))
        col3.metric("Projects Selected for Run", f"{num_selected}")
    
        st.markdown("---")
        st.subheader("Welcome to the City Pollution Reduction Solver")
        st.markdown("""
        This application finds the most cost-effective (minimum cost) solution 
        to meet the city's 10 pollutant reduction targets.
        
        **How to use:**
        1.  Use the **sidebar** to select the projects you want to include.
        2.  Click the **Solve** button.
        3.  Analyze the results in the **Optimal Solution** tab.
        4.  Click the **Simplex Iterations** to view the tableau and basic solution for each iteration.
        5.  Click the **Input data** to view the csv files.
        """)
        st.markdown("---")