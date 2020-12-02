# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 20:54:16 2020

@author: mk1
"""

import numpy as np

class Request:
    alpha = 10 # minutes
    service_time = 2 # minutes
    
    def euclidean_distance(self):
        return ((self.start_loc[0] - self.dest_loc[0])**2 
                + (self.start_loc[1] - self.dest_loc[1])**2)**0.5
    
    def __init__(self, start_loc, dest_loc, req_time):
        self.start_loc = start_loc
        self.dest_loc = dest_loc
        self.req_time = req_time
        
        self.end_time = self.req_time + self.euclidean_distance() + self.alpha
        
class Tourplan:
    
    def __init__(self):
        depot = Request((0,0), (0,0), 0)
        depot.end_time = 1000000 # M, oder Begrenzung
        self.tourenplan = [(depot, 0), (depot, 1)] # 0: origin, 1: destination
        
    def euclidean_distance(loc1, loc2):
        return ((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)**0.5
    
    def insert_costs(self, request, i, j):
        if j - i == 1:
            cost = self.euclidean_distance(self.tourenplan[i-1], request.start_loc)
            + self.euclidean_distance(request.start_loc, request.dest_loc)
            - self.euclidean_distance(self.tourenplan[i-1], [i])
            # hier weitermachen cost+=
    
    def insert_feasible(self, request, i, j):
        return True # Zeitfenster implementieren
    
    def insert(self, request, i, j):
        pass

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
    
