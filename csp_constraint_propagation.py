import copy
import inspect
import random
from typing import Callable, Dict, List


class Constraint(object):

    def __init__(self, formula, variables):
        self.formula: Callable = formula
        self.variables: Dict = variables


class BackTrackError(Exception):
    pass


class Csp():
    def __init__(self, variables, values, constraints):
        self.variables = variables
        self.values = values
        # implemented as lambdas
        self.constraints: List[Constraint] = constraints


def solve(csp: Csp) -> Dict:
    #  This is a very basic constraints solver that is based on backtracking.
    values_per_var = {v: csp.values for v in csp.variables}
    # constraint is a key value pair: lambda, list of variables
    unary_constr = {c.formula: c.variables for c in csp.constraints if len(
        c.variables) == 1}
    other_constr = {c.formula: c.variables for c in csp.constraints if len(
        c.variables) >= 2}
    try:
        for f in unary_constr:
            var = random.choice(unary_constr[f])
            values_per_var[var] = solve_unary(
                f, var, values_per_var[var])
            return bt_search({}, values_per_var, other_constr)
    except BackTrackError:
        pass


def solve_unary(f, var, values):
    # Given a constraint f containing only a single variable,
    # find all possible values for this variable that do not violate f.
    legal = [value for value in values if eval_constraint({var: value}, f)]
    # check if legal consists of other than None
    if legal == []:
        raise BackTrackError  # game over
    return legal


def bt_search(assignment: dict, values: dict, constraints: dict) -> dict:
    assignment = copy.deepcopy(assignment)
    values = copy.deepcopy(values)
    constraints = copy.deepcopy(constraints)

    if len(assignment) == len(values):
        return assignment
    x = most_constrained_var(assignment, values)
    # TODO search for error below this point
    for v in values[x]:
        try:
            if is_consistent(x, v, assignment, constraints):
                new_vals = propagate(x, v, assignment, constraints, values)
                assignment[x] = v
                return bt_search(assignment, new_vals, constraints)
        # equivalent of setlx "check{...}"
        except BackTrackError:
            pass
    raise BackTrackError


def most_constrained_var(assignment, values):
    #  Given the current Assignment, select a variable that has not yet been
    #  assigned a value.  Choose the variable that has the least number of
    #  possible values.
    unassigned = {x: U for x, U in values.items(
    ) if x not in assignment.keys()}
    min_size = min(len(U) for x, U in unassigned.items())
    choice = random.choice(
        [x for x, U in unassigned.items() if len(U) == min_size])
    return choice


def propagate(x, v, assignment, constraints, values):
    # Given a variable x and a value v, extend the Assignment so that x is bound to v
    # and compute the Values that can still be assigned to the unassigned variables.
    assignment = copy.deepcopy(assignment)
    values = copy.deepcopy(values)
    constraints = copy.deepcopy(constraints)
    values[x] = [v]

    # propagation only for binary constraints
    for f, vars in constraints.items():
        if x in vars and len(vars) == 2:
            # extract one variable to compare to x
            del vars[vars.index(x)]
            y = vars[0]
            if y not in assignment.keys():
                legal = []
                for w in values[y]:
                    if eval_constraint({x: v, y: w}, f):
                        legal.append(w)
                if legal == []:
                    raise BackTrackError
                values[y] = legal
    return values


def is_consistent(var, value, assignment: dict, constraints: Dict[Callable, List[str]]) -> bool:
    # Check, whether the extended assignment
    # Assignment + { [var, value] };
    # is consistent with the given constraints.
    new_assignment = copy.deepcopy(assignment)
    new_assignment[var] = value
    for formula, vars in constraints.items():
        cond1 = (var in vars and is_subset_of(vars, new_assignment.keys()))
        if not(not cond1 or eval_constraint(new_assignment, formula)):
            return False
    return True


def is_subset_of(subset, sset):
    # Check if subset is a subset of sset
    for s in subset:
        if s not in sset:
            return False
    return True


def eval_constraint(assignment, formula):
    # Evaluate a formula under a given Assignment.
    # Assignment: Binary relation assigning values to variables
    # Formula:    The formula to evaluate
    return formula(assignment)
