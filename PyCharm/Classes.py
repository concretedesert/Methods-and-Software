
def euclidean(loc1, loc2):
    return ((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)**0.5


def split_requests(requests):
    return sum([[r.origin, r.destination] for r in requests], [])


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
    # Globale Zählvariable für Erstellung von Requests
    count = 0

    def __init__(self, orig_loc, dest_loc, req_t, alpha=22):
        # Erzeuge einzigartige ID für jedes Request
        self.id = Request.count
        Request.count += 1
        self.req_t = req_t
        self.alpha = alpha
        # Berechne späteste tolierte Ankunftszeit
        self.end_t = req_t + euclidean(orig_loc, dest_loc) + alpha
        self.origin = Origin(orig_loc, self)
        self.destination = Destination(dest_loc, self)


class Tour:

    def __init__(self, depot_loc=(0, 0), M=10000):  # überlegen, wie M wählen
        depot = Request(depot_loc, depot_loc, 0, M)
        self.tour = [depot.origin, depot.destination]
        self.early = [0, 0]
        self.late = [M, M]
        self.length = 2

    def get_vehicle_loc(self, time):
        pass

    def feasible(self, place, i):
        # Origin in der gleichen Tour wie Destination, Destination nach Origin:
        if place.is_destination and place.request.origin not in self.tour[:i]:
            return False
        # Origin nicht nach Destination einfügbar
        if place.is_origin and place.request.destination in self.tour[:i]:
            return False
        # überprüfen der Zeitfenster: Early < Late
        e, l = self.insertion_time_window(place, i)
        return e <= l

    def insertion_cost(self, place, i):
        return (euclidean(self.tour[i-1].loc, place.loc) + euclidean(place.loc, self.tour[i].loc)
                - euclidean(self.tour[i-1].loc, self.tour[i].loc))

    def insertion_time_window(self, place, i):
        e = max(place.request.req_t, self.early[i-1] + euclidean(self.tour[i-1].loc, place.loc))
        l = min(place.request.end_t, self.late[i] - euclidean(place.loc, self.tour[i].loc))
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

    def __init__(self, req_t):
        self.t = req_t
