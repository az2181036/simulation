from task import Task

import numpy as np


class Agent(object):
    def __init__(self, id, _lambda, task_num, probability = []):
        """
        :param _lambda: task arrival rate
        :param task_num: tasks number of the simulation
        """
        self.id = id
        self._lambda = _lambda
        self.task_num = task_num
        self.probability = probability
        self.tasks = self.init_tasks_queue()

        self.t = 0
        self.proc_t = 0
        self.trans_t = 0
        self.energy = 0

    def init_tasks_queue(self):
        # set the size of tasks by N(1,1)
        task_size = np.random.normal(1, 1, self.task_num * 2)
        # drop the size if size <= 0 or size >= 2 (keep the expectation is 1)
        task_size = [i for i in task_size if 0 < i < 2]
        task_size = task_size[:self.task_num]

        # init task arrival time
        at = [0 for i in range(self.task_num)]
        gap = np.random.exponential(1/self._lambda, self.task_num)
        for i in range(1, self.task_num):
            at[i] = at[i-1] + gap[i-1]

        # generate the tasks list
        return [Task(self.id, at[i], task_size[i]) for i in range(self.task_num)]

    def init_agent(self, probability=[]):
        for task in self.tasks:
            task.init_info()
        self.probability = probability

        self.t = 0
        self.proc_t = 0
        self.trans_t = 0
        self.energy = 0

    def set_t(self):
        cnt_t = 0
        cnt_proc_t = 0
        cnt_trans_t = 0
        for task in self.tasks:
            proc_t = task.get_proc_lt() - task.proc_at
            trans_t = task.trans_lt - task.at

            cnt_t += task.get_proc_lt() - task.at
            cnt_proc_t += proc_t
            cnt_trans_t += trans_t

        self.t = cnt_t / len(self.tasks)
        self.proc_t = cnt_proc_t / len(self.tasks)
        self.trans_t = cnt_trans_t / len(self.tasks)

    def get_t(self):
        self.set_t()
        return [self.t, self.trans_t, self.proc_t]

    def set_energy(self):
        cnt = 0
        for task in self.tasks:
            cnt += task.proc_consumption + task.trans_cost
        self.energy = cnt / len(self.tasks)

    def get_energy(self):
        self.set_energy()
        return self.energy

    def get_transmission_time(self):
        return self.trans_lt - self.trans_st

    def get_process_time(self):
        return self.__proc_lt - self.at