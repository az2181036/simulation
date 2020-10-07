import numpy as np

import constant
from agent import Agent
from server import Server
from TAU import TAU


seed = 111
np.random.seed(seed)
agent_list = [Agent(i, constant._lambda[i], constant.task_num, constant.probability_lst[i]) for i in range(constant.n)]
server_list = [Server(j, constant.server_list[j]['process_num'], constant.server_list[j]['process_rate'],
                      1/constant.tt[j], constant.server_list[j]['idle_power'], constant.server_list[j]['busy_power'],
                      constant.utilization_threshold)
               for j in range(constant.m)]
tau = TAU(agent_list, server_list)


def get_total_energy_consumption(algorithm_name, probility_lst=[]):
    tau.init_tau(probility_lst)
    energy_consumption = (getattr(tau, algorithm_name)())
    print(energy_consumption)

    time_lst = []
    energy_lst = []
    for agent in agent_list:
        time_lst.append(agent.get_t())
        energy_lst.append(agent.get_energy())
    print(get_agent_response_time())
    print(get_qos_violation(constant.qos))
    return energy_consumption


def bra_energy_consumption(probility_list):
    print("bra algorithm energy_consumption")
    return get_total_energy_consumption('bra', probility_list)


def bra_energy_consumption_with_different_seed(probibality_lst):
    energy_consumption_lst = []
    time_lst = []
    avg_energy_lst = []
    qos = []
    for i in range(100):
        np.random.seed(i * 10)
        energy_consumption_lst.append(get_total_energy_consumption('bra', probibality_lst))
        e_tmp = []
        for agent in agent_list:
            e_tmp.append(agent.get_energy())
        time_lst.append(get_agent_response_time())
        avg_energy_lst.append(e_tmp)
        qos.append(get_qos_violation(constant.qos))
    return energy_consumption_lst, time_lst, avg_energy_lst, qos

def init_probability_energy_consumption(probibality_list):
    print("init probility algorithm energy consumption:")
    return get_total_energy_consumption('bra', probibality_list)


def shortest_wait_energy_consumption():
    print("Shortest_wait algorithm energy consumption:")
    return get_total_energy_consumption('shortestwait')


def least_full_energy_consumption():
    print("Least-full algorithm energy consumption:")
    return get_total_energy_consumption('leastfull', [])

def first_fit_energy_consumption():
    print("First-fit algorithm energy consumption:")
    return get_total_energy_consumption('firstfit', [])

def best_fit_energy_consumption():
    print("Best-fit algorithm energy consumption:")
    return get_total_energy_consumption('bestfit', [])


def get_qos_violation(qos):
    cnt = 0
    for agent in agent_list:
        for task in agent.tasks:
            if task.get_process_time() > qos:
                cnt += 1
    return cnt / (constant.n * constant.task_num)


def get_agent_response_time():
    t = []
    for agent in agent_list:
        t.append(agent.get_t())
    return t


if __name__ == "__main__":
    bra_energy_consumption(constant.probability_lst)
    # avg_process_time_lst1, server_avg_process_time1 = get_server_avg_process_time()

    init_probability_energy_consumption(constant.init_probability)
    # avg_process_time_lst2, server_avg_process_time2 = get_server_avg_process_time()

    shortest_wait_energy_consumption()
    # avg_process_time_lst3, server_avg_process_time3 = get_server_avg_process_time()

    least_full_energy_consumption()
    # avg_process_time_lst3, server_avg_process_time3 = get_server_avg_process_time()

    best_fit_energy_consumption()
    # avg_process_time_lst4, server_avg_process_time4 = get_server_avg_process_time()

    first_fit_energy_consumption()
    # avg_process_time_lst5, server_avg_process_time5 = get_server_avg_process_time()

    # y1, t1, e1, q1 = bra_energy_consumption_with_different_seed(constant.probability_lst)
    # y2, t2, e2, q2 = bra_energy_consumption_with_different_seed(constant.init_probability)











