print("Hello Team 6")

import gurobipy as gp
from gurobipy import GRB

# Data from the study
# Constants
profit_margins = {'A': 80, 'B': 200, 'C': 210, 'D': 65, 'E': 150, 'F': 150}
trucking_cost = 4000
delivery_cost_per_trip = 675
annual_labor_cost = 499200
crate_capacity = {'A': 250, 'B': 70, 'C': 125, 'D': 250, 'E': 70, 'F': 125}
storage_capacity = 20  # crates
restock_truck_capacity = 8  # crates
delivery_truck_capacity = 1  # crate

# Forecasted monthly demands
forecasted_demand = {
    'A': [770, 572, 811, 694, 636, 676, 682, 604, 441, 659, 416, 382],
    'B': [671, 597, 557, 648, 711, 580, 659, 480, 537, 543, 580, 550],
    'C': [182, 171, 136, 159, 273, 208, 118, 160, 173, 143, 95, 87],
    'D': [555, 706, 702, 470, 704, 541, 604, 504, 496, 591, 416, 443],
    'E': [129, 52, 124, 144, 118, 113, 144, 131, 131, 103, 143, 86],
    'F': [55, 72, 58, 63, 55, 72, 72, 49, 77, 56, 91, 54]
}

# Initialize the model
model = gp.Model("Multi-Period_Inventory_Management")

# Decision Variables
Q = model.addVars(profit_margins.keys(), range(12), vtype=GRB.INTEGER, name="Q")
I = model.addVars(profit_margins.keys(), range(11), vtype=GRB.INTEGER, name="I")
t = model.addVars(range(12), vtype=GRB.INTEGER, name="t")
s = model.addVars(range(12), vtype=GRB.INTEGER, name="s")

# Objective Function
model.setObjective(
    gp.quicksum(profit_margins[prod] * Q[prod, month] for prod in profit_margins for month in range(12))
    - trucking_cost * gp.quicksum(t[month] for month in range(12))
    - delivery_cost_per_trip * gp.quicksum(s[month] for month in range(12))
    - annual_labor_cost,
    GRB.MAXIMIZE
)

# Constraints
# Demand constraints
for prod in profit_margins:
    for month in range(12):
        if month == 0:
            model.addConstr(Q[prod, month] - I[prod, month] == forecasted_demand[prod][month], f"demand_{prod}_{month}")
        elif month == 11:
            model.addConstr(I[prod, month-1] + Q[prod, month] == forecasted_demand[prod][month], f"demand_{prod}_{month}")
        else:
            model.addConstr(I[prod, month-1] + Q[prod, month] - I[prod, month] == forecasted_demand[prod][month], f"demand_{prod}_{month}")

# Storage capacity constraint
for month in range(12):
    model.addConstr(gp.quicksum((I[prod, month-1] if month > 0 else 0) + Q[prod, month] for prod in profit_margins) / crate_capacity['A'] <= storage_capacity, f"storage_{month}")

# Restock truck capacity constraint
for month in range(12):
    model.addConstr(gp.quicksum(Q[prod, month] / crate_capacity[prod] for prod in profit_margins) <= restock_truck_capacity * t[month], f"restock_truck_{month}")

# Delivery truck capacity constraint
for month in range(12):
    model.addConstr(gp.quicksum(forecasted_demand[prod][month] / crate_capacity[prod] for prod in profit_margins) <= delivery_truck_capacity * s[month], f"delivery_truck_{month}")

# Solve the model
model.optimize()

# Output the results
if model.status == GRB.OPTIMAL:
    print(f"Optimal Objective Value: {model.objVal}")
    for v in model.getVars():
        if v.X != 0:
            print(f"{v.VarName}: {v.X}")
else:
    print("No optimal solution found.")