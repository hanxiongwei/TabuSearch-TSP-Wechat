# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 09:52:19 2017

@author: hxw
"""
import itertools
from gurobipy import *
from basic_class import Instance

def gurobi_solve(inst):
    # Callback - use lazy constraints to eliminate sub-tours
    def subtourelim(model, where):
        # when finding a new MIP incumbent
        if where == GRB.Callback.MIPSOL:
            # make a list of edges selected in the solution
            vals = model.cbGetSolution(model._vars)
            selected = tuplelist((i,j) for i,j in model._vars.keys() if vals[i,j] > 0.5)
            # find the shortest cycle in the selected edge list
            tour = subtour(selected)
            if len(tour) < n:
                # add subtour elimination constraint for every pair of cities in tour
                # combinations(list_name, 2)   # 从list_name中挑选两个元素，将所有结果升序排序，返回为新的循环器。
                model.cbLazy(quicksum(model._vars[i,j]
                                      for i,j in itertools.combinations(tour, 2))
                             <= len(tour)-1)

    # Given a tuplelist of edges, find the shortest subtour
    def subtour(edges):
        unvisited = list(range(n))
        cycle = range(n+1) # initial length has 1 more city
        while unvisited: # true if list is non-empty
            thiscycle = []
            neighbors = unvisited
            while neighbors:
                current = neighbors[0]
                thiscycle.append(current)
                unvisited.remove(current)
                neighbors = [j for i,j in edges.select(current,'*') if j in unvisited]
            if len(cycle) > len(thiscycle):
                cycle = thiscycle
        return cycle
    
    n = inst.n
    points = inst.points
    dist = inst.dist

    setParam('OutputFlag', 0)    
        
    m = Model()
    
    vars = m.addVars(dist.keys(), obj=dist, vtype=GRB.BINARY, name='e')
    for i,j in vars.keys():
        vars[j,i] = vars[i,j] # edge in opposite direction
    m.addConstrs(vars.sum(i,'*') == 2 for i in range(n))
    m._vars = vars
    m.Params.lazyConstraints = 1
    m.optimize(subtourelim)
    
    vals = m.getAttr('x', vars)
    selected = tuplelist((i,j) for i,j in vals.keys() if vals[i,j] > 0.5)
    
    tour = subtour(selected)
    assert len(tour) == n
    
    '''      
    print('')
    print('----------gurobi solution----------')
    print('is optimal : ', m.status == GRB.OPTIMAL)
    print('Optimal tour : %s' % str(tour))
    print('Optimal cost : %g' % m.objVal)
    print('')
    '''
              
    result = dict()
    result['isOptimal'] = m.status == GRB.OPTIMAL
    result['tour'] = str(tour)
    result['cost'] = m.objVal
    return result 

def main():
    inst = Instance(200, 1)
    gurobi_solve(inst)
    
if(__name__ == '__main__'):
    main()
    print('finished')



    


