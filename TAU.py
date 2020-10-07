import math
import queue
import numpy as np
import constant


class TAU(object):
    def __init__(self, agent_list, server_list):
        self.agent_list = agent_list
        self.server_list = server_list
        self.min_server_utilization = 1
        self.q = queue.PriorityQueue()
        self.allocate_lst = []
        for agent in agent_list:
            for task in agent.tasks:
                self.q.put(task)

    def init_agent_list(self, probility_list):
        for idx, agent in enumerate(self.agent_list):
            if len(probility_list):
                agent.init_agent(probility_list[idx])
            else:
                agent.init_agent()

    def init_server_list(self):
        for server in self.server_list:
            server.init_server()

    def init_tau(self, probility_list=[]):
        self.init_agent_list(probility_list)
        self.init_server_list()
        self.allocate_lst = []
        self.q = queue.PriorityQueue()
        for agent in self.agent_list:
            for task in agent.tasks:
                self.q.put(task)

    def bra(self):
        while not self.q.empty():
            allocate_server = -1
            task = self.q.get()
            probability = self.agent_list[task.agent_id].probability
            p = np.random.random()
            for idx, val in enumerate(probability):
                p = p - val
                if p < 0:
                    allocate_server = idx
                    break
            self.server_list[allocate_server].add_task(task)
            self.allocate_lst.append(allocate_server)
        return self.get_cost()

    def firstfit(self):
        self.server_list = self.server_list[-3:-2] + self.server_list[:-3] + self.server_list[-2:]
        while not self.q.empty():
            task = self.q.get()
            allocate_server = self.get_first_suitable_server(task)

            self.server_list[allocate_server].add_task(task)
            self.allocate_lst.append(allocate_server)
        return self.get_cost()

    def bestfit(self):
        while not self.q.empty():
            task = self.q.get()
            allocate_server = self.get_best_suitable_server(task)

            self.server_list[allocate_server].add_task(task)
            self.allocate_lst.append(allocate_server)
        return self.get_cost()

    def leastfull(self):
        while not self.q.empty():
            task = self.q.get()
            allocate_server, utilization = self.get_min_server_utilization(task)

            self.server_list[allocate_server].add_task(task)
            self.allocate_lst.append(allocate_server)
        return self.get_cost()

    def shortestwait(self):
        while not self.q.empty():
            allocate_server = -1
            task = self.q.get()
            min_server_lt = 1e10
            for idx, server in enumerate(self.server_list):
                if len(server.que):
                    if min_server_lt > server.que[-1][0]:
                        min_server_lt = server.que[-1][0]
                        allocate_server = idx
                else:
                    allocate_server = idx
                    break

            self.server_list[allocate_server].add_task(task)
            self.allocate_lst.append(allocate_server)
        return self.get_cost()

    def get_cost(self):
        compute = 0
        trans = 0
        for i in range(len(self.server_list)):
            self.server_list[i].get_energy_consumption_by_time()
            compute += self.server_list[i].get_compute_cost()
            print(self.server_list[i].get_compute_cost())
        trans = self.get_trans_cost()
        print(compute, trans)
        return compute + trans

    def get_trans_cost(self):
        lastest_time = -1
        for server in self.server_list:
            if len(server.que) and server.que[-1][-1].trans_lt > lastest_time:
                lastest_time = server.que[-1][-1].trans_lt
        return constant.trans_sigma * lastest_time

    def get_min_server_utilization(self, task):
        idx = -1
        min_utilization = 1
        for i in range(len(self.server_list)):
            tmp_utilization = self.server_list[i].get_utilization_between_a_b(max(task.at-1, 0), task.at)
            if tmp_utilization < min_utilization:
                min_utilization = tmp_utilization
                idx = i
        return idx, min_utilization

    def get_allocation_lst(self):
        return self.allocate_lst

    def get_first_suitable_server(self, task):
        for i, server in enumerate(self.server_list):
            if server.is_suitable_for_task(task, False):
                return i
        for i, server in enumerate(self.server_list):
            if server.is_suitable_for_task(task, True):
                return i
        return -1

    def get_best_suitable_server(self, task):
        idx = -1
        max_utilization = -1
        for server in self.server_list:
            utilization = server.get_utilization_between_a_b(max(task.at-1, 0), task.at) + task.size / server.total_process
            if max_utilization < utilization < constant.utilization_threshold:
                t, _ = server.get_earliest_finish_time_and_core()
                trans_wait = max(server.last_trans_lt, task.at) - task.at
                trans_time = trans_wait + task.size / server.bw
                trans_lt = task.at + trans_time
                compute_wait = max(t, trans_lt) - trans_lt
                compute_time = compute_wait + task.size / server.mu
                if trans_time + compute_time < constant.qos:
                    max_utilization = utilization
                    idx = server.id
        if idx < 0:
            for server in self.server_list:
                utilization=server.get_utilization_between_a_b(max(task.at-1, 0), task.at) + task.size / server.total_process
                if max_utilization < utilization < constant.utilization_threshold:
                    max_utilization = utilization
                    idx = server.id
        return idx
