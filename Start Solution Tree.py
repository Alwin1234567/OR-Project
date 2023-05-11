import pandas as pd
from Planner import Planner


 # setting variables
database = "Dataset 11.xlsx"
cottage_sheet = "Cottages"
reservations_sheet = "Reservations"
validator_sheet = "Validator"
restrictionlist = ["Class", "Face South", "Near Playground", \
                   "Close to the Centre", "Near Lake ", \
                   "Near car park", "Accessible for Wheelchair", \
                   "Child Friendly", "Dish Washer ", \
                   "Wi-Fi Coverage ", "Covered Terrace"]
    
 # code to import from excel file
cottages = pd.read_excel(database, sheet_name = cottage_sheet)
reservations = pd.read_excel(database, sheet_name = reservations_sheet)

 # code to run planner
planner = Planner(cottages, reservations)
planner.assign_cottages()
planner.assign_improvements_any(1200)
planner.store_excel(database, validator_sheet)
print(planner.score)

combinations = planner.combinations