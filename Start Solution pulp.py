 # import modules
import pulp
import pandas as pd
from time import time

 # setting variables
start_time = time()
database = "Dataset 11.xlsx"
cottage_sheet = "Cottages"
reservations_sheet = "Reservations"
restrictionlist = ["Class", "Face South", "Near Playground", \
                   "Close to the Centre", "Near Lake ", \
                   "Near car park", "Accessible for Wheelchair", \
                   "Child Friendly", "Dish Washer ", \
                   "Wi-Fi Coverage ", "Covered Terrace"]

 # code to print time
def print_time(start_time, msg = ""):
    print(msg + "   --- %s seconds ---" % (time() - start_time))
    
 # code to import from excel file
cottages = pd.read_excel(database, sheet_name = cottage_sheet)
reservations = pd.read_excel(database, sheet_name = reservations_sheet)

 # modify dataset
earliest_day = reservations["Arrival Date"].min()
reservations["day"] = reservations["Arrival Date"].apply(lambda x: (x-earliest_day).days)
# print(reservations.columns)

 # create dataframe of allowed cottages and reservations
def reservation_options(cottages, reservations):
    combined = pd.merge(reservations, cottages, how = "cross", suffixes = ("_res", "_cot"))
    combined = combined[combined["Max # Pers"] >= combined["# Persons"]]
    for restriction in restrictionlist:
        combined = combined[combined["{}_res".format(restriction)] <= combined["{}_cot".format(restriction)]]
    combined = combined[(combined["Cottage (Fixed)"] == 0).add(combined["Cottage (Fixed)"] == combined["ID_cot"])]
    combined = combined.reset_index()
    combined["ID"] = combined.index
    return combined


 # create dataframe with possible day cottage and reservation
def conflict_cottages(combined):
    conflicts = combined.copy()
    for days in range(2, combined["Length of Stay"].max() + 1):
        combined = combined[combined["Length of Stay"] >= days]
        combined.loc[:, "day"] += 1
        conflicts = pd.concat([conflicts, combined], ignore_index = True)
    return conflicts

print_time(start_time, "start code")
combined = reservation_options(cottages, reservations)
print_time(start_time, "combined done")
conflicted = conflict_cottages(combined)
print_time(start_time, "conflicted done")
 # create pulp variables
pulp_variables = dict()
for i in range(len(combined["ID"]) + 1): pulp_variables[i] = pulp.LpVariable(f"{i}", cat = "Binary")
print_time(start_time, "dict done")
 # create pulp problem and constraints
Lp_prob = pulp.LpProblem("Start_Solution", pulp.LpMinimize)

for reservation in combined.groupby("ID_res")["ID"].apply(list).tolist():
    Lp_prob += pulp.lpSum([pulp_variables[ID] for ID in reservation]) == 1

for conflict in conflicted.groupby(["day", "ID_cot"])["ID"].apply(list).tolist():
    Lp_prob += pulp.lpSum([pulp_variables[ID] for ID in conflict]) <= 1

print_time(start_time, "constraints done")
Lp_prob.solve(pulp.CPLEX_CMD())
##Lp_prob.solve()
print_time(start_time, "Lp calculation done")
