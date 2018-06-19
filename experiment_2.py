# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 00:00:10 2017

@author: hxw
description：
  based on TSP model,
  use gurobi and tabu search algorithm to solve it,
  compare them and output the result.
"""
from basic_class import Instance
from tsp_gurobi import gurobi_solve
import random
import copy
import time
import cPickle as pickle
import csv

#%%
def tabu_solve(inst, start_time, gurobi_time, best_obj):
    #%%
    #randomly generate a initial route
    def initial_route():
        route = []
        unvisited = range(n)
        count = n
        while(count != 0):
            index = random.randint(0, count - 1)
            current = unvisited[index]
            route.append(current)
            unvisited.remove(current)
            count -= 1
        return route
    
    def cal_distance(route):
        distance = 0.0
        for i in range(n - 1):
            distance += get_edge(i, i+1, route)
        distance += get_edge(0, n-1, route)
        return distance
    
    def get_edge(index_i, index_j, route):
        if(index_i == n):
            index_i = 0
        if(index_j == n):
            index_j = 0
        return edge[route[index_i]][route[index_j]]
    
    def cal_neighbor(nid_i, nid_j, route):
        #i, j means the node id, and the index_i and index_j means the node's index in route
        index_i = route.index(nid_i)
        index_j = route.index(nid_j)
        delta = 0
        if(index_i == index_j - 1 or index_i == index_j + n - 1):
            delta += get_edge(index_i, index_j + 1, route) + get_edge(index_i - 1, index_j, route)
            delta -= get_edge(index_i - 1, index_i, route) + get_edge(index_j, index_j + 1, route)
        elif(index_i == index_j + 1 or index_j == index_i + n -1):
            delta += get_edge(index_j, index_i + 1, route) + get_edge(index_j - 1, index_i, route)
            delta -= get_edge(index_j - 1, index_j, route) + get_edge(index_i, index_i + 1, route)
        else:
            delta += get_edge(index_j, index_i - 1, route) + get_edge(index_j, index_i + 1, route)
            delta += get_edge(index_i, index_j - 1, route) + get_edge(index_i, index_j + 1, route)
            delta -= get_edge(index_i, index_i - 1, route) + get_edge(index_i, index_i + 1, route)
            delta -= get_edge(index_j, index_j - 1, route) + get_edge(index_j, index_j + 1, route)
        return delta
            
    def output_route(info, route, distance):
        print(info, ', tour:', route, ', distance:', distance)
    
    eplison = 0.000001
    iteration = 10000
    n = inst.n
    tabu_length = int(n * 0.2)
    points = inst.points
    dist = inst.dist
    edge = [([0] * n) for i in range(n)] #此赋值避免list的浅复制
    for j in range(n):
        for i in range(n):
            if(i > j):
                edge[i][j] = dist.get((i,j))
            elif(i < j):
                edge[i][j] = edge[j][i]
    #print(edge)
    
    tabu_list = [([0] * n) for i in range(n)]
    
    best = float('inf')
    best_route = list()
    local = 0.0
    
    ini_route = initial_route()
    local = cal_distance(ini_route)
    best = min(best, local)
    #output_route('initial route', ini_route, local)
    
    #search begins
    route = copy.copy(ini_route)
    best_route = copy.copy(ini_route)
    neighbors = dict()
    for i in range(n):
        for j in range(i + 1, n):
            neighbors[str(i) + ',' + str(j)] = cal_neighbor(i, j, route)
    #print(neighbors)
    
    #%%        
    for k in range(iteration):
        sorted_neighbors = sorted(neighbors.items(), key = lambda item : item[1])
        #print('sort_neighbors', sorted_neighbors)
        nid_i = nid_j = 0
        flag = 0
        for neighbor in sorted_neighbors:
            nids = neighbor[0].split(',')
            nid_i = int(nids[0])
            nid_j = int(nids[1])
            delta = neighbor[1]
            temp_local = local + delta
            # aspiration criterion
            if(temp_local < best):
                local = temp_local
                best = local
                flag = 1
            else:
                if(tabu_list[nid_i][nid_j] != 0):
                    continue
                else:
                    local = temp_local
            break
        # update the route, by swaping the node nid_i and node nid_j
        index_i = route.index(nid_i)
        index_j = route.index(nid_j)
        route.pop(index_i)
        route.insert(index_i, nid_j)
        route.pop(index_j)
        route.insert(index_j, nid_i)
        if(flag == 1):
            best_route = copy.copy(route)
        # update the tabu_list
        for i in range(n):
            for j in range(n - i):
                if(tabu_list[i][j] != 0):
                    tabu_list[i][j] -= 1
        tabu_list[nid_i][nid_j] = tabu_length
        #print(nid_i, nid_j)
        #print(tabu_list)
        # update the neighbors
        for i in range(n):
            for j in range(i + 1, n):
                neighbors[str(i) + ',' + str(j)] = cal_neighbor(i, j, route)
        #output_route('iteration : ' + str(k), route, local)
        end_time = time.clock()
        if(end_time - start_time > gurobi_time + eplison or abs(best_obj - best) < eplison):
            break
    
    result = dict()
    result['tour'] = str(best_route)
    result['cost'] = best
    return result           

#%%
def single():
    inst = Instance(100, 1)
    random.seed(inst.seed_value)
    
    start_time = time.clock()
    gurobi_result = gurobi_solve(inst)
    end_time = time.clock()
    output_time('gurobi solver : ', start_time, end_time)
    print(gurobi_result)
    
    start_time = time.clock()
    tabu_result = tabu_solve(inst)
    end_time = time.clock()
    output_time('tabu search solver : ', start_time, end_time)
    print(tabu_result)

#%%
def multy():
    node_count_list = [10, 20, 50, 100, 200]
    #node_count_list = [50]
    result = dict()
    for node_count in node_count_list:
        seed_value = random.randint(1, 100000)
        inst = Instance(node_count, seed_value)
        random.seed(inst.seed_value)
            
        start_time = time.clock()
        gurobi_result = gurobi_solve(inst)
        end_time = time.clock()
        gurobi_time = end_time - start_time
        gurobi_result['time'] = gurobi_time
                     
        start_time = time.clock()
        tabu_result = tabu_solve(inst, start_time, gurobi_time, gurobi_result['cost'])
        end_time = time.clock()
        tabu_time = end_time - start_time
        tabu_result['time'] = tabu_time
                   
        result['gurobi,' + str(node_count)] = gurobi_result
        result['tabu_search,' + str(node_count)] = tabu_result
    #存储结果
    f = file('result/experiment_3.pkl', 'wb')
    pickle.dump(result, f, True)
    f.close()
    
    #处理数据，输出为csv文件
    table = [['node_count'], ['gurobi_obj'], ['gurobi_time'], ['ts_obj'], ['ts_time'], ['avg_obj_gap']]
    for node_count in node_count_list:
        table[0].append(node_count)
        gurobi_result = result['gurobi,' + str(node_count)]
        tabu_result = result['tabu_search,' + str(node_count)]
        table[1].append(gurobi_result['cost'])
        table[2].append(gurobi_result['time'])
        table[3].append(tabu_result['cost'])
        table[4].append(tabu_result['time'])
        obj_gap = (tabu_result['cost'] - gurobi_result['cost']) / gurobi_result['cost']
        table[5].append(round(obj_gap, 3))
    print(table)
    #%%
    f = open('result/experiment_3.csv', 'wb')
    writer = csv.writer(f)
    for line in table:
        writer.writerow(line)
    f.close()
        
#%%
def main():
    #single()
    multy()

if(__name__ == '__main__'):
    main()
    print('finished')
