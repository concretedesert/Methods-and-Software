
from Classes import *

tours = []

for i in range(2):
    tours.append(Tour())

#r1 = Request((1, 1), (5, 5), 0)
#r2 = Request((2, 2), (-2, -2), 0)
#r3 = Request((0, 0), (-1, 1), 0)

#requests = [r1, r2, r3]
r1 = Request((1, 1), (7, 7), 0)
r2 = Request((0, 0), (-7, -7), 1)
places = split_requests([r1, r2])

plan = Tourplan(tours, places)
plan.insertion_heuristic()

# Problem: Late, Early wird doppelt eingefügt
for tour in plan.tours:
    print(tour.early)
    print(tour.late)


"""
    def __init__(self, tours, places, M=10000):
        self.tours = tours
        self.places = places
        self.M = M

    def insertion_heuristic(self):
        while self.places:
            cOpt = self.M
            for place in self.places:
                for tour in self.tours:
                    for i in range(1, tour.length):
                        if tour.feasible(place, i) and tour.insertion_cost(place, i) < cOpt:
                            tourOpt = tour
                            iOpt = i
                            placeOpt = place
                            cOpt = tour.insertion_cost(place, i)
            tourOpt.insert(placeOpt, iOpt)
            self.places.remove(placeOpt)
            #tourOpt.update(iOpt)

"""