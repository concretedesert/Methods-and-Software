def euclidean(loc1, loc2):
    return ((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)**0.5

class Request:
    
    def __init__(self, orig_loc, dest_loc, req_t, alpha):
        self.orig_loc = orig_loc
        self.dest_loc = dest_loc
        self.req_t = req_t
        self.alpha = alpha # tolerierte Wartezeit
        self.end_t = req_t + euclidean(orig_loc, dest_loc) + alpha
    
    
class Tour:
    
    M = 100000 # große Zahl
    
    
    def __init__(self, depot_loc):
        depot = Request(depot_loc, depot_loc, 0, M)
        self.tour = []

ta = Tour((0,0))

print(ta.M)
