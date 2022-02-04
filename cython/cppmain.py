# distutils: language=c++
import numpy as np

class Simulation:    
    def __init__(
        self,
        susceptible,
        secure_home,
        exposed,
        infected,
        recovered,
        pending_death,
        dead,
        simulation_time,
        *,
        P_active_function=None
    ): 
        self.simulation_time = simulation_time+1
        
        self.s =  np.zeros(self.simulation_time)
        self.sh = np.zeros(self.simulation_time)
        self.e =  np.zeros(self.simulation_time)
        self.i =  np.zeros(self.simulation_time)
        self.r =  np.zeros(self.simulation_time)
        self.pd = np.zeros(self.simulation_time)
        self.d =  np.zeros(self.simulation_time)
        
        
        self.s[0] = susceptible
        self.sh[0] = secure_home
        self.e[0] = exposed
        self.i[0] = infected
        self.r[0] = recovered
        self.pd[0] = pending_death
        self.d[0] = dead
        
        self.t = 0

        self._P_active_function = (
            P_active_function if P_active_function is not None else lambda x: 0.2
        )

        self.permeability = 0.0  # Permeabilidad de la cuarentena
        self.sigma = 2.3  # Tamaño hogar
        self.k_active = 8.6  # Nº contactos activo
        self.k_conf = 3.2  # Nº contactos confinado
        self.eta = 1.0 / 2.6  # Prob pasar de E a I
        self.landa = 0.07  # Prob de infección exitosa en un contacto
        self.IFR = 0.01  # Prob de dejar de ser infeccioso
        self.mu = 1.0 / 7  # Prob de esperar muerte
        self.what = 1.0 / 7  # Prob de morirse esperando la muerte
        
        self.p_active = 0.2 # Prob de ser activo cuando se activa la cuarentena
        self.step_time = 50 # Momento en el que se activa la cuarentena

    def _P_home_is_secure(self):
        return pow((1 - self.i[self.t]), self.sigma - 1)

    def _P_secure_in_home(self):
        return (1 - self.P_active) * self._P_home_is_secure() * (1 - self.permeability)

    def _P_infection(self):
        P_not_successful_infection = 1 - self.landa * self.i[self.t]

        P_active_infections = self.P_active * (
            1 - pow(P_not_successful_infection, self.k_active)
        )
        P_conf_infections = (1 - self.P_active) * (
            1 - pow(P_not_successful_infection, self.k_conf)
        )

        return P_active_infections + P_conf_infections

    def update_probabilities(self):
        self.P_active = self._P_active_function(self, self.t, self.p_active, self.step_time)
        self.P_infection = self._P_infection()
        self.P_home_is_secure = self._P_home_is_secure()
        self.P_secure_in_home = self._P_secure_in_home()

    def __call__(self):
        for t in range(self.simulation_time-1):
            self.update_probabilities()

            S = self.sh[t] + self.s[t]

            self.sh[t+1] = S * self.P_secure_in_home
            self.s[t+1] = S * (1 - self.P_secure_in_home) * (1 - self.P_infection)

            self.d[t+1] = self.pd[t] * self.what
            self.r[t+1] = self.mu * (1 - self.IFR) * self.i[t]
            self.pd[t+1] = self.mu * self.IFR * self.i[t] + self.pd[t] * (1 - self.what)

            self.i[t+1] = self.e[t] * self.eta + self.i[t] * (1 - self.mu)

            self.e[t+1] = S * (1 - self.P_secure_in_home) * self.P_infection + self.e[self.t] * (
                1 - self.eta
            )
            self.t += 1
    

def funcion_escalon(simulation, t, p_active, step_time):
    # return (simulation.i<0.03)*1 + (simulation.i>=0.03)*0.10
    return (t < step_time) * 1 + (t >= step_time) * p_active