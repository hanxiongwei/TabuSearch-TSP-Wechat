# -*- coding: utf-8 -*-
"""
@author: hxw
description：
  based on TSP model,
  compare the local search and tabu search
  output the result
"""
from basic_class import Instance
import random
import copy
import time
import cPickle as pickle
import csv
from matplotlib import pyplot as plt

#%%
def solve(inst):
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
        
    def local_solve(ini_route, iteration):
        #%%        
        best = float('inf')
        best_route = list()
        local = 0.0
        
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
        #%%
        iteration_values = list()
        for k in range(iteration):
            #%%
            sorted_neighbors = sorted(neighbors.items(), key = lambda item : item[1])
            nid_i = nid_j = 0
            flag = 0
            for neighbor in sorted_neighbors:
                nids = neighbor[0].split(',')
                nid_i = int(nids[0])
                nid_j = int(nids[1])
                delta = neighbor[1]
                if(delta < 0):
                    flag = 1
                    local += delta
                    break
            #%%
            if(flag == 0):
                #随机选择一个领域，进行移动
                sdict_index = random.randint(0, len(sorted_neighbors) - 1)
                nids = sorted_neighbors[sdict_index][0].split(',')
                nid_i = int(nids[0])
                nid_j = int(nids[1])
                delta = sorted_neighbors[sdict_index][1]
                local += delta
            
            #%%
            # update the route, by swaping the node nid_i and node nid_j
            index_i = route.index(nid_i)
            index_j = route.index(nid_j)
            route.pop(index_i)
            route.insert(index_i, nid_j)
            route.pop(index_j)
            route.insert(index_j, nid_i)
            #%%
            if(local < best):
                best = local
                best_route = copy.copy(route)
            #%%
            # update the neighbors
            for i in range(n):
                for j in range(i + 1, n):
                    neighbors[str(i) + ',' + str(j)] = cal_neighbor(i, j, route)        
            #output_route('iteration : ' + str(k), route, local)
            iteration_values.append(best)
            
            #%%
        result = dict()
        result['tour'] = str(best_route)
        result['cost'] = best
        result['iteration_values'] = iteration_values
        return result
    
    #%%
    def tabu_solve(ini_route, iteration):
        tabu_list = [([0] * n) for i in range(n)]
        tabu_length = int(len(ini_route) * 0.3)
        
        best = float('inf')
        best_route = list()
        local = 0.0
    
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
        iteration_values = list()
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
            
            iteration_values.append(best)
    
        result = dict()
        result['tour'] = best_route
        result['cost'] = best
        result['iteration_values'] = iteration_values
        return result          
    
    #%%    
    n = inst.n
    iteration = n * 5 #迭代次数
    points = inst.points
    dist = inst.dist
    edge = [([0] * n) for i in range(n)] #此赋值避免list的浅复制
    for j in range(n):
        for i in range(n):
            if(i > j):
                edge[i][j] = dist.get((i,j))
            elif(i < j):
                edge[i][j] = edge[j][i]
    ini_route = initial_route()
    #%%
    result = dict()
    result['local_search'] = local_solve(ini_route, iteration)
    result['tabu_search'] = tabu_solve(ini_route, iteration)
    return result
    
#%%
def output_time(info, start, end):
    print(info, round(end - start, 2), 's')

#%%
def single():
    inst = Instance(100, 1)
    random.seed(inst.seed_value)

    start_time = time.clock()
    result = solve(inst)
    end_time = time.clock()
    output_time('tabu search solver : ', start_time, end_time)
    print(result)

#%%
def multy():
    #node_count_list = [10, 20, 50, 100, 200]
    node_count_list = [20]
    experiment_count = 5
    result = dict()
    for node_count in node_count_list:
        for i in range(experiment_count):
            print('node_count:' + str(node_count) + ', experiment_count:' + str(i))
            seed_value = random.randint(1, 100000)
            #seed_value = 1
            inst = Instance(node_count, seed_value)
            random.seed(inst.seed_value)
            result[str(node_count) + ',' + str(i)] = solve(inst)
    #print(result)
    
    #存储结果
    f = file('result/experiment_1.pkl', 'wb')
    pickle.dump(result, f, True)
    f.close()
    
    #%%
    f = file('result/experiment_1.pkl', 'rb')  
    result = pickle.load(f)
    f.close()
    #%%
    #处理数据，输出为csv文件
    epsilon = 0.000001
    table = [['node_count'], ['local_search'], ['tabu_search'], ['avg_gap']]
    for node_count in node_count_list:
        table[0].append(node_count)
        ls_win = ts_win =0
        avg_gap = 0.0
        for i in range(experiment_count):
            temp_result = result[str(node_count) + ',' + str(i)]
            ls_obj = temp_result['local_search']['cost']
            ts_obj = temp_result['tabu_search']['cost']
            avg_gap += (ls_obj - ts_obj) / ls_obj
            if(ls_obj > ts_obj + epsilon):
                ts_win += 1
            elif(epsilon + ls_obj < ts_obj):
                ls_win += 1
            else:
                ts_win += 1
                ls_win += 1
            print(ls_obj, ts_obj, ls_win, ts_win)
        table[1].append(ls_win)
        table[2].append(ts_win)
        table[3].append(round(avg_gap / experiment_count, 3))
    print(table)
    #%%
    f = open('result/experiment_1.csv', 'wb')
    writer = csv.writer(f)
    for line in table:
        writer.writerow(line)
    f.close()

#%%
def analysis():
    #%%
    f = file('result/experiment_1.pkl', 'rb')  
    result = pickle.load(f)
    f.close()
    
    node_count = 200
    x = range(node_count * 5)
    values = result[str(node_count) + ',0']['local_search']['iteration_values']
    plt.plot(x, values)
    values = result[str(node_count) + ',0']['tabu_search']['iteration_values']
    plt.plot(x, values)
    
    plt.xlabel('iteration count')
    plt.ylabel('search best value')
    
#%%
def main():
    #single()
    multy()
    #analysis()

if(__name__ == '__main__'):
    main()
    print('finished')
