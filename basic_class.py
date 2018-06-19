# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 10:22:50 2017

@author: hxw
"""
import math
import random

class Instance:
    def __init__(self, n, seed_value):
        self.n = n # the count of nodes
        self.seed_value = seed_value
        random.seed(self.seed_value)
        self.points = [(random.randint(0, 100), random.randint(0, 100)) \
                for i in range(n)]  # coordinates of nodes
        self.dist = {(i, j) : math.sqrt(sum((self.points[i][k] - self.points[j][k])**2 \
                for k in range(2))) for i in range(n) for j in range(i)} # edges between nodes
    def __str__(self):
        pass