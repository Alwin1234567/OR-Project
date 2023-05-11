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
        if reservation not in self.days: 
            print("!!! reservation not in cottage")
            return
        for i, day in enumerate(self.days):
            if day == reservation: self.days[i] = None
        # self.days = list(map(lambda day: day.replace(reservation, None), self.days))
    
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
    
    def calculate_score(self):
        score = 0
        for reservation in self.reservations:
            if reservation[1]: score += self.scores["Upgrade"]
        gap = False
        gap_count = 0
        fritothu = 0
        for i, day in enumerate(self.days):
            if not gap and day == None:
                fritothu = 0
                gap = True
                gap_count = 1
                score += self.scores["Gap"]
            elif gap and day == None:
                if (i + self.startday) % 7 == 4: fritothu = 0
                fritothu += 1
                if fritothu == 7: score += self.scores["GapFriToThu"]
                gap_count += 1
                if gap_count > 21:
                    score += self.scores["GapLegionella"]
                    gap_count = 0
            elif gap and day != None: gap = False
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
        
                
    
    @property
    def score(self): return self.calculate_score()
    
    @property
    def reservations(self):
        items = set(self.days)
        if None in items: items.remove(None)
        return list(items)
        