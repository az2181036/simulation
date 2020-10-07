from functools import total_ordering

import constant


@total_ordering
class Task(object):
    def __init__(self, agent_id, at=0, size=0):
        """
        :param at: task arrival time
        :param size: task size
        """
        self.at = at
        self.size = size
        self.agent_id = agent_id

        self.trans_st = 0
        self.trans_lt = 0
        self.proc_at = 0
        self.proc_st = 0
        self.__proc_lt = 0
        self.server_id = -1
        self.trans_cost = 0
        self.proc_consumption = 0

    def __eq__(self, other):
        return self.at == other.at

    def __lt__(self, other):
        return self.at < other.at

    def __str__(self):
        return str(self.at) + " " + str(self.lt) + " " + str(self.size) + " " + str(self.agent_id)

    def init_info(self):
        self.trans_st = 0
        self.trans_lt = 0
        self.proc_at = 0
        self.proc_st = 0
        self.__proc_lt = 0
        self.server_id = -1
        self.trans_cost = 0
        self.proc_consumption = 0

    def set_trans_st(self, t):
        self.trans_st = t

    def get_proc_lt(self):
        return self.__proc_lt

    def set_proc_lt(self, lt):
        self.__proc_lt = lt

    def set_trans_lt(self, lt):
        self.trans_lt = lt
        self.proc_at = lt

    def add_proc_consumption(self, st, lt, consumption):
        self.proc_consumption += consumption * (lt - st) / (self.__proc_lt - self.proc_at)

    def get_transmission_time(self):
        return self.trans_lt - self.at

    def get_process_time(self):
        return self.__proc_lt - self.at

    def update_trans_cost(self):
        self.trans_cost = constant.trans_sigma * (self.trans_lt - self.at)
        return self.trans_cost