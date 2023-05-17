 # import modules
import pandas as pd
from time import time
from Cottage import Cottage
import openpyxl
from math import exp
from random import random
pd.options.mode.chained_assignment = None

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
        reservations["final_day"] = reservations['final_day'].clip(upper = reservations["day"].max())
        reservations["Length of Stay"] = reservations["final_day"].subtract(reservations["day"]).add(1)
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
        combined["upgrade"] = (combined["Class_cot"] - combined["Class_res"] + \
                              combined["Max # Pers"] - combined["# Persons"] > 0).multiply(combined["Cottage (Fixed)"] == 0)
        
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
    
    def read_assignements(self, assignments, remove = False):
        """
        Function that takes a series with the reservations assigned to a cottage and imports this into the class.

        Parameters
        ----------
        assignments : pd.Series
            Series with reservation_ID as index and cottage number as value.
        remove : bool, optional
            boolean that describes if the cottages should be emptied first. The default is False.
        """
        self.print_time("started reading assignments")
        if remove:
            for cottage in self.cottages.values():
                for reservation in cottage.reservations:
                    cottage.remove_reservation(reservation)
        for reservation, cottage in assignments.items():
            combination = self.combinations.loc[(self.combinations["ID_res"] == reservation).multiply(self.combinations["ID_cot"] == cottage)].squeeze()
            self.cottages[cottage].add_reservation((combination["ID_res"], combination["upgrade"]), combination["day"], combination["Length of Stay"])
        self.print_time("ended reading assignments")
    
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
    
    def assign_improvements_best(self):
        self.print_time("started improving assignments with a score of {}".format(self.score))
        count = 0
        improved = True
        while improved:
            improved = False
            assignments = self.reservation_assignments()
            cottageIDs = list()
            cottagescores = list()
            for cottage in self.cottages.values():
                cottageIDs.append(cottage.ID)
                cottagescores.append(cottage.score)
            order = pd.Series(cottagescores, index = cottageIDs).sort_values(ascending = False).index.tolist()
            best = (0, 0)
            for cottage_ID in order:
                reservations = self.combinations[self.combinations["ID_cot"] == cottage_ID]
                for index, row in reservations.iterrows():
                    skip = False
                    for reservation in self.cottages[cottage_ID].reservations: 
                        if row["ID_res"] == reservation[0]: 
                            skip = True
                            break
                    if skip: continue
                    startscore = self.cottages[assignments.loc[row["ID_res"]]].score + \
                                 self.cottages[cottage_ID].score
                    if self.cottages[cottage_ID].allowed_reservation((row["ID_res"], row["upgrade"]), row["day"], row["Length of Stay"]):
                        old_cottage_ID = assignments.loc[row["ID_res"]]
                        if not self.switch_cottage(row["ID_res"], cottage_ID): print("error while switching cottages")
                        endscore = self.cottages[old_cottage_ID].score + self.cottages[cottage_ID].score
                        if not self.switch_cottage(row["ID_res"], old_cottage_ID): print("error while switching back cottages")
                        score = startscore - endscore
                        if score > best[1]:
                            best = (row["ID_res"], score)
                            improved = True
                if improved:
                    if not self.switch_cottage(best[0], cottage_ID): print("error while switching cottages")
                    break
            count += 1
            if count % 1 == 0: self.print_time("iteratie {} with score {}".format(count, self.score))
        self.print_time("ended improving assignments with a score of {}".format(self.score)) 
    
    def assign_improvements_any(self, max_time = 300):
        self.print_time("started improving assignments with a score of {}".format(self.score))
        count = 0
        improved = True
        runtime = time()
        repeat_after = 5
        while time() - runtime < max_time:
            improved = False
            assignments = self.reservation_assignments()
            cottageIDs = list()
            cottagescores = list()
            for cottage in self.cottages.values():
                cottageIDs.append(cottage.ID)
                cottagescores.append(cottage.score)
            order = pd.Series(cottagescores, index = cottageIDs).sort_values(ascending = False).index.tolist()
            for i, cottage_ID in enumerate(order):
                reservations = self.combinations[self.combinations["ID_cot"] == cottage_ID]
                for index, row in reservations.iterrows():
                    skip = False
                    for reservation in self.cottages[cottage_ID].reservations: 
                        if row["ID_res"] == reservation[0]: 
                            skip = True
                            break
                    if skip: continue
                    startscore = self.cottages[assignments.loc[row["ID_res"]]].score + \
                                 self.cottages[cottage_ID].score
                    if self.cottages[cottage_ID].allowed_reservation((row["ID_res"], row["upgrade"]), row["day"], row["Length of Stay"]):
                        old_cottage_ID = assignments.loc[row["ID_res"]]
                        if not self.switch_cottage(row["ID_res"], cottage_ID): print("error while switching cottages")
                        endscore = self.cottages[old_cottage_ID].score + self.cottages[cottage_ID].score
                        score = startscore - endscore
                        if score <= 0:
                            if not self.switch_cottage(row["ID_res"], old_cottage_ID): print("error while switching back cottages")
                        else:
                            improved = True
                            count += 1
                            assignments.loc[row["ID_res"]] = cottage_ID
                            if count % 10 == 0: self.print_time("iteratiion {} with score {}".format(count, self.score))
                if i >= repeat_after:
                    if not improved: repeat_after += 1
                    else: break
        self.print_time("ended improving assignments with a score of {}".format(self.score)) 
    
    
    def assign_improvements_simulated(self, max_time = 300, temperature_init_mul = 0.0001, temperature_mul = 0.5, temperature_repeat = 10):
        self.print_time("started improving assignments with a score of {}".format(self.score))
        temperature = self.score * temperature_init_mul
        runtime = time()
        assignments = [self.reservation_assignments(), self.score]
        best_assignment = (assignments[0].copy, self.score)
        combinations = self.combinations[self.combinations["Cottage (Fixed)"] == 0]
        itteration = 0
        while time() - runtime < max_time:
            success = False
            row = combinations.sample(replace = False).squeeze()
            if assignments[0].loc[row["ID_res"]] == row["ID_cot"] or \
                not self.cottages[row["ID_cot"]].allowed_reservation((row["ID_res"], row["upgrade"]), row["day"], row["Length of Stay"]): pass
            else:
                old_cottage_ID = assignments[0].loc[row["ID_res"]]
                startscore = self.cottages[assignments[0].loc[row["ID_res"]]].score + \
                             self.cottages[row["ID_cot"]].score
                if not self.switch_cottage(row["ID_res"], row["ID_cot"]): print("error while switching cottages")
                endscore = self.cottages[old_cottage_ID].score + self.cottages[row["ID_cot"]].score
                score = startscore - endscore
                if score < 0:
                    success = random() < exp(score / temperature)
                else: success = True
                if success:
                    assignments[0].loc[row["ID_res"]] = row["ID_cot"]
                    assignments[1] += score
                    if assignments[1] > best_assignment[1]: best_assignment = (assignments[0].copy(), self.score)
                    itteration += 1
                    if itteration % 10 == 0: self.print_time("iteration {} with score {}".format(itteration, self.score))
                    if itteration % temperature_repeat == 0: temperature *= temperature_mul
                else:
                    if not self.switch_cottage(row["ID_res"], old_cottage_ID): print("error while switching back cottages")
        self.print_time("ended improving assignments with a score of {}".format(self.score))
        self.read_assignements(best_assignment[0], remove = True)

    
    def gaps_optimiser(self, max_time = 300):
        self.print_time("started improving gaps with a score of {}".format(self.score))
        itteration = 0
        runtime = time()
        improved = True
        while improved: # verschil tussen 1 run en meerdere is minimaal
            cottageIDs = list()
            cottagescores = list()
            improved = False
            for cottage in self.cottages.values():
                cottageIDs.append(cottage.ID)
                cottagescores.append(cottage.score)
            order = pd.Series(cottagescores, index = cottageIDs).sort_values(ascending = False).index.tolist()
            for cottage_ID in order:
                gap_start = None
                front_reservation = (0, None)
                for i, day in enumerate(self.cottages[cottage_ID].days):
                    if gap_start == None:
                        if day == None: gap_start = i
                        elif day != front_reservation[1]: front_reservation = (i, day)
                    if gap_start != None and day != None:
                        if self.find_gap_improvement_456(cottage_ID, gap_start, i - 1):
                            improved = True
                            itteration += 1
                            if itteration % 20 == 0: self.print_time("iteration {} with score {}".format(itteration, self.score))
                        # elif front_reservation != (0, None):
                        #     if self.find_gap_improvement_1(cottage_ID, gap_start, i - 1, front_reservation):
                        #         itteration += 1
                        #         if itteration % 20 == 0: self.print_time("iteration {} with score {}".format(itteration, self.score))
                        gap_start = None
                if time() - runtime > max_time:
                    self.print_time("ended improving gaps with a score of {}".format(self.score))
                    return
        self.print_time("ended improving gaps with a score of {}".format(self.score))
                    
    def find_gap_improvement_1(self, cottage_ID, gap_start, gap_end, front_reservation):
        combinations = self.combinations
        assignments = self.reservation_assignments()
        allowed_reservations = assignments[assignments.isin(combinations[combinations["ID_res"] == front_reservation[1][0]]["ID_cot"])].index
        options = combinations[(combinations["ID_cot"] == cottage_ID).multiply(combinations["day"] == front_reservation[0]).multiply(combinations["final_day"] == gap_end).multiply(combinations["ID_res"].isin(allowed_reservations))]
        if options.empty: return False
        options = self.get_empty(options, front_reservation[0] - 1, gap_end + 1, side = "right")
        if options.empty: return False
        if not self.swap_cottages(front_reservation[1][0], options.iloc[0]["ID_res"]): print("error while swapping cottages")
        return True

    def find_gap_improvement_456(self, cottage_ID, gap_start, gap_end):
        combinations = self.combinations
        options = combinations[(combinations["ID_cot"] == cottage_ID).multiply(combinations["day"] == gap_start).multiply(combinations["final_day"] == gap_end)]
        if options.empty: return False
        options = self.get_empty(options, gap_start - 1, gap_end + 1, side = "both")
        if options.empty: return False
        if not self.switch_cottage(options.iloc[0]["ID_res"], cottage_ID): print("error while switching cottages")
        return True
        

    def get_empty(self, options, start, end, side = "both"):
        if side not in ["left", "right", "both"]:
            print("get_empty: invalid side {}".format(side))
            return options
        assignments = self.reservation_assignments()
        if side == "left" or side == "both":
            options["left_empty"] = start
            options["left_empty"] = options[["ID_res", "left_empty"]].values.tolist()
            options["left_empty"] = options["left_empty"].map(lambda row: self.cottages[assignments[row[0]]].empty_day(row[1]))
        if side == "right" or side == "both":
            options["right_empty"] = end
            options["right_empty"] = options[["ID_res", "right_empty"]].values.tolist()
            options["right_empty"] = options["right_empty"].map(lambda row: self.cottages[assignments[row[0]]].empty_day(row[1]))
        
        if side == "left":
            options = options[options["left_empty"]]
            return options
        if side == "right":
            options = options[options["right_empty"]]
            return options
        if side == "both":
            options = options[options["left_empty"].add(options["right_empty"])]
            if options.empty: return options
            options = options.sort_values(by = ["left_empty", "right_empty"], ascending = False)
            return options

    def switch_cottage(self, ID_res, new_cottage_ID):
        combinations = self.combinations
        assignments = self.reservation_assignments()
        reservation_old = self.cottages[assignments.loc[ID_res]].find_reservation(ID_res)
        reservation_new = combinations.loc[(combinations["ID_res"] == ID_res).multiply(combinations["ID_cot"] == new_cottage_ID)].squeeze()
        if self.cottages[new_cottage_ID].allowed_reservation((reservation_new["ID_res"], reservation_new["upgrade"]), reservation_new["day"], reservation_new["Length of Stay"]):
            self.cottages[assignments.loc[ID_res]].remove_reservation(reservation_old)
            self.cottages[new_cottage_ID].add_reservation((reservation_new["ID_res"], reservation_new["upgrade"]), reservation_new["day"], reservation_new["Length of Stay"])
            return True
        return False
    
    def swap_cottages(self, ID_res1, ID_res2):
        combinations = self.combinations
        assignments = self.reservation_assignments()
        cottage1 = assignments.loc[ID_res1]
        cottage2 = assignments.loc[ID_res2]
        reservation_old1 = self.cottages[cottage1].find_reservation(ID_res1)
        reservation_old2 = self.cottages[cottage2].find_reservation(ID_res2)
        reservation_new1 = combinations.loc[(combinations["ID_res"] == ID_res1).multiply(combinations["ID_cot"] == cottage2)].squeeze()
        reservation_new2 = combinations.loc[(combinations["ID_res"] == ID_res2).multiply(combinations["ID_cot"] == cottage1)].squeeze()
        self.cottages[cottage1].remove_reservation(reservation_old1)
        self.cottages[cottage2].remove_reservation(reservation_old2)
        if self.cottages[cottage2].allowed_reservation((reservation_new1["ID_res"], reservation_new1["upgrade"]), reservation_new1["day"], reservation_new1["Length of Stay"]) and \
           self.cottages[cottage1].allowed_reservation((reservation_new2["ID_res"], reservation_new2["upgrade"]), reservation_new2["day"], reservation_new2["Length of Stay"]):
               self.cottages[cottage2].add_reservation((reservation_new1["ID_res"], reservation_new1["upgrade"]), reservation_new1["day"], reservation_new1["Length of Stay"])
               self.cottages[cottage1].add_reservation((reservation_new2["ID_res"], reservation_new2["upgrade"]), reservation_new2["day"], reservation_new2["Length of Stay"])
               return True
        self.cottages[cottage1].add_reservation((reservation_new1["ID_res"], reservation_new1["upgrade"]), reservation_new1["day"], reservation_new1["Length of Stay"])
        self.cottages[cottage2].add_reservation((reservation_new2["ID_res"], reservation_new2["upgrade"]), reservation_new2["day"], reservation_new2["Length of Stay"])
        return False
        
            
        
        


    @property
    def score(self):
        total = 0
        for cottage in self.cottages.values(): total += cottage.score
        return total
    
    @property
    def upgrade_count(self):
        total = 0
        for cottage in self.cottages.values(): total += cottage.upgrade_count
        return total
    
    @property
    def gaps(self):
        total = 0
        for cottage in self.cottages.values(): total += cottage.gaps
        return total
    
    @property
    def legionellas(self):
        total = 0
        for cottage in self.cottages.values(): total += cottage.legionellas
        return total
    
    @property
    def fritothus(self):
        total = 0
        for cottage in self.cottages.values(): total += cottage.fritothus
        return total