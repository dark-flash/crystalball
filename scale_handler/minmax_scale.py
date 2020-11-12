
from scale_handler.abstract_scale import abstract_scale
import numpy as np

class minmax_scale(abstract_scale):
    def __init__(self):
        super().__init__()
        scale_type = 'minmax'
        self.scale_params['scale_type'] = scale_type

    def calc_scale(self, input, col_name):
        col_num = len(input[0])
        for idx in range(0, col_num):
            col_value_list = input[:, idx]
            max_value = max(col_value_list)
            min_value = min(col_value_list)
            calc_col_value = [(float(x) - min_value) / (max_value - min_value + 1e-6) for x in col_value_list]
            self.output.append(calc_col_value)
            self.scale_params[col_name[idx]] = (min_value, max_value)
        self.output = np.array(self.output).T

    def calc_reconstruct_scale(self, input, params):
        del(params["scale_type"])
        key_list = list(params.keys())
        for id in range(len(key_list)):
            col_input = input[:, id]
            col_min = params[key_list[id]][0]
            col_max = params[key_list[id]][1]
            reconstruct_col_value = [(float(x) - float(col_min)) / (float(col_max) - float(col_min) + 1e-6) for x in col_input]
            self.reconstruct.append(reconstruct_col_value)
        self.reconstruct = np.array(self.reconstruct).T

