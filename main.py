import streamlit as st
import pandas as pd
import numpy as np
from utils.simplex import SimplexSolver, createBigMTableau

st.set_page_config(layout="wide", page_title="Pollution Reduction Solver")

@st.cache_data
def load_data():
    #Loads CSV data.
    try:
        projects_df = pd.read_csv('data/projects_matrix.csv')
        targets_df = pd.read_csv('data/pollutant_targets.csv')
        
        # Get the 10 pollutant names from the targets file
        pollutant_cols = targets_df['Pollutant'].tolist()
        
        return projects_df, targets_df, pollutant_cols
    except FileNotFoundError as e:
        # Show error on main page if files not found
        st.error(f"Error loading data: {e}. Make sure 'data' folder and CSV files exist.")
        return None, None, None
# Clearing selections
def clear_selections():
    st.session_state.project_selector = []

# loading the dataframe
projects_df, targets_df, pollutant_cols = load_data()

# Streamlit Sidebar controls
with st.sidebar:
    st.title("Solver Controls")
    st.markdown("Select mitigation projects and run the solver.")
    
    if projects_df is not None:
        st.header("1. Select Projects")
        
        project_names_list = projects_df['Project Name'].tolist()
        
        selected_project_names = st.multiselect(
            "Choose projects to include:",
            options=project_names_list,
            default=project_names_list, # "Check all" by default
            key='project_selector'
        )

        st.button(
            'Reset Selection', 
            on_click=clear_selections,
            help="Deselects all projects.",
            use_container_width=True
        )
        
        st.markdown("---")

        # Start button to start solving
        solve_button = st.button(
            "Start Solving",
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
           project_data = projects_df[projects_df['Project Name'] == project_to_inspect]
           st.dataframe(project_data, use_container_width=True)
        else:
           st.error("Data files not found.")


# Main Display page
st.title("City Pollution Reduction Solver")

# Only proceed if data was loaded and not null
if projects_df is not None:
    
    # Solver Execution (solve button)
    if solve_button:
        st.header("2. Solver Results")
        if not selected_project_names:
            st.warning("Please select at least one project from the sidebar.")
        else:
            with st.spinner("Running Simplex Algorithm..."):
                try:
                    # FIltering the Project Name from the selected project names to see if it exists in the csv
                    filtered_df = projects_df[projects_df['Project Name'].isin(selected_project_names)].copy()
                    filtered_df['Project Name'] = pd.Categorical(filtered_df['Project Name'], categories=selected_project_names, ordered=True)
                    filtered_df = filtered_df.sort_values('Project Name')
                    costVectorC = filtered_df['Costs'].values
                    pollutantMatrixApoll_raw = filtered_df[pollutant_cols].values 
                    targetVectorBpoll = targets_df.set_index('Pollutant').loc[pollutant_cols, 'Target'].values
                    num_decision_vars = len(costVectorC)
                    tableau = createBigMTableau(costVectorC, pollutantMatrixApoll_raw.T, targetVectorBpoll)
                    solver = SimplexSolver()
                    result = solver.solve(tableau, numVars=num_decision_vars, costVectorC=costVectorC)

                    # Displaying the result
                    tableau_Z = result['finalTableau'][-1, -1]
                    
                    if result['status'] == 'Infeasible/Unbounded' or tableau_Z < -1e8:
                        st.error("The problem is not feasible.", icon="❌")
                        st.write("The selected combination of projects cannot meet the required pollutant reduction targets.")
                    
                    elif result['status'] == 'Optimal':
                        st.success("Optimal Solution Found!", icon="✅")
                        st.metric("Minimum Total Cost (Z)", f"${result['Z']:,.2f}")
                        
                        solution_df = pd.DataFrame({
                            'Mitigation Project': filtered_df['Project Name'].tolist(),
                            'Project Units (x_i)': result['basicSolution'],
                            'Total Cost': result['basicSolution'] * costVectorC
                        })
                        
                        solution_df = solution_df[solution_df['Project Units (x_i)'] > 1e-6]
                        solution_df['Project Units (x_i)'] = solution_df['Project Units (x_i)'].map('{:,.4f}'.format)
                        solution_df['Total Cost'] = solution_df['Total Cost'].map('${:,.2f}'.format)
                        
                        st.subheader("Final Project Implementation")
                        st.dataframe(solution_df, use_container_width=True)


                        # Convert the dataframe to CSV format Downloading it
                        @st.cache_data
                        def convert_df_to_csv(df):
                            return df.to_csv(index=False).encode('utf-8')

                        csv_data = convert_df_to_csv(solution_df)
                        # Download button
                        st.download_button(
                            label="Download Solution as CSV",
                            data=csv_data,
                            file_name="project_solution.csv",
                            mime="text/csv",
                            use_container_width=True
                        )                         
                        # Display Iterations 
                        st.markdown("---")
                        st.subheader("Simplex Iterations (Step-by-Step)")
                        with st.expander("Show/Hide All Iteration Tableaus"):
                            tableau_list = result.get('tableauList', [])
                            obj_row_list = result.get('objectiveRowList', [])
                            
                            if not tableau_list:
                                st.warning("Iteration list not found in solver result.")
                            else:
                                st.info(f"The solver found the solution in {len(tableau_list) - 1} iterations.")
                                for i, tableau_step in enumerate(tableau_list):
                                    st.markdown(f"**Iteration {i}**")
                                    if i < len(obj_row_list):
                                        st.write("Objective Row:")
                                        st.dataframe(pd.DataFrame(obj_row_list[i]).T)
                                    st.dataframe(pd.DataFrame(tableau_step))
                                    st.markdown("---")

                except Exception as e:
                    st.error(f"An error occurred during solving: {e}")
                    import traceback
                    st.exception(e)
    else:
        # This is the default message on the main page before solving
        st.info("Select projects from the sidebar and click 'Start Solving' to see the results.")

    # Show Input Data 
    st.markdown("---")
    with st.expander("Show Input Data Files"):
        
        st.subheader("Projects Matrix (`projects_matrix.csv`)")
        st.dataframe(projects_df, use_container_width=True)
        
        st.subheader("Pollutant Targets (`pollutant_targets.csv`)")
        st.dataframe(targets_df, use_container_width=True)