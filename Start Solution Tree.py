import pandas as pd
from Planner import Planner


 # setting variables
database = "Dataset 11.xlsx"
cottage_sheet = "Cottages"
reservations_sheet = "Reservations"
validator_sheet = "Validator"
read_sheet = "Validator"

restrictionlist = ["Class", "Face South", "Near Playground", \
                   "Close to the Centre", "Near Lake ", \
                   "Near car park", "Accessible for Wheelchair", \
                   "Child Friendly", "Dish Washer ", \
                   "Wi-Fi Coverage ", "Covered Terrace"]
    
 # code to import from excel file
cottages = pd.read_excel(database, sheet_name = cottage_sheet)
reservations = pd.read_excel(database, sheet_name = reservations_sheet)

assignments = pd.read_excel(database, sheet_name = read_sheet, index_col = 0, usecols = [0, 1]).squeeze()

 # code to run planner
planner = Planner(cottages, reservations)
planner.assign_cottages()
# planner.assign_improvements_any(300)
# planner.assign_improvements_simulated(300)
# planner.store_excel(database, validator_sheet)
# planner.read_assignements(assignments)
print(planner.score, planner.upgrade_count)

combinations = planner.combinations