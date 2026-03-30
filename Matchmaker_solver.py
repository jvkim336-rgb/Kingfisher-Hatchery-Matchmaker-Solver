import pandas as pd
import copy
import itertools
import re

def matchmaker(matrix, females, male_use, quarter):
    domains = {}

    #enforce unary conditions:
    for female in females:
        female_table = matrix[[female]]
        #Remove inbreeding
        female_table = female_table.merge(male_use, how= "inner",left_on=female, right_on="Male")
        #remove males spawned more than 4 times
        candidates = female_table[female_table["Uses"] < min(quarter+1, 4)][female]
        double_allowed = set(female_table[female_table["Uses"] <= 2][female])

        #add top candidates and find all valid combinations. 
        candidates = candidates[0:9]
        #filter domains for double jacks
        domains[female] = domain_jack_filter(list(itertools.combinations(candidates, 6)))

    initial_assignment = {female : [] for female in domains.keys()} 

    solutions = backtrack(initial_assignment, domains, double_allowed)
    solutions = assignment_jack_filter(solutions)
    solutions.sort(key = lambda sol:cost(sol, matrix))
    return solutions

def backtrack(assignment, domains, double_allowed):
    unfilled_f = None
    for female in assignment.keys():
        if not assignment[female]:
            unfilled_f = female
            break
    if not unfilled_f:
        return [copy.deepcopy(assignment)]


    solutions = []
    for value in domains[unfilled_f]:
        new_assignment = copy.deepcopy(assignment)
        new_assignment[unfilled_f] = value

        if constraint_check(new_assignment, double_allowed):
            solutions += backtrack(new_assignment, domains, double_allowed)
    return solutions
    
def constraint_check(assignment, double_allowed):
    checked = set()
    double = set()
    for female in assignment.keys():
        if assignment[female]:
            for i in range(6):
                male = assignment[female][i]
                if male in checked:
                    if male in double_allowed:
                        double.add(male)
                    else:
                        return False
                else:
                    checked.add(male)
    return True

def domain_jack_filter(combinations):
    jack_mask = [len(re.findall(r"p", str(comb))) < 2 for comb in combinations]
    return list(itertools.compress(combinations, jack_mask))

def assignment_jack_filter(assignments):
    jack_mask = [len(re.findall(r"p", str(sol)))/(5*len(sol)) < 0.05 for sol in assignments]
    return list(itertools.compress(assignments, jack_mask))

def cost(solution, matrix):
    solution_table = pd.DataFrame(solution)
    sol_cost = 0
    for female in solution.keys():
        female_table = matrix[[female, "rank"]]
        sol_cost += int(solution_table.copy().merge(female_table)["rank"].sum())
    return sol_cost