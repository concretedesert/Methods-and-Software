#!/usr/bin/env python
# coding: utf-8

# In[1]:


from copy import deepcopy
import sys


# ![Request,%20Pickup,%20Dropoff.jpg](attachment:Request,%20Pickup,%20Dropoff.jpg)

# Eine Kundenanfrage $r$ (*request*) ist in der Menge der Kundenanfragen $R$ ($r \in R$) enthalten. Jede Kundenanfrage hat eine Empfangszeit $t_r$ (*receiving time*). Sie beschreibt den Zeitpunkt, zu dem der Kunde eine Anfrage nach einer Fahrt des Ride-Sharing-Anbieters stellt.
#
# Der Kunde frägt hierbei eine Fahrt von einem Startstandort $p_r$ (*Pick-Up*) zu einem Zielstandort $d_r$ (*Drop-Off*) an. Die Standorte werden durch Klassen repräsentiert, die die Koordinaten ($x, y$) beinhalten, wobei $x, y \in \mathbb{R}$.
#
# Die Fahrt muss innerhalb des Zeitfensters [$t_r, e_r$] (*time window*) durchgeführt werden. Der früheste Abholzeitpunkt wird durch die Empfangszeit der Kundenanfrage $t_r$ festgelegt. Vorausbuchungen sind somit nicht möglich. Der späteste Ankunftszeitpunkt des Kunden am Zielstandort $e_r = t_r + c_{p_r,d_r} + \alpha$ ergibt sich aus der Empfangszeit der Anfrage $t_r$, der euklidischen Distanz zwischen dem Start- und dem Zielstandort $c_{p_r,d_r}$ und $\alpha$. Der Parameter $\alpha$ bezeichnet die vom Kunden maximal tolerierte Verzögerungszeit, die durch Wartezeiten und abweichende Touren durch Bedienung anderer Kunden ensteht
#
# Auf Bedienzeiten, etwa die Einsteigezeit und die Verifizierung des Kunden wird wegen der Einfachheit verzichtet.

# In[2]:


class Request:
    # Klassenübergreifende Zählvariable: Anzahl der erstellten Request-Objekte
    count = 0

    def __init__(self, pickup_loc, dropoff_loc, request_time, alpha):
        # Erzeuge einzigartige ID für jedes Request-Objekt und aktualisiere Zählvariable
        self.id = Request.count
        Request.count += 1
        # Empfangszeit der Anfrage und frühester Abholzeitpunkt
        self.request_time = request_time
        # Spätest mögliche Ankunftszeit des Kunden
        self.latest_dropoff = request_time + distance(pickup_loc, dropoff_loc) + alpha
        # Zur Anfrage zugehörige Start- und Zielstandorte
        self.pickup = PickUp(pickup_loc, self)
        self.dropoff = DropOff(dropoff_loc, self)


class PickUp:
    is_pickup = True
    is_dropoff = False

    def __init__(self, loc, request):
        self.loc = loc
        self.request = request


class DropOff:
    is_pickup = False
    is_dropoff = True

    def __init__(self, loc, request):
        self.loc = loc
        self.request = request


