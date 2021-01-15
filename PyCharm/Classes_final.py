
import sys
from copy import deepcopy


def distance(loc1, loc2):
    return ((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)**0.5


class RideSharing:

    requests = []
    tours = []

    def add_request(self, pickup_loc, dropoff_loc, request_time, max_waiting_duration):
        self.requests.append(Request(pickup_loc, dropoff_loc, request_time, max_waiting_duration))

    def remove_request(self, request):
        if request in self.requests:
            self.requests.remove(request)

    def add_tour(self, depot_loc, latest_return=sys.maxsize):
        self.tours.append(Tour(depot_loc, latest_return))

    def remove_tour(self, tour):
        if tour in self.tours:
            self.tours.remove(tour)

    def solve(self):
        parallel_insertion(self.tours, self.requests)

    def __init__(self):
        pass


class Tour:

    tour = []
    early = []
    late = []
    length = 0
    total_cost = 0

    def __init__(self, depot_loc, latest_return=sys.maxsize):
        depot = Request(depot_loc, depot_loc, 0, latest_return)
        self.tour += [depot, depot]
        self.early += [0, 0]
        self.late += [latest_return, latest_return]
        self.length += 2

    def get_total_cost(self):
        return self.total_cost

    def feasible(self, place, i):
        if place.is_dropoff and place.request.pickup not in self.tour[:i]:
            return False
        if place.is_pickup and place.request.dropoff in self.tour[:i]:
            return False
        e, l = self.insertion_time_window(place, i)
        return e <= l

    def insertion_cost(self, place, i):
        return (distance(self.tour[i-1], place.loc) + distance(place.loc, self.tour[i].loc)
                - distance(self.tour[i-1].loc, self.tour[i].loc))

    def insertion_time_window(self, place, i):
        e = max(place.request.request_time, self.early[i-1] + distance(self.tour[i-1].loc, place.loc))
        l = min(place.request.end_t, self.late[i] - distance(place.loc, self.tour[i].loc))
        return e, l

    def insert(self, place, i):
        self.total_cost += self.insertion_cost(place, i)
        self.tour.insert(i, place)
        self.length += 1
        self.update(i)

    def update(self, i):
        e, l = self.insertion_time_window(self.tour[i], i)
        self.early.insert(i, e)
        self.late.insert(i, l)
        # Update der Zeitfenster (late) der vorigen Orte
        for k in range(i-1, -1, -1):
            self.late[k] = min(self.late[k], self.late[k+1] - distance(self.tour[k].loc, self.tour[k+1].loc))
        # Update der Zeitfenster (early) der nachfolgenden Orte
        for k in range(i+1, self.length):
            self.early[k] = max(self.early[k], self.early[k-1] + distance(self.tour[k-1].loc, self.tour[k].loc))

    def printable(self):
        result= []
        for i in range(self.length):
            if i == 0 or i == self.length-1:
                typ = "Depot"
            elif self.tour[i].is_pickup:
                typ = "Pick-Up"
            else:
                typ = "Drop_Off"
            result.append((self.tour[i].request.id, self.tour[i].loc, self.early[i], typ))
        return result


class Request:

    count = 0

    def __init__(self, pickup_loc, dropoff_loc, request_time, max_waiting_duration):
        self.id = Request.count
        Request.count += 1
        self.request_time = request_time
        self.max_waiting_duration = max_waiting_duration
        self.latest_dropoff = request_time + distance(pickup_loc, dropoff_loc) + max_waiting_duration
        self.pickup = PickUp(pickup_loc, self)
        self.dropoff = DropOff(dropoff_loc, self)


class Location:

    def __init__(self, loc, request):
        self.loc = loc
        self.request = request


class PickUp(Location):
    is_pickup = True
    is_dropoff = False

    def __init__(self, loc, request):
        super().__init__(loc, request)


class DropOff(Location):
    is_pickup = False
    is_dropoff = True

    def __init__(self, loc, request):
        super().__init__(loc, request)


def parallel_insertion(tours, requests, M=sys.maxsize):
    reject = []
    # Kunden = copy.deepcopy(fiktivekunden)

    while requests:
        pOpt = M
        for j in range(len(requests)):
            for k in range(len(tours)):
                # spos: Position in Tour k, an der der Pickup des Kunden eingefügt wird
                for spos in range(1, tours[k].length):
                    if tours[k].feasible(requests[j].pickup, spos):
                        skosten = tours[k].insertion_cost(requests[j].pickup, spos)

                        # speichert die aktuell gültige Tour in einer temporären Variablen
                        tour_temp = deepcopy(tours[k])

                        # füge den Pickup des Kunden vorübergehend in den Tourenplan ein und Update der Zeitfenster
                        tour_temp.insert(requests[j].pickup, spos)

                        # Prüfe für alle Positionen im Tourenplan nach dem eingefügten Pickup ob es einen möglichen Drop-off gibt
                        for epos in range(spos + 1, tour_temp.length):
                            if tour_temp.feasible(requests[j].dropoff, epos):
                                ekosten = tour_temp.insertion_cost(requests[j].dropoff, epos)
                                if skosten + ekosten < pOpt:
                                    reqOpt = requests[j]
                                    tourOpt = tours[k]
                                    sposOpt = spos
                                    eposOpt = epos
                                    pOpt = skosten + ekosten

        if pOpt < M:
            # Setze den Pickup und Drop-Off des Kunden ein und aktualisiere Zeitfenster
            tourOpt.insert(reqOpt.pickup, sposOpt)
            tourOpt.insert(reqOpt.dropoff, eposOpt)

            # Entferne den eigesetzten Kunden aus der Liste der noch ausstehenden Kunden
            requests.remove(reqOpt)
        else:
            # Wenn kein Kunde den Feasibility mehr besteht, speichere die abgewiesenen Kunden und leere die Liste
            reject = deepcopy(requests)
            requests = []

    return tours, reject
