'''
Created on Sep 24, 2017

@author: mstf
'''

import os
import sys
import json
import random
import datetime

class Graph(object):

    _root = -1
    _num_of_e = -1
    _num_of_v = -1
    _num_of_c =  0
    _graph_matrix = None
    
    def _check_connectivity_constraint(self):
        if self._num_of_e < (self._num_of_v - 1):
            return False
        return True
    
    def _check_complete_graph_constraint(self):
        if self._num_of_e > (self._num_of_v * (self._num_of_v - 1) / 2):
            return False
        return True
    
    def _generate_random_with_exclusion(self, ceil, floor, ex):
        while True:
            n_i = random.randint(ceil, floor)
            if n_i != ex:
                return n_i
    
    def _has_edge(self, v):
        for i in range(self._num_of_v):
            if -1 != self._graph_matrix[v][i]:
                return True
        return False
        
    def _insert_edges(self):
        remaining_edges = self._num_of_e
        for i in range(self._num_of_v):
            if not self._has_edge(i):
                remaining_edges -= 1
                n_i = self._generate_random_with_exclusion(0, self._num_of_v - 1, i)
                self._graph_matrix[i][n_i] = 0
                self._graph_matrix[n_i][i] = 0
        
        while remaining_edges > 0:
            r1_i = random.randint(0, self._num_of_v - 1)
            r2_i = self._generate_random_with_exclusion(0, self._num_of_v - 1, r1_i)
            if -1 == self._graph_matrix[r1_i][r2_i]:
                self._graph_matrix[r1_i][r2_i] = 0
                self._graph_matrix[r2_i][r1_i] = 0
                remaining_edges -= 1

    def __str__(self):
        r_val = "{\n"
        r_val += "\t\"graph\" : {"                             + "\n"
        r_val += "\t\t\"root\"      : " + str(self._root)     + ",\n"
        r_val += "\t\t\"num_of_v\" : " + str(self._num_of_v) + ",\n"
        r_val += "\t\t\"num_of_e\" : " + str(self._num_of_e) + ",\n"
        r_val += "\t\t\"num_of_c\" : " + str(self._num_of_c) + ",\n"
        r_val += "\t\t\"matrix\"    :"                        + "\n"
        
        r_val += "\t\t\t["
        for i in range(self._num_of_v):
            if i > 0:
                r_val += "\t\t\t "
            r_val += "["
            for j in range(self._num_of_v):
                r_val += '{0:3d}'.format(self._graph_matrix[i][j])
                if j < (self._num_of_v - 1):
                    r_val += ", "
            r_val += "]"
            if i < (self._num_of_v - 1):
                r_val += ",\n"
        r_val += "]\n"
        r_val += "\t}\n"
        r_val += "}\n"
        return r_val
    
    def __repr__(self):
        return self.__str__()

    def __init__(self):
        self._graph_matrix = []
    
    def set_vertex(self, v):
        self._num_of_v = v
    
    def get_num_of_vertex(self):
        return self._num_of_v
    
    def set_edge(self, e):
        self._num_of_e = e
        
    def get_num_of_edge(self):
        return self._num_of_e
    
    def set_colour(self, c):
        self._num_of_c = c
    
    def get_num_of_colour(self):
        return self._num_of_c
    
    def set_root(self, r):
        self._root = r
    
    def get_root(self):
        return self._root
    
    def reconstruct_graph_from_json(self, json_file):
        with open(json_file) as data_file:
            data = json.load(data_file)
        
        self._root = data["graph"]["root"]
        self._num_of_v = data["graph"]["num_of_v"]
        self._num_of_e = data["graph"]["num_of_e"]
        self._num_of_c = data["graph"]["num_of_c"]
        self._graph_matrix = data["graph"]["matrix"]
        
    def construct_graph(self):
        if self._check_complete_graph_constraint() and self._check_connectivity_constraint():
            for i in range(self._num_of_v):
                self._graph_matrix.append([])
                for j in range(self._num_of_v):
                    self._graph_matrix[i].append(-1)
            self._insert_edges()

    def clear_colour(self):
        for i in range(self._num_of_v):
            for j in range(self._num_of_v):
                if -1 != self._graph_matrix[i][j]:
                    self._graph_matrix[i][j] = 0
    
    def assign_colours(self):
        for i in range(self._num_of_v):
            for j in range(self._num_of_v):
                if 0 == self._graph_matrix[i][j]:
                    r_c = random.randint(1, self._num_of_c)
                    self._graph_matrix[i][j] = r_c
                    self._graph_matrix[j][i] = r_c

    def get_colour(self, v1, v2):
        return self._graph_matrix[v1][v2]
        
    def get_neighbors(self, v):
        n_list = []
        for i in range(self._num_of_v):
            if -1 != self._graph_matrix[v][i]:
                n_list.append(i)
        return n_list
       
    def dump_into_file(self, fbase, tag):
        fbase += "grap_v_" + str(self._num_of_v) + "_e_" + str(self._num_of_e) + "_c_" + str(self._num_of_c) + "_r_" + str(self._root) + "_"
        fbase += str(datetime.datetime.now()).replace("-", "_").replace(" ", "_").replace(":", "_").replace(".", "_")
        fbase += tag + ".json"
        gfile = open(fbase, "w")
        gfile.write(self.__str__())
        gfile.close()
                

