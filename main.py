import numpy as np
import matplotlib.pyplot as plt

class Simulation:
    
    def __init__(self, susceptible, secure_home, exposed, infected, recovered, pending_death, dead, *, P_active_function=None):
        self.s = susceptible
        self.sh = secure_home
        self.e = exposed
        self.i = infected
        self.r = recovered
        self.pd = pending_death
        self.d = dead
        
        self.t = 0
        self._P_active_function = P_active_function if P_active_function is not None else lambda x: 0.2
        self.landa = 0.015
        self.permeability = 0.20
        self.sigma = 2.3
        self.k_active = 3.2
        self.k_conf = 1.2
        self.eta = 0.2
        self.IFR = 0.007
        self.what = 0.3
    
    def _P_home_is_secure(self):
        return pow((1-self.i), self.sigma-1)
    
    def _P_secure_in_home(self):
        return (1-self.P_active)*self._P_home_is_secure()*(1-self.permeability)
    
    def _P_infection(self):
        P_not_successful_infection = 1 - self.landa * self.i
        
        P_active_infections = self.P_active * (1 - pow(P_not_successful_infection, self.k_active))
        P_conf_infections = (1-self.P_active) * (1 - pow(P_not_successful_infection, self.k_conf))
        
        return P_active_infections + P_conf_infections
    
    def update_probabilities(self):
        self.P_active = self._P_active_function(self.t)
        self.P_infection = self._P_infection()
        self.P_home_is_secure = self._P_home_is_secure()
        self.P_secure_in_home = self._P_secure_in_home()

    def __call__(self):
        self.t += 1
        self.update_probabilities()
        
        S = self.sh + self.s
        
        self.sh = S * self.P_secure_in_home
        self.s = S * (1-self.P_secure_in_home) * (1-self.P_infection)
        
        self.d += self.pd * self.what
        self.r += self.IFR * (1-self.landa) * self.i
        
        self.pd = self.IFR * self.i + self.pd * (1-self.what) 
        self.i = self.e * self.eta + self.i * (1-self.IFR)
    
        self.e = S * (1-self.P_secure_in_home) * self.P_infection + self.e * (1-self.eta)
        
        return self.save_state()
        

    def save_state(self):
        return np.array((self.s, self.sh, self.e, self.i, self.r, self.pd, self.d))
    

def funcion_escalon(t):
    return (t<50)*1 + (t>=50)*0.1

if __name__=='__main__':
    simulation = Simulation(0.95, 0, 0, 0.05, 0, 0, 0, P_active_function=funcion_escalon)
    results = [simulation() for i in range(200)]
    results = list(zip(*results))
    
    for res in results:
        plt.plot(res)
    plt.show()