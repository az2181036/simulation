import scipy.io

qos = 0.5
task_num = 1000
data = scipy.io.loadmat("..\\mat\\1e-2\\info_4_1e-2")
n = int(data["n"])
m = int(data["m"])
utilization_threshold = 0.95
_lambda = data["lambda"][0]
tt = data['t'][0]
energy_unit_price = float(data["compute_unit_price"][0])
trans_sigma = float(data["trans_unit_price"][0])
server_list = data["server_list"]
probability_lst = data["now_probility"]
init_probability = [data["init_probility"][0] for i in range(8)]