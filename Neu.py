# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 20:54:16 2020

@author: mk1
"""

class Request:
    alpha = 10 # minutes
    service_time = 2 # minutes
    visit_origin = -1 # not planned yet
    visit_dest = -1 # not planned yet
    
    def euclidean_distance(self):
        return ((self.start_loc[0] - self.dest_loc[0])**2 
                + (self.start_loc[1] - self.dest_loc[1])**2)**0.5
    
    def __init__(self, start_loc, dest_loc, req_time):
        self.start_loc = start_loc
        self.dest_loc = dest_loc
        self.req_time = req_time
        self.end_time = self.req_time + self.euclidean_distance() + self.alpha
        
    def check_visit_times(self, t_origin, t_dest):
        if t_origin < self.req_time or t_origin > t_dest or t_dest > self.end_time:
            return False
        return True
    
    def check_visit_start(self, t_origin):
        return self.req_time <= t_origin <= self.end_time
    
    def check_visit_dest(self, t_dest):
        return self.req_time <= t_dest <= self.end_time
    
    def set_visit_times(self, t_origin, t_dest):
        if not self.check_visit_times(t_origin, t_dest):
            raise ValueError("Fehlerhafte Besuchszeiten")
        self.visit_origin = t_origin
        self.visit_dest = t_dest
        
class Tourplan:
    
    def __init__(self):
        depot = Request((0,0), (0,0), 0)
        depot.end_time = 1000000 # M, oder Begrenzung
        self.tourenplan = [(depot, 0), (depot, 1)] # 0: origin, 1: destination
        self.coordinates = [(depot.start_loc), (depot.dest_loc)]
        
    def euclidean_distance(loc1, loc2):
        return ((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)**0.5
    
    def insert_costs(self, request, i, j):
        if j - i == 1:
            return (Tourplan.euclidean_distance(self.coordinates[i-1], request.start_loc) 
            + Tourplan.euclidean_distance(request.start_loc, request.dest_loc) 
            + Tourplan.euclidean_distance(request.dest_loc, self.coordinates[i]) 
            - Tourplan.euclidean_distance(self.coordinates[i-1], self.coordinates[i]))
        else:
            return self.euclidean_distance(self.coordinates[i-1], request.start_loc) \
            + self.euclidean_distance(request.start_loc, self.coordinates[i]) \
            + self.euclidean_distance(self.coordinates[j-1], request.dest_loc) \
            + self.euclidean_distance(request.dest_loc, self.coordinates[j]) \
            - self.euclidean_distance(self.coordinates[i-1], self.coordinates[i]) \
            - self.euclidean_distance(self.coordinates[j-1], self.coordinates[j])
    
    def insert_costs_single(self, loc, i): # startordest = 0 / 1
        return self.euclidean_distance(self.coordinates[i-1], loc) \
        + self.euclidean_distance(loc, self.coordinates[i]) \
        - self.euclidean_distance(self.coordinates[i-1], self.coordinates[i]) 
    
    def insert_feasible(self, request, i, j):
        t_start = self.euclidean_distance(self.coordinates[i-1], request.start_loc) \
            + self.euclidean_distance(request.start_loc, self.coordinates[i])
        lag_start = self.insert_costs_single(request.start_loc, i)
        t_dest = self.euclidean_distance(self.coordinates[j-1], request.dest_loc) \
            + self.euclidean_distance(request.dest_loc, self.coordinates[j]) \
            + lag_start
        lag_dest = self.insert_costs_single(request.dest_loc, j) \
            + lag_start
        
        if not request.check_visit_times(t_start, t_start):
            return False
        
        for place in self.tourenplan[i:j]:
            if place[1] == 0:
                if not place[0].check_visit_start(place[0].visit_origin + lag_start):
                    return False
            else:
                if not place[0].check_visit_dest(place[0].visit_dest + lag_start):
                    return False
        
        if not request.check_visit_times(t_dest, t_dest):
            return False
        
        for place in self.tourenplan[j:]:
            if place[1] == 0:
                if not place[0].check_visit_start(place[0].visit_origin + lag_dest):
                    return False
            else:
                if not place[0].check_visit_dest(place[0].visit_dest + lag_dest):
                    return False
        
        return True
    
    def update_visit_times(self, request, i, j):
        lag_start = self.insert_costs_single(request.start_loc, i)
        lag_dest = self.insert_costs_single(request.dest_loc, j) \
            + lag_start
        
        for place in self.tourenplan[i:j]:
            if place[1] == 0:
                place[0].visit_origin += lag_start
            else:
                place[0].visit_origin += lag_dest
        
        for place in self.tourenplan[j:]:
            if place[1] == 0:
                place[0].visit_origin += lag_start
            else:
                place[0].visit_origin += lag_dest
        
    
    def insert(self, request, i, j):
        t_start = self.euclidean_distance(self.coordinates[i-1], request.start_loc) \
            + self.euclidean_distance(request.start_loc, self.coordinates[i])
        lag_start = self.insert_costs_single(request.start_loc, i)
        t_dest = self.euclidean_distance(self.coordinates[j-1], request.dest_loc) \
            + self.euclidean_distance(request.dest_loc, self.coordinates[j]) \
            + lag_start
        
        self.update_visit_times(request, i, j)
        
        self.tourenplan.insert(j, (request, 1))
        self.tourenplan.insert(i, (request, 0))
        self.coordinates.insert(j, request.dest_loc)
        self.coordinates.insert(i, request.start_loc)
        
        request.visit_origin = t_start
        request.visit_dest = t_dest

# Wie entscheiden, welcher Kunde zuerst eingefügt wird

def parallel_insertion(tourplan, requests):
    while requests:
        M = 1000000
        pOpt = M 
        for req in requests:
            for tour in tourplan:
                for i in range(1, tourplan.length): # Start
                    for j in range(i+1, tourplan.length): # Ende
                        if tour.insert_costs(req, i, j) < pOpt and tour.insert_feasible(req, i, j):
                            tourOpt = tour
                            reqIns = req
                            iOpt = i
                            jOpt = j
                            pOpt = tour.insert_costs(req, i, j)
        if pOpt < M: # Breaken, falls nicht einfügbar?
            tourOpt.insert(reqIns, iOpt, jOpt)
            requests.remove(reqIns)

def LNS(beta, y1, y2, tourplan, t):
    for i in range(beta):
        pass
    
    
    
    
    
    
    
    
    
    
    
    
    
