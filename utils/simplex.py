
def solve_simplex(initial_tableau):
    tableau_history = [] 
    
    current_tableau = initial_tableau
    tableau_history.append(current_tableau)
    
    while not is_optimal(current_tableau):
        current_tableau = pivot(current_tableau)
        tableau_history.append(current_tableau)
        
    final_solution = parse_solution(current_tableau)
    #test
    return final_solution, tableau_history