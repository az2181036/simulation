import math
import bisect
import constant


class Server(object):
    def __init__(self, id, c, mu, bw, idle_power, busy_power, utilization_threshold):
        self.id = id
        self.bw = bw
        self.c = int(c)
        self.mu = float(mu)
        self.idle_power = float(idle_power)
        self.busy_power = float(busy_power)
        self.total_process = self.c * self.mu
        self.utilization_threshold = utilization_threshold

        self.que = []
        self.last_trans_lt = 0
        self.core_que = [[] for i in range(self.c)]
        self.finish_time = 0
        self.energy_consumption = 0
        self.trans_cost = 0
        self.max_utilization = -1

    def init_server(self):
        self.finish_time = 0
        self.last_trans_lt = 0
        self.energy_consumption = 0
        self.trans_cost = 0

        self.que = []
        self.core_que = [[] for i in range(self.c)]

    def get_utilization_between_a_b(self, a, b):
        if a == b:
            b = a + 1
        cnt = 0
        for core in self.core_que:
            for task in core:
                if task.proc_st >= b:
                    break
                elif task.proc_st >= a:
                    cnt += (min(b, task.get_proc_lt()) - task.proc_st) * self.mu
                elif a < task.get_proc_lt() <= b:
                    cnt += (task.get_proc_lt() - max(a, task.proc_st)) * self.mu

        return cnt / (self.c * self.mu * (b - a))

    def compute_energy_consumption_between_a_b(self, a, b, utilization):
        return (utilization * (self.busy_power - self.idle_power) + self.idle_power) * (b - a)

    def compute_trans_consumption(self, task):
        task.set_trans_st(max(self.last_trans_lt, task.at))
        task.set_trans_lt(task.trans_st + task.size / self.bw)
        task.update_trans_cost()
        self.last_trans_lt = task.trans_lt

    def add_task(self, task):
        task.server_id = self.id
        self.compute_trans_consumption(task)
        tpt = task.size / self.mu  # task process time

        # set task leave time and put task in the queue of core
        earliest_finish_time, core_idx = self.get_earliest_finish_time_and_core()
        task.proc_st = max(task.proc_at, earliest_finish_time)
        task.set_proc_lt(tpt + task.proc_st)
        self.core_que[core_idx].append(task)
        self.finish_time = max(self.finish_time, task.get_proc_lt())

        # add element to the queue of server
        # sort by task.proc_lt
        tmp = [task.get_proc_lt(), task.proc_at, task.size, task]
        bisect.insort(self.que, tmp)

    def get_earliest_finish_time_and_core(self):
        core_idx = -1
        earliest_finish_time = 1e10
        for i in range(self.c):
            if len(self.core_que[i]):
                if self.core_que[i][-1].get_proc_lt() < earliest_finish_time:
                    earliest_finish_time = self.core_que[i][-1].get_proc_lt()
                    core_idx = i
            else:
                earliest_finish_time = 0
                core_idx = i
        return earliest_finish_time, core_idx

    def jg_idle_core(self, t):
        cnt = 0
        for lt, at, size, task in self.que:
            if at <= t < lt:
                cnt += 1
        if cnt >= self.c:
            return False
        else:
            return True

    def get_energy_consumption_by_time(self):
        i = 0
        gap = 1
        while i < self.finish_time - gap:
            utilization = self.get_utilization_between_a_b(i, i+gap)
            self.energy_consumption += self.compute_energy_consumption_between_a_b(i, i+gap, utilization)
            i += 1
        utilization = self.get_utilization_between_a_b(i, self.finish_time)
        self.energy_consumption += self.compute_energy_consumption_between_a_b(i, self.finish_time, utilization)

    def get_compute_cost(self):
        return self.energy_consumption * constant.energy_unit_price

    def get_trans_cost(self):
        self.trans_cost = self.last_trans_lt * constant.trans_sigma
        return self.trans_cost

    def get_total_cost(self):
        return self.trans_cost + self.get_compute_cost()

    def is_suitable_for_task(self, task, flag):
        b = task.at
        a = max(0, task.at-1)
        utilizaiton = self.get_utilization_between_a_b(a, b)
        if task.size / self.total_process < self.utilization_threshold - utilizaiton:
            if flag:
                return True
            else:
                t, _ = self.get_earliest_finish_time_and_core()
                trans_wait = max(self.last_trans_lt, task.at) - task.at
                trans_time = trans_wait + task.size / self.bw
                trans_lt = task.at + trans_time
                compute_wait = max(t, trans_lt) - trans_lt
                compute_time = compute_wait + task.size / self.mu
                if compute_time + trans_time < constant.qos:
                    return True
                return False
        return False