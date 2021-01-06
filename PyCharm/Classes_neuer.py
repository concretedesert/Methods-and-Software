import sys
from copy import deepcopy


def euclidean(loc1, loc2):
    return ((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)**0.5


class Location:

    def __init__(self, loc, req):
        self.loc = loc
        self.request = req


class Origin(Location):
    is_origin = True
    is_destination = False

    def __init__(self, loc, req):
        super().__init__(loc, req)


class Destination(Location):
    is_origin = False
    is_destination = True

    def __init__(self, loc, req):
        super().__init__(loc, req)


class Request:
    _count = 0

    def __init__(self, orig_loc, dest_loc, req_t, alpha=15):
        self.id = Request._count
        Request._count += 1
        self.req_t = req_t
        self.alpha = alpha
        self.end_t = req_t + euclidean(orig_loc, dest_loc) + alpha
        self.origin = Origin(orig_loc, self)
        self.destination = Destination(dest_loc, self)


class Tour:

    def __init__(self, depot_loc=(0, 0), M=sys.maxsize):
        depot = Request(depot_loc, depot_loc, 0, M)
        self.tour = [depot.origin, depot.destination]
        self.early = [0, 0]
        self.late = [M, M]
        self.length = 2
        self.total_cost = 0
        self.M = M

    # Beim Updaten bestimmen
    def get_total_cost(self):
        pass

    # Überprüfe, ob Pick-Up / Drop-Off (place) des Kunden an Position i in der Tour zulässig ist
    def feasible(self, place, i):
        # Für Destination muss gelten: Pick-Up vor Drop-Off, Drop-Off in der gleichten Tour wie Pick-Up
        if place.is_destination and place.request.origin not in self.tour[:i]:
            return False
        # Origin nicht nach Destination einfügbar
        if place.is_origin and place.request.destination in self.tour[:i]:
            return False
        # überprüfen der Zeitfenster: Early < Late
        e, l = self.insertion_time_window(place, i)
        return e <= l

    # Einfügekosten, die entstehen, falls Location in Tour an Position i eingefügt wird
    def insertion_cost(self, place, i):
        return (euclidean(self.tour[i-1].loc, place.loc) + euclidean(place.loc, self.tour[i].loc)
                - euclidean(self.tour[i-1].loc, self.tour[i].loc))

    # berechne Zeitfenster
    def insertion_time_window(self, place, i):
        e = max(place.request.req_t, self.early[i-1] + euclidean(self.tour[i-1].loc, place.loc))
        l = min(place.request.end_t, self.late[i] - euclidean(place.loc, self.tour[i].loc))
        return e, l

    def insert(self, place, i):
        self.total_cost += self.insertion_cost(place, i)
        self.tour.insert(i, place)
        self.length += 1
        self.update(i)

    def update(self, i):
        # Berechnung und Einfügen des Zeitfensters des neuen Ortes
        e, l = self.insertion_time_window(self.tour[i], i)
        self.early.insert(i, e)
        self.late.insert(i, l)
        # Update der Zeitfenster (late) der vorigen Orte
        for k in range(i-1, -1, -1):
            self.late[k] = min(self.late[k], self.late[k+1] - euclidean(self.tour[k].loc, self.tour[k+1].loc))
        # Update der Zeitfenster (early) der nachfolgenden Orte
        for k in range(i+1, self.length):
            self.early[k] = max(self.early[k], self.early[k-1] + euclidean(self.tour[k-1].loc, self.tour[k].loc))

    def printable(self):
        abfolge = []
        for i in range(self.tour.length):
            type = "Origin" if self.tour[i].is_origin else "Destination"
            abfolge.append((self.tour[i].request.id, self.tour[i].loc, self.early[i], type))
        return abfolge


class Decision_Epoch:
    pass

def parallel_insertion(tours, requests, M=sys.maxsize):
    reject = []
    # Kunden = copy.deepcopy(fiktivekunden)

    while requests:
        pOpt = M
        for j in range(len(requests)):
            for k in range(len(tours)):
                # spos: Position in Tour k, an der der Pickup des Kunden eingefügt wird
                for spos in range(1, tours[k].length):
                    if tours[k].feasible(requests[j].origin, spos):
                        skosten = tours[k].insertion_cost(requests[j].origin, spos)

                        # speichert die aktuell gültige Tour in einer temporären Variablen
                        tour_temp = deepcopy(tours[k])

                        # füge den Pickup des Kunden vorübergehend in den Tourenplan ein und Update der Zeitfenster
                        tour_temp.insert(requests[j].origin, spos)

                        # Prüfe für alle Positionen im Tourenplan nach dem eingefügten Pickup ob es einen möglichen Drop-off gibt
                        for epos in range(spos + 1, tour_temp.length):
                            if tour_temp.feasible(requests[j].destination, epos):
                                ekosten = tour_temp.insertion_cost(requests[j].destination, epos)
                                if skosten + ekosten < pOpt:
                                    reqOpt = requests[j]
                                    tourOpt = tours[k]
                                    sposOpt = spos
                                    eposOpt = epos
                                    pOpt = skosten + ekosten

        if pOpt < M:
            # Setze den Pickup und Drop-Off des Kunden ein und aktualisiere Zeitfenster
            tourOpt.insert(reqOpt.origin, sposOpt)
            tourOpt.insert(reqOpt.destination, eposOpt)

            # Entferne den eigesetzten Kunden aus der Liste der noch ausstehenden Kunden
            requests.remove(reqOpt)
        else:
            # Wenn kein Kunde den Feasibility mehr besteht, speichere die abgewiesenen Kunden und leere die Liste
            reject = deepcopy(requests)
            requests = []

    return tours, reject
