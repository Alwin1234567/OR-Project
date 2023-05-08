 # import modules
import pandas as pd
from time import time
from Cottage import Cottage
import openpyxl

 # Planner class
class Planner():
    """
    Class that stores and maintaines all info regarding reservations and cottages
    """
    
    def __init__(self, cottages, reservations, restrictionlist = ["Class", "Face South", "Near Playground", \
                       "Close to the Centre", "Near Lake ", \
                       "Near car park", "Accessible for Wheelchair", \
                       "Child Friendly", "Dish Washer ", \
                       "Wi-Fi Coverage ", "Covered Terrace"]):
        self.start_time = time()
        self.print_time("starting Planner init")
         # Add day (0 is earliest reservation day) and departure day
        earliest_day = reservations["Arrival Date"].min()
        reservations["day"] = reservations["Arrival Date"].apply(lambda x: (x-earliest_day).days)
        reservations["final_day"] = reservations["day"].add(reservations["Length of Stay"]).add(-1)
         # Changes "# persons" for reservations to nearest higher or equal "max # pers"
        cottage_Max_pers = cottages["Max # Pers"].unique().tolist()
        cottage_Max_pers.append(0)
        cottage_Max_pers.sort()
        for i in range(len(cottage_Max_pers) - 1): reservations.loc[(cottage_Max_pers[i] < reservations["# Persons"]).multiply(reservations["# Persons"] < cottage_Max_pers[i + 1]), "# Persons"] = cottage_Max_pers[i + 1]
        
        self.df_cottages = cottages
        self.df_reservations = reservations
        self.restrictionlist = restrictionlist
        self.combinations = self.combine()
        daycount = reservations["final_day"].max() + 1
        self.cottages = dict()
        for ID in cottages["ID"].tolist(): self.cottages[ID] = Cottage(ID, daycount, earliest_day)
        self.print_time("finished Planner init")
    
    
    def print_time(self, msg = ""): print(msg + "   --- %s seconds ---" % (time() - self.start_time))
    
    
    def combine(self):
        """
        Function to retrieve a dataframe with all possible reservation-cottage combos.        

        Returns
        -------
        combined : pd.Dataframe
            Cross product of cottages and reservations where only allowed combos are left.

        """
        combined = pd.merge(self.df_reservations, self.df_cottages, how = "cross", suffixes = ("_res", "_cot"))
        combined = combined[combined["Max # Pers"] >= combined["# Persons"]]
        for restriction in self.restrictionlist:
            combined = combined[combined["{}_res".format(restriction)] <= combined["{}_cot".format(restriction)]]
        combined = combined[(combined["Cottage (Fixed)"] == 0).add(combined["Cottage (Fixed)"] == combined["ID_cot"])]
        combined["upgrade"] = combined["Class_cot"] - combined["Class_res"] + \
                              combined["Max # Pers"] - combined["# Persons"] > 0
        combined["fitness"] = combined["Max # Pers"] - combined["# Persons"]
        for restriction in self.restrictionlist:
            combined["fitness"] = combined["fitness"].add(combined["{}_cot".format(restriction)] - combined["{}_res".format(restriction)])
        combined = combined.reset_index()
        combined["ID"] = combined.index
        return combined
    
    def assign_cottages(self):
        """
        Function that assigns reservations to the cottages. There is no failsafe yes.
        It assigns the reservation with the least possible cottages first and chooses 
        the cottage based on whether it is considered an upgrade and the fitness score.
        """
        self.print_time("started assigning cottages")
        order = self.combinations.groupby("ID_res")["index"].count().sort_values().index.tolist()
        for reservation_ID in order:
            cottages = self.combinations[self.combinations["ID_res"] == reservation_ID]
            cottages = cottages.sort_values(by = ["upgrade", "fitness"])[["ID_cot", "ID_res", "day", "Length of Stay", "upgrade"]]
            assigned = False
            for index, row in cottages.iterrows():
                cottage = self.cottages[row["ID_cot"]]
                if cottage.allowed_reservation((row["ID_res"], row["upgrade"]), row["day"], row["Length of Stay"]):
                    cottage.add_reservation((row["ID_res"], row["upgrade"]), row["day"], row["Length of Stay"])
                    assigned = True
                    break
            if not assigned: print("couldn't assign reservation {}".format(reservation_ID))
        self.print_time("ended assigning cottages")

    def display_cottages(self):
        """
        Function that prints all cottage planning.
        """
        self.print_time("started displaying cottages")
        for cottage in self.cottages.values(): cottage.display_days()
        self.print_time("ended displaying cottages")
    
    def reservation_assignments(self):
        """
        Function that returns a dataframe with the reservations as index and the cottage number they are assigned to.
        """
        assignments = dict()
        for cottage in self.cottages.values():
            ID = cottage.ID
            for reservation in cottage.reservations: assignments[reservation[0]] = ID
        return pd.Series(data = assignments).sort_index()
    
    def store_excel(self, filename, sheetname):
        """
        Function that stores the assigned cottage of a reservation in Excel.
        """
        repeat = True
        while repeat:
            try: 
                workbook = openpyxl.load_workbook(filename = filename)
                workbook.save(filename)
                workbook.close()
                repeat = False
            except:
                answer = input("Python can't open {}.\nIf the file is opened please close it\nDo you want to try again? (y/n)".format(filename))
                if answer != "y": return
        self.print_time("started writing in excel")
        workbook = openpyxl.load_workbook(filename = filename)
        worksheet = workbook[sheetname]
        for i, cottage in enumerate(self.reservation_assignments().values.tolist(), start = 2):
            worksheet.cell(row = i, column = 2).value = cottage
        workbook.save(filename)
        workbook.close()
        self.print_time("ended writing in excel")
    
    @property
    def score(self):
        total = 0
        for cottage in self.cottages.values(): total += cottage.score
        return total