def distance(loc1, loc2):
    return ((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2) ** 0.5


# ![Tour.jpg](attachment:Tour.jpg)

# Eine Tour $v$ ist in der Menge der Touren $V$ ($v \in V$) enthalten. Jede Tour besteht anfänglich aus einer Rundreise,

# In[3]:


class Tour:

    def __init__(self, depot_loc=(0, 0), M=sys.maxsize):
        # Erstelle Pseudo-Request depot. depot_loc ist Start- und Zielstandort
        depot = Request(depot_loc, depot_loc, 0, M)
        Request.count -= 1
        depot.id = 'D'
        # Tour: Abfolge von Pickups und Dropoffs, Tour beginnt und endet mit dem Depot
        self.tour = [depot.pickup, depot.dropoff]
        # Early: Frühest mögliche und geplante Besuchszeit des Standortes in Tour.
        self.early = [0, 0]
        # Late: Spätest möglich geplante Besuchszeit
        self.late = [M, M]
        # Length: Länge der Tour
        self.length = 2
        # Gesamtkosten der Tour
        self.total_cost = 0
        # Positionen der Standorte der Tour
        self.dict_place_positions = {}

    # Check: Ist der PickUp/DropOff in Position i der Tour einfügbar?
    def check_insert_feasible(self, place, i):
        if place.is_dropoff and place.request.pickup not in self.tour[:i]:
            return False
        if place.is_pickup and place.request.dropoff in self.tour[:i]:
            return False
        e, l = self.insertion_time_window(place, i)
        return e <= l

    # Berechne entstehende Einfügekosten, falls PickUp/DropOff in Position i eingefügt wird
    def insertion_cost(self, place, i):
        return (distance(self.tour[i - 1].loc, place.loc) + distance(place.loc, self.tour[i].loc)
                - distance(self.tour[i - 1].loc, self.tour[i].loc))

    # Berechnen des Zeitfensters des PickUps/DropOffs, falls es in Position i eingefügt wird
    def insertion_time_window(self, place, i):
        # e alt:
        # e = max(place.request.req_t, self.early[i-1] + euclidean(self.tour[i-1].loc, place.loc))
        # e neu:
        e = max(place.request.request_time + distance(self.tour[i - 1].loc, place.loc),
                self.early[i - 1] + distance(self.tour[i - 1].loc, place.loc))
        l = min(place.request.latest_dropoff,
                self.late[i] - distance(place.loc, self.tour[i].loc))
        return e, l

    # füge PickUp/DropOff place in Position i ein
    def insert(self, place, i):
        self.total_cost += self.insertion_cost(place, i)
        self.tour.insert(i, place)
        self.length += 1
        self.update_after_insertion(place, i)

    # entferne den PickUp/DropOff auf Position i der Tour
    def remove(self, i):
        place = self.tour[i]
        del self.tour[i]
        del self.early[i]
        del self.late[i]
        del self.dict_place_positions[place]
        self.total_cost -= self.insertion_cost(place, i)
        self.length -= 1
        self.update_after_removal(place, i)

    # berechne die Zeitfenster des eingefügten PickUps/DropOffs, aktualisiere die restlichen Zeitfenster
    # und halte die Klasse aktuell
    def update_after_insertion(self, place, i):
        # Berechnung und Einfügen des Zeitfensters des neuen Ortes
        e, l = self.insertion_time_window(self.tour[i], i)
        self.early.insert(i, e)
        self.late.insert(i, l)
        # Update der Zeitfenster (late) der vorigen Orte
        for k in range(i - 1, -1, -1):
            self.late[k] = min(self.late[k], self.late[k + 1] - distance(self.tour[k].loc, self.tour[k + 1].loc))
        # Update der Zeitfenster (early) der nachfolgenden Orte
        for k in range(i + 1, self.length):
            self.early[k] = max(self.early[k], self.early[k - 1] + distance(self.tour[k - 1].loc, self.tour[k].loc))
        # Update der Positionen im Dictionary:
        for key in self.dict_place_positions:
            if self.dict_place_positions[key] >= i:
                self.dict_place_positions[key] += 1
        # Einfügen der Position im Dictionary
        self.dict_place_positions[place] = i

    # aktualisere die Zeitfenster der anderen PickUps/DropOffs nachdem der PickUp / DropOff an Position i entfernt wurde
    # halte Klasse aktuell
    def update_after_removal(self, place, i):
        for k in range(1, self.length):
            self.early[k] = max(self.tour[k].request.request_time + distance(self.tour[k - 1].loc, self.tour[k].loc),
                                self.early[k - 1] + distance(self.tour[k - 1].loc, self.tour[k].loc))
        for k in range(self.length - 2, -1, -1):
            self.late[k] = min(self.tour[k].request.latest_dropoff,
                               self.late[k + 1] - distance(self.tour[k].loc, self.tour[k + 1].loc))
        for key in self.dict_place_positions:
            if self.dict_place_positions[key] >= i:
                self.dict_place_positions[key] -= 1

    # gebe die Kundenanfragen der Tour aus, die zum Zeitpunkt time in dem Fahrzeug sitzen
    def get_requests_in_vehicle(self, time):
        result = []
        v = len([e for e in self.early if e <= time])
        for key in self.dict_place_positions:
            if (key.is_pickup
                    and self.dict_place_positions[key] < v
                    and self.dict_place_positions[key.request.dropoff] >= v):
                result.append(key.request)
        return result

    # gebe die Kundenanfragen der Tour aus, die zum Zeitpunkt time auf das Fahrzeug warten
    def get_waiting_requests(self, time):
        result = []
        v = len([e for e in self.early if e <= time])
        for key in self.dict_place_positions:
            if (key.is_pickup
                    and self.dict_place_positions[key] >= v
                    and self.dict_place_positions[key.request.dropoff] >= v):
                result.append(key.request)
        return result

    # Für jeden Standort in der Tour: id, loc, early=visit_time, typ
    def printable(self):
        result = []
        for i in range(self.length):
            if i == 0 or i == self.length - 1:
                typ = "Depot"
            elif self.tour[i].is_pickup:
                typ = "Pick-Up"
            else:
                typ = "Drop-Off"
            result.append((self.tour[i].request.id,
                           #self.tour[i].loc,
                           #round(self.early[i], 2),
                           # round(self.late[i], 2),
                           typ))
        return result


# In[4]:


class DecisionEpoch:

    def __init__(self, new_request, tours, beta, gamma1, gamma2):
        self.time = new_request.request_time
        self.request = new_request
        self.tours = deepcopy(tours)
        self.accept, self.solution = LNS(self, "accept", beta, gamma1, gamma2)
        if self.accept:
            self.tours = self.solution
            _, self.solution = LNS(self, "re-routing", beta, gamma1, gamma2)


# In[5]:


class RideSharing:

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
        self.requests = sorted(self.requests, key=lambda x: x.request_time)
        for request in self.requests:
            new_epoch = DecisionEpoch(request, self.tours, self.beta, self.gamma1, self.gamma2)
            self.tours = new_epoch.tours
            self.epochs.append(new_epoch)

    def __init__(self, beta, gamma1, gamma2):
        self.requests = []
        self.tours = []
        self.epochs = []
        self.beta = beta
        self.gamma1 = gamma1
        self.gamma2 = gamma2


# In[6]:


def parallel_insertion(tours, requests, time=0, M=sys.maxsize):
    reject = []
    # Kunden = copy.deepcopy(fiktivekunden)

    while requests:
        pOpt = M
        for j in range(len(requests)):
            for k in range(len(tours)):
                # + 1?
                earl_pos = min(len([e for e in tours[k].early if e <= time]) + 1, tours[k].length - 1)
                # spos: Position in Tour k, an der der Pickup des Kunden eingefügt wird
                for spos in range(earl_pos, tours[k].length):
                    if tours[k].check_insert_feasible(requests[j].pickup, spos):
                        skosten = tours[k].insertion_cost(requests[j].pickup, spos)

                        # speichert die aktuell gültige Tour in einer temporären Variablen
                        tour_temp = deepcopy(tours[k])

                        # füge den Pickup des Kunden vorübergehend in den Tourenplan ein und Update der Zeitfenster
                        tour_temp.insert(requests[j].pickup, spos)

                        # Prüfe für alle Positionen im Tourenplan nach dem eingefügten Pickup ob es einen möglichen Drop-off gibt
                        for epos in range(spos + 1, tour_temp.length):
                            if tour_temp.check_insert_feasible(requests[j].dropoff, epos):
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


# In[7]:


from random import sample, randint
from math import floor, ceil


def random_removal(tours, time, gamma1, gamma2):
    new_tours = deepcopy(tours)
    candidates = []
    for i in range(len(new_tours)):
        for elem in new_tours[i].get_waiting_requests(time):
            candidates.append((i, elem))
    removed = []
    q = len(candidates)
    n = randint(floor(gamma1 * q), ceil(gamma2 * q))
    to_remove = sample(candidates, n)
    for elem in to_remove:
        pos_pickup = new_tours[elem[0]].dict_place_positions[elem[1].pickup]
        pos_dropoff = new_tours[elem[0]].dict_place_positions[elem[1].dropoff]
        new_tours[elem[0]].remove(pos_dropoff)
        new_tours[elem[0]].remove(pos_pickup)
        removed.append(elem[1])
    return new_tours, removed


def worst_removal():
    pass


def shaw_removal():
    pass


def LNS(epoch, type, beta, gamma1, gamma2):
    plan_current = deepcopy(epoch.tours)
    plan_best = deepcopy(epoch.tours)
    if type == "accept":
        unplanned = [epoch.request]
    else:
        unplanned = []
    all_inserted = False
    iteration = 0
    while iteration < beta:
        iteration += 1
        plan_new, removed = random_removal(plan_current, epoch.time, gamma1, gamma2)
        unplanned.extend(removed)
        plan_new, reject = parallel_insertion(plan_new, unplanned, epoch.time)
        if len(reject) == 0 and type == "accept":
            return True, plan_new
        elif len(reject) == 0 and type == "re-routing":
            plan_current = plan_new
            cost_current = sum([tour.total_cost for tour in plan_current])
            cost_best = sum([tour.total_cost for tour in plan_best])
            if cost_current < cost_best:
                plan_best = plan_current
    return all_inserted, plan_best


# In[8]:


# In[9]:


n = 3  # Fahrzeuge
m = 20  # Anfragen
low = 0  # Koordinaten
up = 20  # Koordinaten
end = 100
beta = 10
g1 = 0.1
g2 = 0.9
a = 25

groß = RideSharing(beta, g1, g2)
for i in range(n):
    groß.add_tour((randint(low, up), randint(low, up)))
for i in range(m):
    groß.add_request((randint(low, up), randint(low, up)), (randint(low, up), randint(low, up)), randint(0, end), a)
groß.solve()

# In[10]:


for tour in groß.tours:
    print(tour.printable())
    print(tour.length // 2 - 1)

