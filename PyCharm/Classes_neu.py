import sys
from copy import deepcopy


# Berechnung der euklidischen Distanz aus zwei Orten loc1, loc2 (Tupel: (num, num))
def euclidean(loc1, loc2):
    return ((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)**0.5


# Location: Beinhaltet die Koordinaten eines Ortes loc (Tupel: (num, num))
# und das dazugehörige Request (Objekt: Request)
class Location:

    def __init__(self, loc, req):
        self.loc = loc
        self.request = req


# Origin: Erbt von Location.
# Identifikation: Handelt es such um die Origin (Pick-Up des Kunden, True), oder die Destination (Drop-off, False)
class Origin(Location):
    is_origin = True
    is_destination = False

    def __init__(self, loc, req):
        super().__init__(loc, req)


# Destination: Erbt von Location.
# Identifikation: Handelt es such um die Origin (Pick-Up des Kunden, False), oder die Destination (Drop-off, True)
class Destination(Location):
    is_origin = False
    is_destination = True

    def __init__(self, loc, req):
        super().__init__(loc, req)


# Request: Kundenanfrage nach dem Ride-Sharing-Service
# Input: Location & Destination der Anfrage orig_loc, dest_loc (Tupel: (num, num)) und Erzeugung der zugehörigen Objekte
# Input: Zeitpunkt der Anfrage req_t (num), entspricht dem frühesten Pick-Up-Zeitpunkt
# Input: alpha (num) bezeichnet die maximal tolerierte Verzögerung (durch Wartezeit, De-Touren) des Kunden
# Berechne: Spätestens tolierte Ankunftzeit end_t (num) des Kunden:
#           Zeitpunkt der Anfrage req_t + Reisezeit zwischen Origin und Destination (euklidische Distanz) + alpha
# Jedes Request wird durch eine einzigartige ID (num) identifiziert
class Request:
    # Globale Zählvariable für Erstellung von Requests
    _count = 0

    def __init__(self, orig_loc, dest_loc, req_t, alpha=15):
        # Erzeuge einzigartige ID für jedes Request, hochzählen von count, falls neues Request erzeugt
        self.id = Request._count
        Request._count += 1
        self.req_t = req_t
        self.alpha = alpha
        # Berechne späteste tolerierte Ankunftszeit
        self.end_t = req_t + euclidean(orig_loc, dest_loc) + alpha
        self.origin = Origin(orig_loc, self)
        self.destination = Destination(dest_loc, self)


# Tour: Beschreibt die Route eines Vehikels des Ride-Sharing-Dienstleisters
# Input: Location des Depots depot_loc (Tupel: (num, num))
# Input: M (num) Wahlweise: große Zahl, oder spätester Rückkehrzeitpunkt des Vehikels zum Depot
# tour: bezeichnet die Reihenfolge der angefahrenen Orte
# Early, Late: Zeitfenster nach Campbell und Savelsbergh, early (num) bezeichnet sowohl den frühesten mögichen,
#              als auch den geplanten Anfahrtzeitpunkt. Late (num) bezeichnet den spätest möglichen Anfahrzeitpunkt
# Length (num) bezeichnet die derzeitige Länge der Tour (# der Anfahrtorte)
class Tour:

    def __init__(self, depot_loc=(0, 0), M=sys.maxsize):
        depot = Request(depot_loc, depot_loc, 0, M)
        self.tour = [depot.origin]
        self.early = [0]
        self.late = [M]
        self.length = 1
        self.M = M

    # Berechnet die derzeitige Position (Tupel: (num, num)) des Vehikels zum Zeitpunkt time (num)
    def get_vehicle_loc(self, time):
        # Fall: Fahrzeug wartet beim zuletzt besuchten Ort
        if time >= self.early[-1]:
            return self.tour[-1].loc
        left = [e for e in self.early if e <= time]
        # Fall: Fahrzeug derzeit direkt an einem Ort
        if left[-1] == time:
            return self.tour[len(left)-1].loc
        # Fall: Fahrzeug wartet beim letzten Ort, nächste Kundenanfrage noch nicht eingetroffen
        if time <= self.tour[len(left)].request.req_t:
            return self.tour[len(left)-1].loc
        # Fall: Fahrzeug befindet sich auf dem Weg zwischen zwei Orten
        end = self.early[len(left)]
        start = end - euclidean(self.tour[len(left)-1].loc, self.tour[len(left)].loc)
        frac = (time - start) / (end - start)
        x = self.tour[len(left)-1].loc[0] + frac * (self.tour[len(left)].loc[0] - self.tour[len(left)-1].loc[0])
        y = self.tour[len(left)-1].loc[1] + frac * (self.tour[len(left)].loc[1] - self.tour[len(left)-1].loc[1])
        return x, y

    # Kunden im Vehikel zum Zeitpunkt time
    def get_O_k(self, time):
        left = [self.tour[i] for i in range(self.length) if self.early[i] <= time]
        right = [self.tour[i] for i in range(self.length) if self.early[i] > time]
        requests = []
        for k in left:
            if k.is_origin and k.request.destination in right:
                requests.append(k.request)
        return requests

    # Akzeptierte Kunden, die auf das Vehikel warten
    def get_U_k(self, time):
        left = [self.tour[i] for i in range(self.length) if self.early[i] <= time]
        right = [self.tour[i] for i in range(self.length) if self.early[i] > time]
        requests = []
        for k in right:
            if k.is_origin and k.request.destination in right:
                requests.append(k.request)
        return requests

    def total_cost(self):
        total = 0
        for i in range(self.length-1):
            total += euclidean(self.tour[i].loc, self.tour[i+1].loc)
        return total + euclidean(self.tour[-1].loc, self.tour[0].loc)

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

    # Einfügekosten, die entstehen, falls Location in Tour eingefügt wird
    def insertion_cost(self, place, i):
        ante = self.tour[i-1]
        # Am Ende eingefügt, berechne Einfügekosten anhand Pendeltour
        post = self.tour[0] if i == self.length else self.tour[i]
        return (euclidean(ante.loc, place.loc) + euclidean(place.loc, post.loc)
                - euclidean(ante.loc, post.loc))

    # berechne Zeitfenster
    def insertion_time_window(self, place, i):
        e = max(place.request.req_t, self.early[i-1] + euclidean(self.tour[i-1].loc, place.loc))
        late_post = self.M if i == self.length else self.late[i]
        post = self.tour[0] if i == self.length else self.tour[i]
        l = min(place.request.end_t, late_post - euclidean(place.loc, post.loc))
        return e, l

    def insert(self, place, i):
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


class Decision_Epoch:

    def __init__(self, new_request, tours):
        self.t_r = new_request.req_t
        self.I_k = [tour.get_vehicle_loc for tour in tours]
        self.O_k = [tour.get_O_k for tour in tours]
        self.U_k = [tour.get_U_k for tour in tours]
        self.r_k = new_request

    def request_accepted(self):
        return True

    def LNS_accept(self, beta):
        w = deepcopy(self.tours)
        w_best = w
        found = False
        i = 0
        while i < beta and not found:
            pass
