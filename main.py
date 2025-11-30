import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from utils.simplex import SimplexSolver
from utils.createTableau import createTableau
from time import sleep
st.set_page_config(layout="wide", page_title="ReductionSolver")

# function to load data
@st.cache_data
def loadData():
    try:
        projectsDF = pd.read_csv('data/projects_matrix.csv')
        targetsDF = pd.read_csv('data/pollutant_targets.csv')
        pollutantCols = targetsDF['Pollutant'].tolist()
        return projectsDF, targetsDF, pollutantCols
    except FileNotFoundError as e: # if those csv files doesnt exists
        st.error(f"Error loading data: {e}. Make sure 'data' folder and CSV files exist.")
        return None, None, None
# resetting fuction
def clearSelections():
    st.session_state.project_selector = []
    # clear results in reset
    if 'solution_result' in st.session_state:
        st.session_state.solution_result = None

# load the data
projectsDF, targetsDF, pollutantCols = loadData()

# sidebar controls
with st.sidebar:
    st.markdown("Select mitigation projects and run the solver.")
    # selection of projects    
    if projectsDF is not None:
        st.header("1. Select Projects")
        project_names_list = projectsDF['Project Name'].tolist()
        
        def selectAll():
            st.session_state.project_selector = project_names_list

        selected_project_names = st.multiselect(
            "Choose projects to include:",
            options=project_names_list,
            default=project_names_list,
            key='project_selector'
        )
        # organizing buttons to columns
        col1, col2 = st.columns(2)
        with col1:
            st.button('Reset', on_click=clearSelections, use_container_width=True)
        with col2:
            st.button('Select All', on_click=selectAll, use_container_width=True)
        
        st.markdown("---")
        solve_button = st.button("Solve", type="primary", use_container_width=True)
        # another section for individual inspection of a project
        st.markdown("---")
        st.header("2. Project Inspector")
        project_to_inspect = st.selectbox("Select a project to view its data:", options=project_names_list)
        if project_to_inspect:
            projectData = projectsDF[projectsDF['Project Name'] == project_to_inspect]
            st.dataframe(projectData, use_container_width=True)
        # about section            
        st.markdown("---")
        st.subheader("About")
        st.info("CMSC150 Final Project\n\n**Author:** Arvin Ferrer\n\n**Section:** AB2L")


# main display
st.title("City Pollution Reduction Solver")

