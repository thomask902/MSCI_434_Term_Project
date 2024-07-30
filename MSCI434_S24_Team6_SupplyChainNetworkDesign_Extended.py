import gurobipy as gp
from gurobipy import GRB

# Defining the sets for products and months
products = {'A', 'B', 'C', 'D', 'E', 'F'}
months = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}

# NEW
# Defining the profit price and cost for each product
purchase_price = {'A': 395, 'B': 1060, 'C': 650, 'D': 375, 'E': 1030, 'F': 630}
selling_price = {'A': 475, 'B': 1260, 'C': 860, 'D': 440, 'E': 1180, 'F': 780}

# Defining the costs
trucking_cost = 4000
delivery_cost_per_trip = 675
annual_labor_cost = 499200

# NEW
# Defining the monthly holding cost rate or interest rate, and creating a dictionary of cost for each product
holding_rate = 0.20 / 12
product_holding = {key: value * holding_rate for key, value in purchase_price.items()}

# Defining the crate capacity for each product
crate_capacity = {'A': 250, 'B': 70, 'C': 125, 'D': 250, 'E': 70, 'F': 125}

# Defining the crate capacity of storage, restock trucks, and delivery trucks
storage_capacity = 20  
restock_truck_capacity = 8  
delivery_truck_capacity = 1 

# Defining the max number of restock trucks per period
restock_truck_max = 3 

# Defining the forecasted monthly demands
forecasted_demand = {
    'A': [770, 572, 811, 694, 636, 676, 682, 604, 441, 659, 416, 382],
    'B': [671, 597, 557, 648, 711, 558, 659, 480, 537, 543, 580, 550],
    'C': [182, 171, 136, 159, 273, 208, 118, 160, 173, 143, 95, 87],
    'D': [555, 706, 702, 470, 704, 541, 604, 504, 496, 591, 416, 443],
    'E': [129, 52, 124, 144, 118, 113, 144, 131, 131, 103, 143, 86],
    'F': [55, 72, 58, 63, 55, 72, 72, 49, 77, 56, 91, 54]
}

# Initializing the Gurobi model to begin adding decision variables and constraints
model = gp.Model("Plywood_Inventory_Management")

# Defining the decision variables, they have an automatic lower bound of zero

# Defining reorder quantity for each product at each month
Q = model.addVars(products, months, vtype=GRB.INTEGER, name="Q")

# Defining inventory level for each product at each month
I = model.addVars(products, months, vtype=GRB.INTEGER, name="I")

# Defining the number of restock trucks needed each month, with an upper-bound of 3 per month
t = model.addVars(months, vtype=GRB.INTEGER, ub=restock_truck_max, name="t")

# Defining the number of delivery trucks needed each month
s = model.addVars(months, vtype=GRB.INTEGER, name="s")

# Setting the objective function to be the profit of products sold less the restock trucking cost, delivery trucking cost and annual labor cost
model.setObjective(
    gp.quicksum(selling_price[prod] * forecasted_demand[prod][month] - purchase_price[prod] * Q[prod, month] - product_holding[prod] * I[prod, month] for prod in products for month in months)
    # gp.quicksum(selling_price[prod] * forecasted_demand[prod][month] - purchase_price[prod] * Q[prod, month] for prod in products for month in months)
    - trucking_cost * gp.quicksum(t[month] for month in months)
    - delivery_cost_per_trip * gp.quicksum(s[month] for month in months)
    - annual_labor_cost,
    GRB.MAXIMIZE
)

# Defining the model's constraints

# Setting the demand constraint for each product in each month
for prod in products:
    for month in months:

        # If it is the first month, there is no entering inventory, so the ending inventory is only the ordered amount minus the demand
        if month == 0:
            model.addConstr(Q[prod, month] - I[prod, month] == forecasted_demand[prod][month], f"demand_{prod}_{month}")

        # REMOVED FINAL MONTH INVENTORY CONSTRAINT
        # If it is the last month, there is no ending inventory, so the order quantity is just enough to meet the demand given the entering inventory
        #elif month == 11:
        #    model.addConstr(I[prod, month-1] + Q[prod, month] == forecasted_demand[prod][month], f"demand_{prod}_{month}")

        # For all other months, the ending inventory is the entering inventory plus order quantity minus demand
        else:
            model.addConstr(I[prod, month-1] + Q[prod, month] - I[prod, month] == forecasted_demand[prod][month], f"demand_{prod}_{month}")


# Setting the storage capacity constraint for each month
for month in months:
    model.addConstr(

        # For the first month, there is no entering inventory, so the storage amount is only the ordering amount
        # For all subsequent months, the holding amount is the entering inventory plus the quantity ordered
        # The holding amount is scaled by the crate capacity for that product, and these capacities are summed and forced to be <= 20
        gp.quicksum(
            ((I[prod, month-1] if month > 0 else 0) + Q[prod, month]) / crate_capacity[prod] 
            for prod in products
        ) <= storage_capacity, 
        f"storage_{month}"
    )

# Setting restock truck capacity constraint
for month in months:

    # The sum of quantities ordered across all products, scaled by their crate capacity, must be less than the capacity of the number of restock trucks ordered
    # (the number of trucks ordered also has an upper bound of 3 as defined above)
    model.addConstr(gp.quicksum(Q[prod, month] / crate_capacity[prod] for prod in products) <= restock_truck_capacity * t[month], f"restock_truck_{month}")

# Setting delivery truck capacity constraint
for month in months:

    # The sum of quantities delivered across all products, scaled by their crate capacity, must be less than the capacity of the number of delivery trucks ordered
    model.addConstr(gp.quicksum(forecasted_demand[prod][month] / crate_capacity[prod] for prod in products) <= delivery_truck_capacity * s[month], f"delivery_truck_{month}")

# Initiate Gurobi's model solver
model.optimize()

# Output the results of the solution for each decision variable
if model.status == GRB.OPTIMAL:
    print(f"Optimal Objective Value: {model.objVal}")
    for v in model.getVars():
        if v.X != 0:
            print(f"{v.VarName}: {v.X}")
else:
    print("No optimal solution found.")