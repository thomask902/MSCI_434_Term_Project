# This script was created to confirm our assumption that the paper's implementation of the model
# does not align with the constraints provided for delivery truck capacity
crate_capacity = {'A': 250, 'B': 70, 'C': 125, 'D': 250, 'E': 70, 'F': 125}

forecasted_demand = {
    'A': [770, 572, 811, 694, 636, 676, 682, 604, 441, 659, 416, 382],
    'B': [671, 597, 557, 648, 711, 558, 659, 480, 537, 543, 580, 550],
    'C': [182, 171, 136, 159, 273, 208, 118, 160, 173, 143, 95, 87],
    'D': [555, 706, 702, 470, 704, 541, 604, 504, 496, 591, 416, 443],
    'E': [129, 52, 124, 144, 118, 113, 144, 131, 131, 103, 143, 86],
    'F': [55, 72, 58, 63, 55, 72, 72, 49, 77, 56, 91, 54]
}

# List to store total number of crates needed in each month
total_crates_per_month = []

for month in range(12):
    total_crates = 0
    for product in forecasted_demand:
        demand = forecasted_demand[product][month]
        capacity = crate_capacity[product]
        crates_needed = demand / capacity
        total_crates += crates_needed
    total_crates_per_month.append(total_crates)

print(total_crates_per_month)
