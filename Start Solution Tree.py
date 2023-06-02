import pandas as pd
from Planner import Planner


 # setting variables
database = "Dataset 11.xlsx"
# database = "Dataset julia.xlsx"
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
# planner.read_assignements(assignments)
planner.gaps_legionella_optimiser_repeat(max_time = 600, gaps_1 = True, gaps_2 = True, gaps_3 = True, gaps_456 = True)
# planner.gaps_optimiser(max_time = 120)
# planner.legionella_optimiser(max_time = 120)
planner.upgrade_optimiser(max_time = 400)
# planner.assign_improvements_any(300)
# planner.assign_improvements_simulated(300)
# planner.store_excel(database, validator_sheet)
# planner.read_assignements(assignments)
planner.results()
