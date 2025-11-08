import streamlit as st
from simplex import solve_simplex

selected_projects = st.multiselect("Select Mitigation Projects", all_projects, default=all_projects)
if st.button("Run Solver"):
    results, tableaus = solve_simplex(selected_projects)
    st.write(results)
    for t in tableaus:
        st.table(t)