if projectsDF is not None:
    
    # run solve if clicked
    if solve_button:
        if not selected_project_names:
            st.warning("Please select at least one project from the sidebar.")
        else:
            with st.spinner("Running Simplex Algorithm..."):
                sleep(2) # waiting time loading
                try:
                    # filter the data
                    filteredDF = projectsDF[projectsDF['Project Name'].isin(selected_project_names)].copy()
                    filteredDF['Project Name'] = pd.Categorical(filteredDF['Project Name'], categories=selected_project_names, ordered=True)
                    filteredDF = filteredDF.sort_values('Project Name')
                    
                    # prepare data(matrices)
                    costVectorC = filteredDF['Costs'].values
                    pollutantMatrix =  filteredDF[pollutantCols].values 
                    targetPollutants = targetsDF.set_index('Pollutant').loc[pollutantCols, 'Target'].values
                    n = len(costVectorC)

                    # create the tableau
                    tableau = createTableau(costVectorC, pollutantMatrix.T, targetPollutants)
                    solver = SimplexSolver()
                    result = solver.solve(tableau, numVars=n, costVectorC=costVectorC)
                    
                    # save to session state
                    st.session_state.solution_result = {
                        "result": result,
                        "filteredDF": filteredDF,
                        "costVectorC": costVectorC,
                        "pollutantMatrix": pollutantMatrix, # save matrix
                        "targetPollutants": targetPollutants,
                        "n_vars": n,
                        "pollutantCols": pollutantCols
                    }

                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    st.session_state.solution_result = None

    # display results
    if 'solution_result' in st.session_state and st.session_state.solution_result is not None:
        
        # extract the data
        data = st.session_state.solution_result
        result = data["result"]
        filteredDF = data["filteredDF"]
        costVectorC = data["costVectorC"]
        pollutantMatrix = data["pollutantMatrix"]
        targetPollutants = data["targetPollutants"]
        n_vars = data["n_vars"]
        p_cols = data["pollutantCols"]

        st.header("2. Solver Results")
        tab1, tab2, tab3, tab4 = st.tabs(["Optimal Solution", "Simplex Iterations", "Input Data", "About"])

        # optimal Solution 
        with tab1:
            tableauZ = result['finalTableau'][-1, -1]
            
            # check if feasible
            if result['status'] == 'Infeasible' or tableauZ < -1e8:
                st.error("The problem is not feasible.")
                st.write("The selected projects cannot meet the reduction targets.")
                
                # show what failed if not feasible
                st.subheader("Feasibility Table")
                max_units = np.full(n_vars, 20.0) 
                max_reduction = pollutantMatrix.T @ max_units
                
                report_df = pd.DataFrame({
                    'Pollutant': p_cols,
                    'Target': targetPollutants,
                    'Achieved': max_reduction,
                    'Shortfall': targetPollutants - max_reduction
                })
                report_df = report_df[report_df['Shortfall'] > 1e-6]
                st.warning("These pollutants failed to meet targets:")
                st.dataframe(report_df, use_container_width=True)

            elif result['status'] == 'Optimal':
                st.success("Optimal Solution Found!")
                
                # build the dataframe for visualization/analysis
                solutionDF = pd.DataFrame({
                    'Mitigation Project': filteredDF['Project Name'].tolist(),
                    'Project Units (x_i)': result['basicSolution'],
                    'Total Cost': result['basicSolution'] * costVectorC
                })
                
                chartDF = solutionDF[solutionDF['Project Units (x_i)'] > 1e-6].copy()

                # metrics for the visualization
                col1, col2 = st.columns(2)
                col1.metric("Minimum Total Cost (Z)", f"${result['Z']:,.2f}")
                col2.metric("Projects Implemented", f"{len(chartDF)}")
                
                # create the visualization
                st.subheader("Visual Solution")
                c1, c2 = st.columns(2)
                with c1:
                    st.write("**Units Implemented**")
                    st.bar_chart(chartDF, x='Mitigation Project', y='Project Units (x_i)')
                with c2:
                    st.write("**Cost Breakdown**")
                    st.vega_lite_chart(chartDF, {
                        'mark': {'type': 'arc', 'tooltip': True},
                        'encoding': {
                            'theta': {'field': 'Total Cost', 'type': 'quantitative'},
                            'color': {'field': 'Mitigation Project', 'type': 'nominal'},
                            'tooltip': [{'field': 'Mitigation Project'}, {'field': 'Total Cost', 'format': '$,.2f'}]
                        }
                    }, use_container_width=True)

                # pollutant analysis chart
                st.subheader("Pollutant Reduction Analysis")
                achieved = result['basicSolution'] @ pollutantMatrix
                
                target_df_indexed = targetsDF.set_index('Pollutant')
                red_df = pd.DataFrame({
                    'Pollutant': p_cols,
                    'Target': target_df_indexed.loc[p_cols, 'Target'],
                    'Achieved': achieved
                }).melt('Pollutant', var_name='Type', value_name='Amount')
                
                chart = alt.Chart(red_df).mark_bar().encode(
                    x=alt.X('Pollutant', title='Pollutant'),
                    y=alt.Y('Amount', title='Reduction (tons)'),
                    color=alt.Color('Type', title='Metric'),
                    xOffset='Type', # groups bars side-by-side
                    tooltip=['Pollutant', 'Type', 'Amount']
                ).properties(title='Target vs Achieved').interactive()
                
                st.altair_chart(chart, use_container_width=True)

                # final table with selection
                st.subheader("Implementation Plan")
                displayDF = chartDF.copy()
                displayDF['Project Units (x_i)'] = displayDF['Project Units (x_i)'].map('{:,.4f}'.format)
                displayDF['Total Cost'] = displayDF['Total Cost'].map('${:,.2f}'.format)
                
                all_cols = displayDF.columns.tolist()
                cols_to_show = st.multiselect("Columns to display:", all_cols, default=all_cols)
                st.dataframe(displayDF[cols_to_show], use_container_width=True)

                # downloading the result as csv file
                @st.cache_data
                def to_csv(df): return df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV", to_csv(displayDF), "solution.csv", "text/csv", use_container_width=True)

        # tab 2 with the iterations of the simplex algo
        with tab2:
            st.subheader("Simplex Algorithm Steps")
            tableauList = result.get('tableauList', [])
            basicSols = result.get('basicSolutions', [])
            
            if not tableauList:
                st.warning("No iterations recorded.")
            else:
                st.info(f"Solved in {len(tableauList)-1} iterations.")
                
                # add a toggle to switch views
                view_mode = st.radio("Display Mode:", ["Show All Iterations", "Slider View"], horizontal=True)
                st.markdown("---")

                # slider view
                if view_mode == "Slider View":
                    index = st.slider("Select Iteration:", 0, len(tableauList)-1, 0)
                    if index == 0:
                        st.markdown(f"### Initial Tableau")
                    else: 
                        st.markdown(f"### Iteration {index}")
                    
                    # show basic solution
                    if index < len(basicSols):
                        st.write("**Current Basic Solution:**")
                        st.dataframe(pd.DataFrame([basicSols[index]]), hide_index=True)
                    
                    st.write("**Full Tableau:**")
                    st.dataframe(pd.DataFrame(tableauList[index]))

                # show all view
                else:
                    for i, tableau in enumerate(tableauList):
                        if i == 0:
                            st.markdown(f"### Initial Tableau")
                        else:
                            st.markdown(f"### Iteration {i}")
                        
                        if i < len(basicSols):
                            st.caption("**Current Basic Solution:**")
                            st.dataframe(pd.DataFrame([basicSols[i]]), hide_index=True)
                        
                        st.caption("**Full Tableau:**")
                        st.dataframe(pd.DataFrame(tableau))
                        st.markdown("---")

        # about section
        with tab4:
            # header Section
            st.title("About the Project")
            
            # organizing project details and overview to columns     
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Project Overview")
                st.markdown("""
                The **City Pollution Reduction Solver** is a system developed to address the challenge of environmental budgeting and pollution for Greenvale City. 
                
                By utilizing **Linear Programming** (Simplex Algorithm), the application helps users select the most cost-effective combination of mitigation projects to satisfy strict reduction constraints for 10 different pollutants.
                """)
                
                st.subheader("Algorithm Implementation")
                st.markdown("""
                At the core of this project is a custom-built **Simplex Algorithm** written in Python:
                * Simplex Algorithm (Minimization): The solver handles minimization problems by reconstructing the problem to a maximization problem by converting it to a dual problem and use the simplex method. 
                * **Matrix Operations:** All the tableau operations (pivoting, normalization, row elimination) are performed using numpy for efficiency.
                * **Generating Tableau:** It automatically constructs the matrix based on the user's specific selection of projects.""")
                
                # constraints section
                st.subheader("Problem Statement")
                st.markdown("""
                This project models the problem as a **Minimization Linear Programming (LP)** problem:
                
                #### Mathematical Formulation
                * **Objective Function:**
                    $$ \\text{Minimize } Z = \\sum_{j=1}^{30} (\\text{Cost}_j \\times x_j) $$
                
                * **Constraint A: Pollutant Reduction ($\ge$)**
                    $$ \\sum (\\text{Reduction}_{ij} \\times x_j) \\ge \\text{Target}_i \\quad \\text{(for CO}_2, \\text{NO}_x, \\dots) $$
                
                * **Constraint B: Project Limits ($\le$)**
                    $$ x_j \\le 20 \\quad \\text{for all } j $$
                
                The solver runs the standard Simplex algorithm on this problem.
                """)
            
            with col2:
                st.subheader("Project Details")
                st.success("""
                **Course:** CMSC 150: Numerical & Symbolic Computation

                **Term:** 1st Sem, A.Y. 2025-2026

                **Author:** Arvin C. Ferrer

                **Section:** AB2L
                """)
                
                # for logo
                # st.image("logo.png", use_container_width=True)

            st.markdown("---")
            
            # sub-section for tech stack used
            st.subheader("Tech Stack")
            st.write("This application uses a powerful stack of open-source Python libraries:")
            
            t1, t2, t3, t4 = st.columns(4)
            
            with t1:
                st.markdown("### Python")
                st.caption("Core Logic")
                st.write("The primary programming language used for the backend logic, simplex implementation, and data management.")
            
            with t2:
                st.markdown("### NumPy")
                st.caption("Simplex algorithm")
                st.write("Used for array manipulation. It handles the Simplex tableau as a matrix, performing Gaussian elimination.")
            
            with t3:
                st.markdown("### Pandas")
                st.caption("Data Management")
                st.write("Manages the CSV inputs (`projects_matrix.csv`, `pollutant_targets.csv`) and organizes the final solution for display and export.")
                
            with t4:
                st.markdown("### Altair")
                st.caption("Visualization")
                st.write("A statistical visualization library used to generate the interactive Bar Charts and Pie Charts in the results tab.")

            st.markdown("---")
     
        # view the input data
        with tab3:
            st.subheader("Raw Data")
            with st.expander("Projects Matrix", expanded=True): st.dataframe(projectsDF)
            with st.expander("Pollutant Targets", expanded=True): st.dataframe(targetsDF)

    # default welcome page
    # elif not solve_button:
    else:
        # st.image("logo.png", width=150) # for the logo
         # default message on the main page before solving
        st.info("Select projects from the sidebar and click 'Solve' to see the results.")
        st.subheader("Problem Overview")

        # get the number of projects the user has currently selected
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