class CoMinSolver(object):
    
    _graph = None
    _random = False
    _total_cost = 0
    _seen_vertexes = []
    _incoming_edge_colour = []
    
    
    def __init__(self, fname, rnd = False):
        self._random = rnd
        self._graph = Graph()
        self._graph.reconstruct_graph_from_json(fname)
        
        for i in range(self._graph.get_num_of_vertex()):
            self._incoming_edge_colour.append(-1)
            self._seen_vertexes.append(0)
    
    def _get_not_seen_neighbors(self, v):
        not_seen_nbors = []
        nbors = self._graph.get_neighbors(v)
        for i in nbors:
            if 0 == self._seen_vertexes[i]:
                not_seen_nbors.append(i)
        return not_seen_nbors
    
    def _calc_cost(self, v1, v2):
        if 0 == self._seen_vertexes[v1]:
            return 0
        if -1 == self._incoming_edge_colour[v1]:
            return 0
        else:
            return abs(self._incoming_edge_colour[v1] - self._graph.get_colour(v1, v2)) 
    
    def _get_vertex_cost_pairs(self, v):
        vc_pair = []
        not_seen_n = self._get_not_seen_neighbors(v)
        for i in not_seen_n:
            c = self._calc_cost(v, i)
            vc_pair.append({"v" : i, "c": c})
        return vc_pair
    
    def _get_min_cost_out_of_cost_pairs(self, pairs):
        if 0 == len(pairs):
            return {"v" : -1, "c": 0}

        min_cost = pairs[0]["c"]
        min_cost_p = pairs[0]
        for p in pairs:
            if p["c"] < min_cost:
                min_cost_p = p
        return min_cost_p
    
    def _is_all_seen(self):
        for i in range(self._graph.get_num_of_vertex()):
            if 0 == self._seen_vertexes[i]:
                return False
        return True

    def solve(self):
        self._seen_vertexes[self._graph.get_root()] = 1
        self._incoming_edge_colour[self._graph.get_root()] = -1
        
        while not self._is_all_seen():

            #print self._seen_vertexes
            #print self._incoming_edge_colour
            
            curr_min_cost = -1
            curr_min_cost_vertex = -1
            curr_min_cost_pair = None
            candidates_for_random = []

            for s in range(len(self._seen_vertexes)):
                if 1 == self._seen_vertexes[s]:
                    if self._random == False:
                        min_cp = self._get_min_cost_out_of_cost_pairs(self._get_vertex_cost_pairs(s))
                        if -1 != min_cp["v"]:
                            if -1 == curr_min_cost:
                                curr_min_cost = min_cp["c"]
                                curr_min_cost_vertex = s
                                curr_min_cost_pair = min_cp
                            else:
                                if min_cp["c"] < curr_min_cost:
                                    curr_min_cost_vertex = s
                                    curr_min_cost_pair = min_cp
                    else:
                        vc_pairs = self._get_vertex_cost_pairs(s)
                        for pair in vc_pairs:
                            candidates_for_random.append({"v": s, "p": pair})

            if self._random == True:
                idx = random.randint(0, len(candidates_for_random) - 1)
                curr_min_cost = candidates_for_random[idx]["p"]["c"]
                curr_min_cost_vertex = candidates_for_random[idx]["v"]
                curr_min_cost_pair = candidates_for_random[idx]["p"]

            self._total_cost += curr_min_cost_pair["c"]
            self._seen_vertexes[curr_min_cost_pair["v"]] = 1
            self._incoming_edge_colour[curr_min_cost_pair["v"]] = self._graph.get_colour(curr_min_cost_vertex, curr_min_cost_pair["v"])

        #print self._seen_vertexes
        #print self._incoming_edge_colour
    
    def get_total_cost(self):
        return self._total_cost

    def get_number_of_vertex(self):
        return self._graph.get_num_of_vertex()

    def get_number_of_edge(self):
        return self._graph.get_num_of_edge()

    def get_number_of_colour(self):
        return self._graph.get_num_of_colour()

    def get_root_vertex(self):
        return self._graph.get_root()

if __name__ == '__main__':

    '''
    for g in range(1, 101):
        graph = Graph()    
        graph.set_vertex(50)
        graph.set_edge(700)
        graph.set_root(random.randint(0, 49))
        graph.construct_graph()
        for c in range (10, 101):
            graph.clear_colour()
            graph.set_colour(c)
            graph.assign_colours()
            graph.dump_into_file("./changes_on_colour/", "_" + str(g) + "_")
    '''

    '''
    g = Graph()
    g.set_vertex(5)
    g.set_edge(6)
    g.set_root(1)
    g.construct_graph()
    g.set_colour(10)
    g.assign_colours()
    g.dump_into_file("./", "")
    print g
    '''

    '''
    g = Graph()
    g.reconstruct_graph_from_json("grap_v_10_e_20_c_20_r_9_2017_09_24_14_32_26_907880.json")
    print g
    '''

    '''
    solver = CoMinSolver("grap_v_5_e_6_c_10_r_1_2017_09_25_17_44_03_335158.json", True)
    solver.solve()
    '''

    root_folder = "./changes_on_colour/"
    solution_array = []

    files = os.listdir(root_folder)

    for f in files:
        print root_folder + f
        solver = CoMinSolver(root_folder + f)
        solver.solve()
        solution_array.append({"v" : solver.get_number_of_vertex(),
                               "e" : solver.get_number_of_edge(),
                               "c" : solver.get_number_of_colour(),
                               "r" : solver.get_root_vertex(),
                               "t" : solver.get_total_cost()})
    
    print solution_array

