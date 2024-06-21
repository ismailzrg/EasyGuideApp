# aco_algorithme.py

import math
import random
import time as tm
from tqdm import tqdm
from matplotlib import pyplot as plt
import folium
import sqlite3
from time import strptime
from datetime import datetime, timedelta
from geopy.distance import geodesic
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy_garden.mapview import MapView, MapMarker, MapMarkerPopup, MapSource


class EasyGuideACO:

    class Edge:
        def __init__(self, a, b, travel_time_, initial_pheromone, alpha):
            self.a = a
            self.b = b
            if travel_time_ == timedelta(hours=0, minutes=0, seconds=0):
                travel_time_ = timedelta(microseconds=1)
            self.travel_time = travel_time_
            self.pheromone = initial_pheromone
            self.alpha = alpha

    class Ant:
        def __init__(self, beta, num_nodes, edges, opening_duration):
            self.beta = beta
            self.num_nodes = num_nodes
            self.edges = edges
            self.opening_duration = opening_duration
            self.tour = []
            self.total_time = timedelta(hours=0, minutes=0, seconds=0)
            self.arrival_times = []

        def _select_node(self, current_time, duration_time):
            roulette_wheel = 0.0
            print("tour in select node is: ",len(self.tour),"\n",self.tour)
            unvisited_nodes = [node for node in range(self.num_nodes) if node not in self.tour] #----- les nodes aui ne sont pas visité
            heuristic_total = timedelta(hours=0, minutes=0, seconds=0)
            print("unvisited nodes are: ",len(unvisited_nodes),"\n",unvisited_nodes)
            for unvisited_node in unvisited_nodes:
                edge = self.edges[self.tour[-1]][unvisited_node]  # ----- le node selectionnée par tour et work with it avec les autres unvisited nodes
                travel_time = edge.travel_time  # ----- la durrée entre aux
                arrival_time = current_time + travel_time  # ----- arrivale time current time real et en ajouter la durrée de deplacement
                print("node open under unvisited node loop: ", self._is_node_open(unvisited_node, arrival_time))
                print("travel time is: ", travel_time, " duration time is: ", duration_time)
                if self._is_node_open(unvisited_node, arrival_time) and travel_time <= duration_time:
                    heuristic_total += travel_time
                    print("******************************* heuristic: ", heuristic_total," | travel time: ", travel_time)
            if heuristic_total == timedelta(hours=0, minutes=0, seconds=0):
                print("///////////// none...")
                return None  # No available nodes
            for unvisited_node in unvisited_nodes:
                edge = self.edges[self.tour[-1]][unvisited_node]
                travel_time = edge.travel_time
                arrival_time = current_time + travel_time
                if self._is_node_open(unvisited_node, arrival_time) and travel_time <= duration_time:
                    roulette_wheel += pow(edge.pheromone, edge.alpha) * pow((heuristic_total.total_seconds() / travel_time.total_seconds()), self.beta)
            random_value = random.uniform(0.0, roulette_wheel)
            wheel_position = 0.0
            for unvisited_node in unvisited_nodes:
                edge = self.edges[self.tour[-1]][unvisited_node]
                travel_time = edge.travel_time
                arrival_time = current_time + travel_time
                if self._is_node_open(unvisited_node, arrival_time) and travel_time <= duration_time:
                    wheel_position += pow(edge.pheromone, edge.alpha) * pow((heuristic_total.total_seconds() / travel_time.total_seconds()), self.beta)
                    if wheel_position >= random_value:
                        print("i return the unvisited node: ",unvisited_node)
                        return unvisited_node

        def _is_node_open(self, node, arrival_time):
            opening_time, closing_time = self.opening_duration[node]
            open_time_ = datetime.strptime(opening_time, "%H:%M:%S")
            hours = open_time_.hour
            minutes = open_time_.minute
            seconds = open_time_.second
            open_time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            close_time_ = datetime.strptime(closing_time, "%H:%M:%S")
            hours = close_time_.hour
            minutes = close_time_.minute
            seconds = close_time_.second
            close_time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            if open_time == timedelta(hours=0) and close_time == timedelta(hours=12): #----- j'ajouter cette condition pca les pharms/docts ouvrée 24h yediw value false
                return True                                                           #----- c pour ça ajouter cette condition
            else:
                return open_time <= arrival_time <= close_time #----- return true si open sinon false

        def find_tour(self, current_time, duration):
            end_work = current_time + duration  # ----- pour respect la durrée de voyage de déligué
            bool_randon = False
            while bool_randon == False:
                temp_num = random.randint(0,self.num_nodes - 1)
                if self._is_node_open(temp_num, current_time):
                    bool_randon = True
                else:
                    print("/////////////////////////////// false")
            self.tour = [temp_num]
            #self.tour = [random.randint(0,self.num_nodes - 1)]  # ----- select randon node pour commance a partir il la simulation
            self.arrival_times = [timedelta(hours=0, minutes=0, seconds=0)]  # Starting at time 0
            current_time_ = current_time  # ----- time real
            self.total_time = timedelta(hours=0, minutes=0, seconds=0)
            consultation_duration = timedelta(hours=0, minutes=15,seconds=0)  # ----- je donnée 15minutes pour la consultation de deligué avec pharm/doct
            duration_time = duration
            while len(self.tour) < self.num_nodes:
                if current_time_ + consultation_duration <= end_work:
                    next_node = self._select_node(current_time_, duration_time)
                    if next_node is None:
                        break
                    last_node = self.tour[-1]
                    travel_time_ = self.edges[last_node][next_node].travel_time
                    if current_time_ + travel_time_ + consultation_duration <= end_work:
                        self.tour.append(next_node)
                        current_time_ += travel_time_ + consultation_duration
                        duration_time -= travel_time_ + consultation_duration
                        self.arrival_times.append(current_time_)
                    else:
                        break
                else:
                    break

            for i in range(len(self.tour)):
                total_travel_time = self.edges[self.tour[i]][self.tour[(i + 1) % len(self.tour)]].travel_time
                self.total_time += total_travel_time + consultation_duration  # ----- total time retenue par finishing ce tour
            # return self.total_time
            return self.tour, self.total_time

    def __init__(self, colony_size=10, elitist_weight=1.0, min_scaling_factor=0.001, beta=3.0, nodes=None,
                 labels=None, rho=0.1, pheromone_deposit_weight=1.0, initial_pheromone=1.0, steps=10, duration_trailer=None):
        self.colony_size = colony_size
        self.elitist_weight = elitist_weight
        self.min_scaling_factor = min_scaling_factor
        self.rho = rho
        self.pheromone_deposit_weight = pheromone_deposit_weight
        self.steps = steps
        conn = sqlite3.connect('easyguide.db')
        c = conn.cursor()
        c.execute("select count(*) from pharm_doct")
        result = c.fetchone()
        nbr_nodes = result[0] if result else 0
        c.execute("select * from pharm_doct")
        markets = c.fetchall()
        conn.commit()
        conn.close()
        nodes_coor = []
        name_nodes = []
        alpha_nodes = []
        opening_diration = []
        for market in markets:
            name, lat, lon, score, open_time, close_time = market[0], market[3], market[4], market[5], market[6], market[7]
            lat = float(lat)
            lon = float(lon)
            nodes_coor += [(lat, lon)]
            name_nodes += [name]
            alpha_nodes += [score] #----- la score de pharm/doct ==> importance de node next donc importance de edge qui donne la priorité de choisie
            opening_diration += [(open_time, close_time)] #----- la durrée de travaille de pharm/doct

        self.num_nodes = nbr_nodes #----- le nombre total de pharmù/doct saisie dans notre databade
        self.nodes = nodes #----- les coordinations de pharm/doct
        self.labels = name_nodes #----- le nom de pharm/doct
        self.edges = [[None] * self.num_nodes for _ in range(self.num_nodes)]
        for i in range(self.num_nodes):
            for j in range(i + 1, self.num_nodes):
                alpha = alpha_nodes[j]  #----- alpha value for each edge ( importance de edge = importance de pharm/doct destiné)
                travel_time = self.calculate_travel_time(nodes[i], nodes[j])
                hours = int(travel_time)
                minutes = int((travel_time - hours) * 60)
                seconds = int(((travel_time - hours) * 60 - minutes) * 60)
                #travel_time_ = time(hour=hours, minute=minutes, second=seconds)
                travel_time_ = timedelta(hours=hours, minutes=minutes, seconds=seconds) #----- travel time entre node et node
                print(f"travel time between n°{i + 1} {self.labels[i]} et n°{j + 1} {self.labels[j]}: ", "is: ",travel_time_)
                self.edges[i][j] = self.edges[j][i] = self.Edge(i, j, travel_time_, initial_pheromone, alpha)
        self.ants = [self.Ant(beta, self.num_nodes, self.edges, opening_diration) for _ in range(colony_size)]
        self.global_best_tour = [None] #----- return best value de tour a partir time
        self.global_best_total_time = timedelta(0) #----- best time retenue  qui respect la durrée de voyage
        self.duration_trailer = duration_trailer #----- la durrée de voyage (li rana ndiroh avant commance generée
        self.run_time = None

    def calculate_travel_time(self, node1, node2):
        distance = geodesic(node2, node1).kilometers
        if distance <= 2:
            speed_kmh = 12
        elif 2 < distance <= 6:
            speed_kmh = 18
        else:
            speed_kmh = 33
        travel_time = distance / speed_kmh
        return travel_time

    def _add_pheromone(self, tour, travel_time,  weight=1.0):
        if travel_time == timedelta(hours=0, minutes=0,seconds=0):  # ----- cette condition pour evité l'erreur de  devision par zero
            travel_time = timedelta(microseconds=1)
        pheromone_to_add = self.pheromone_deposit_weight / travel_time.total_seconds()
        # for i in range(self.num_nodes):
        for i in range(len(tour)):
            # self.edges[tour[i]][tour[(i + 1) % self.num_nodes]].pheromone += weight * pheromone_to_add
            self.edges[tour[i]][tour[(i + 1) % len(
                tour)]].pheromone += weight * pheromone_to_add  # ----- intialisation de pheromone dans chaqu'un edge

    def run(self):
        current_time_ = datetime.now().time()
        start_of_day = datetime.combine(datetime.now().date(), datetime.min.time())
        start = datetime.combine(datetime.now().date(), current_time_) - start_of_day
        duration = self.duration_trailer
        i = 0
        j = 0
        k = 0
        p = 0
        for step in range(self.steps):
            iteration_best_tour = []
            iteration_best_total_time = timedelta(0)
            current_time_ = datetime.now().time()
            start_of_day = datetime.combine(datetime.now().date(), datetime.min.time())
            current_time = datetime.combine(datetime.now().date(), current_time_) - start_of_day
            for ant in self.ants:
                tour, total_time = ant.find_tour(current_time, duration)
                if len(tour) > len(iteration_best_tour):
                    i += 0
                    iteration_best_tour = tour
                    iteration_best_total_time = total_time
            if float(step + 1) / float(self.steps) <= 0.75:
                k += 1
                self._add_pheromone(iteration_best_tour, iteration_best_total_time)
                # self._add_pheromone(ant.tour, ant.total_time)
                max_pheromone = self.pheromone_deposit_weight / iteration_best_total_time.total_seconds()
            else:
                if len(iteration_best_tour) > len(self.global_best_tour):
                    j += 1
                    self.global_best_tour = iteration_best_tour
                    self.global_best_total_time = iteration_best_total_time
                    self._add_pheromone(self.global_best_tour,self.global_best_total_time)  # ----- initialisé pheromone dans les nodes
                max_pheromone = self.pheromone_deposit_weight / self.global_best_total_time.total_seconds()
            min_pheromone = max_pheromone * self.min_scaling_factor
            for i in range(len(tour)):
                for j in range(i + 1, len(tour)):
                    p += 1
                    self.edges[i][j].pheromone *= (1.0 - self.rho)
                    if self.edges[i][j].pheromone > max_pheromone:
                        self.edges[i][j].pheromone = max_pheromone
                    elif self.edges[i][j].pheromone < min_pheromone:
                        self.edges[i][j].pheromone = min_pheromone
            print("duration is: ", duration)
            print("steps is: ", self.steps, " | step is: ", step)
            print("ant tour is: ", len(ant.tour), " his values: ", ant.tour)
            print("iteration best tour is: ", len(iteration_best_tour), " his values: ", iteration_best_tour)
            print("global best tour is: ", len(self.global_best_tour), " his values: ", self.global_best_tour)
            print("ant total time: ", ant.total_time)
            print("iteration total time: ", iteration_best_total_time)
            print("global best total time: ", self.global_best_total_time)
            print("value of I is: ", i, " | value of J is: ", j, " | value of K is: ", k, " | value of P is: ", p)
            i = 0
            j = 0
            k = 0
            p = 0
        current_time_ = datetime.now().time()
        start_of_day = datetime.combine(datetime.now().date(), datetime.min.time())
        end = datetime.combine(datetime.now().date(), current_time_) - start_of_day
        runtime = end - start
        self.run_time = runtime
        return self.run_time, self.global_best_total_time, self.global_best_tour

    def plot(self, line_width=1, point_radius=math.sqrt(2.0), color='green', x_size=40, y_size=30, dpi=80,save_as="best_tour.png", best_tour_=None):
        fig, ax = plt.subplots(figsize=(x_size, y_size))
        best_tour = best_tour_
        for i in range(len(best_tour)):
            node = best_tour[i]
            next_node = best_tour[(i + 1) % len(best_tour)]
            x = [self.nodes[node][0], self.nodes[next_node][0]]
            y = [self.nodes[node][1], self.nodes[next_node][1]]
            ax.plot(x, y, 'bo-', linewidth=line_width, markersize=point_radius)
            name = f"{i+1} {self.labels[node]}"
            ax.text(self.nodes[node][0], self.nodes[node][1], name, fontsize=12, ha='right')
            ax.text(self.nodes[next_node][0], self.nodes[next_node][1], self.labels[next_node], fontsize=12, ha='right')
        ax.set_title(f"Best tour found by ACO: {self.global_best_total_time} units")
        ax.set_xlabel('Latitude')
        ax.set_ylabel('Longitude')
        plt.savefig(save_as, dpi=dpi)
        plt.close(fig)

    def generate_map(self, nodes, best_tour, labels):

        my_map = folium.Map(location=[sum([node[0] for node in nodes]) / len(nodes),
                                      sum([node[1] for node in nodes]) / len(nodes)], zoom_start=13)
        for i, node in enumerate(nodes):
            folium.Marker(location=[node[0], node[1]], popup=f"{labels[i]}").add_to(my_map)
        for i in range(len(best_tour)):
            node = best_tour[i]
            next_node = best_tour[(i + 1) % len(best_tour)]
            folium.Marker(location=nodes[node], popup=f"{i+1} {labels[int(best_tour[i])]}", icon=folium.Icon(color='green')).add_to(my_map)
            if i == 0:folium.Marker(location=nodes[node], popup=f"{i+1} {labels[int(best_tour[i])]}", icon=folium.Icon(color='red')).add_to(my_map)
            if i == len(best_tour)-1: folium.Marker(location=nodes[node], popup=f"{i+1} {labels[int(best_tour[i])]}", icon=folium.Icon(color='purple')).add_to(my_map)
            folium.PolyLine(locations=[nodes[node], nodes[next_node]], color="red").add_to(my_map)
        return my_map


