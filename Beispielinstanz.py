# -*- coding: utf-8 -*-

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

requests = [Request((-3, -3), (0, 0), 0),
            Request((0, 1), (5, 5), 3),
            Request((2, 2), (8, 1), 6),
            Request((7, 6), (0, 0), 9)]



for r in requests:
    print(r.req_time, r.end_time)