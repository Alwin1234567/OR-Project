class Cottage():
    
    def __init__(self, ID, days):
        self.ID = ID
        self.days = [None] * days
        
        
    def add_reservation(self, reservation, start_day, days):
        if self.days[start_day:start_day + days] != [None] * days:
            print("!!! reservationspace not free")
            return
        else: self.days[start_day:start_day + days] = [reservation] * days
    
    def remove_reservation(self, reservation):
        if reservation not in self.days: 
            print("!!! reservation not in cottage")
            return
        self.days = list(map(lambda day: day.replace(reservation, None), self.days))
    
    def allowed_reservation(self, reservation, start_day, days):
        if self.days[start_day:start_day + days] != [None] * days: return False
        return True
    
    def calculate_score(self):
        score = 0
        for reservation in self.reservations:
            if reservation[1]: score += 1
        gap = False
        gap_count = 0
        for day in self.days:
            if not gap and day == None:
                gap = True
                gap_count = 1
                score += 1
            elif gap and day == None:
                gap_count += 1
                if gap_count > 21:
                    score += 12
                    gap_count = 0
            elif gap and day != None: gap = False
        return score
    
    def display_days(self):
        days = list()
        for day in self.days:
            if day == None: days.append(None)
            else: days.append(day[0])
        msg = str(days) + str(self.score)
        print(msg)
                
    
    @property
    def score(self): return self.calculate_score()
    
    @property
    def reservations(self):
        items = set(self.days)
        if None in items: items.remove(None)
        return items
        