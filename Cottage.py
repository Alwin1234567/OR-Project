class Cottage():
    """
    Class that stores the information of a specific cottage.
    """
    def __init__(self, ID, days, startday,\
                 scores = {"Gap": 6, "GapFriToThu": -3, \
                           "GapLegionella": 12, "Upgrade": 1}):
        self.ID = ID
        self.days = [None] * days
        self.startday = startday.weekday()
        self.scores = scores
        
        
    def add_reservation(self, reservation, start_day, days):
        """
        Function that checks if the reservation is possible and stores the reservation.

        Parameters
        ----------
        reservation : (ID_res, BOOL)
            Tuple that stores the reservation ID and wheter or not this is an upgrade.
        start_day : INT
            Integer with the arrival day for the reservation.
        days : INT
            Days the reservation lasts.

        """
        if self.days[start_day:start_day + days] != [None] * days:
            print("!!! reservationspace not free")
            return
        else: self.days[start_day:start_day + days] = [reservation] * days
    
    def remove_reservation(self, reservation):
        """
        Function that removes a reservation from the cottage

        Parameters
        ----------
        reservation : (ID_res, BOOL)
            Tuple that stores the reservation ID and wheter or not this is an upgrade.

        """
        if reservation not in self.days or reservation == None: 
            print("!!! reservation not in cottage")
            return
        for i, day in enumerate(self.days):
            if day == reservation: self.days[i] = None
    
    def allowed_reservation(self, reservation, start_day, days):
        """
        Function that tests if a reservation is possible in this cottage.

        Parameters
        ----------
        reservation : (ID_res, BOOL)
            Tuple that stores the reservation ID and wheter or not this is an upgrade.
        start_day : INT
            Integer with the arrival day for the reservation.
        days : INT
            Days the reservation lasts.

        Returns
        -------
        bool
            Boolean that discribes if a reservation is possible in this cottage.
        """
        if self.days[start_day:start_day + days] != [None] * days: return False
        return True
    
    def calculate_score(self, return_sort = None):
        score = 0
        for reservation in self.reservations:
            if reservation[1]: score += self.scores["Upgrade"]
        gap = False
        gap_count = 0
        gaps_count = 0
        fritothu = 0
        legionella_count = 0
        fritothu_gap = 0
        for i, day in enumerate(self.days):
            if not gap and day == None:
                fritothu = -100
                if (i + self.startday) % 7 == 4: fritothu = 0
                fritothu += 1
                gap = True
                gap_count = 1
                score += self.scores["Gap"]
                gaps_count += 1
            elif gap and day == None:
                if (i + self.startday) % 7 == 4: fritothu = 0
                fritothu += 1
                if fritothu == 7: 
                    score += self.scores["GapFriToThu"]
                    fritothu_gap += 1
                gap_count += 1
                if gap_count == 22:
                    score += self.scores["GapLegionella"]
                    legionella_count += 1
            elif gap and day != None: gap = False
        if return_sort == "gap": return gaps_count
        if return_sort == "legionella": return legionella_count
        if return_sort == "fritothu": return fritothu_gap
        return score
    
    def display_days(self):
        """
        Function that prints the list of all days.
        """
        days = list()
        for day in self.days:
            if day == None: days.append(None)
            else: days.append(day[0])
        msg = str(days) + str(self.score)
        print(msg)
    
    def find_reservation(self, reservation_ID):
        for day in self.days:
            if day != None:
                if day[0] == reservation_ID: return day
    
    def empty_day(self, day):
        if day == -1 or day > len(self.days) - 1: return False
        if self.days[day] == None: return True
        return False
                
    
    @property
    def score(self): return self.calculate_score()
    
    @property
    def reservations(self):
        items = set(self.days)
        if None in items: items.remove(None)
        return list(items)
    
    @property
    def upgrade_count(self):
        total = 0
        for reservation in self.reservations:
            if reservation[1]: total += self.scores["Upgrade"]
        return total
    
    @property
    def gaps(self): return self.calculate_score(return_sort = "gap")
    
    @property
    def legionellas(self): return self.calculate_score(return_sort = "legionella")
    
    @property
    def fritothus(self): return self.calculate_score(return_sort = "fritothu")