import cupy as cp
import cupy.random as cprand

param_to_index = {
    'permeability' : 0,
    'lambda' : 1,
    'IFR' : 2,
    'what' : 3,
    'initial_i' : 4,
    # 'mu' : 5,
    'offset' : 5,
}

fixed_params_to_index = {
    'home_size' : 0,
    'k_average_active' : 1,
    'k_average_confined' : 2,
    'mu' : 3,
    'eta' : 4,
}

class Params_Manager:
    def __init__(self, configuration: dict):
        self.configuration = configuration
        
    def set_params(self, params, size=1):
        counter = 0
        for param_name, param_range in self.configuration["params"].items():
            param_index = param_to_index.get(param_name)
            if param_index is not None:
                counter += 1
                if param_name == 'offset':
                    params[param_index] = cprand.randint(param_range["min"], param_range["max"]+1, self.configuration["simulation"]["n_simulations"], dtype=cp.int32)
                else:
                    params[param_index] = cprand.random(self.configuration["simulation"]["n_simulations"], dtype=cp.float64) * (param_range["max"] - param_range["min"]) + param_range["min"]

        if counter < len(param_to_index.keys()):
            raise Exception("params array could not be completed with current options.")


    def set_fixed_params(self, fixed_params):
        counter = 0
        for fparam_name, value in self.configuration["fixed_params"].items():
            fparam_index = fixed_params_to_index.get(fparam_name)
            if fparam_index is not None:
                counter += 1 
                fixed_params[fparam_index] = value

        if counter < len(fixed_params_to_index.keys()):
            raise Exception("fixed_params array could not be completed with current options.")


    def save_parameters(self, files, params, log_diff, recovered):
        for i, l in enumerate(log_diff):
            for k,f in files.items():
                if k=='log_diff':
                    f.write(str(log_diff[i]))
                    f.write('\n')
                if k=='recovered':
                    f.write(str(recovered*100))
                    f.write('\n')
                else:
                    f.write(str(params[param_to_index[k]][i]))
                    f.write('\n')