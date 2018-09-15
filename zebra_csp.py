import operator
from datetime import datetime
from typing import Dict, List
import inspect

from csp_constraint_propagation import Constraint, Csp, solve


def zebra_csp() -> (List, List, List):
    nations = ["English", "Spanish", "Ukrainian", "Norwegian", "Japanese"]
    drinks = ["Coffee", "Tea", "Milk", "OrangeJuice", "Water"]
    pets = ["Dog", "Snails", "Horse", "Fox", "Zebra"]
    brands = ["LuckyStrike", "Parliaments",
              "Kools", "Chesterfields", "OldGold"]
    colours = ["Red", "Green", "Ivory", "Yellow", "Blue"]
    variables = nations + drinks + pets + brands + colours
    values = list(range(1, 6))
    constraints = []
    constraints_equal = [["English", "Red"],
                         ["Spanish", "Dog"],
                         ["Coffee", "Green"],
                         ["Ukrainian", "Tea"],
                         ["OldGold", "Snails"],
                         ["Kools", "Yellow"],
                         ["LuckyStrike", "OrangeJuice"],
                         ["Japanese", "Parliaments"],
                         ["Norwegian", "Blue"],
                         ]
    constraints_next_to = [["Chesterfields", "Fox"], ["Horse", "Kools"]]
    for c in constraints_equal:
        constraints += [Constraint(lambda x, c0_bind=c[0], c1_bind=c[1]: x[c0_bind]
                                   == x[c1_bind], c)]

    for c in constraints_next_to:
        constraints += [Constraint(lambda x, c0_bind=c[0], c1_bind=c[0]: next_to(
            c0_bind, c1_bind, x), c)]

    constraints += [Constraint(lambda x: x["Norwegian"] == 1, ["Norwegian"])]
    constraints += [Constraint(lambda x: x["Milk"] == 3, ["Milk"])]
    constraints += [Constraint(lambda x: x["Green"]
                               == x["Ivory"] + 1, [["Green"], ["Ivory"]])]
    constraints += all_different(colours)
    constraints += all_different(drinks)
    constraints += all_different(nations)
    constraints += all_different(pets)
    constraints += all_different(brands)

    return Csp(variables, values, constraints)


def next_to(x, y, assignment)-> bool:
    return abs(assignment[x]-assignment[y]) == 1


def all_different(keys)-> List[Constraint]:
    ret = []
    for k in keys:
        for j in keys:
            if j != k:
                ret += [Constraint(lambda x,
                                   k_bind=k, j_bind=j:  x[j_bind] != x[k_bind], [j, k])]
    return ret


def main():
    start_total = datetime.now()
    csp = zebra_csp()
    solution = solve(csp)
    print(
        f"The total computation took {(datetime.now()-start_total).microseconds} microsecs")
    try:
        print("zebra:", solution["Zebra"])
        print("water:", solution["Water"])
        print(sorted(solution.items(), key=lambda kv: kv[1]))
    except:
        print("No solution")
