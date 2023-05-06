import pandas as pd
from time import time
from Planner import Planner

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

 # code to run functions
planner = Planner(cottages, reservations)
planner.assign_cottages()
planner.display_cottages()