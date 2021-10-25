import numpy as np
import matplotlib.pyplot as plt
from phaseportrait.sliders import sliders


class Simulation:
    # Esto hace falta para los sliders
    _name_='Simulation_PhasePortrait'
    
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
        
        self.fig, self.ax = plt.subplots()
        self.death_fig, self.death_ax = plt.subplots()
        self.sliders = {}

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
    
    def add_slider(self, param_name, *, valinit=None, valstep=0.1, valinterval=10):
        self.sliders.update({param_name: sliders.Slider(self, param_name, valinit=valinit, valstep=valstep, valinterval=valinterval)})

        self.fig.subplots_adjust(bottom=0.25)

        self.sliders[param_name].slider.on_changed(self.sliders[param_name])
        
        
    def plot(self, scale=None):
        if scale is not None:
            self.scale = scale
        # self.dF_args.update({name: slider.value for name, slider in self.sliders.items() if slider.value!= None})

        for name, slider in self.sliders.items():
            if slider.value!= None:
                self.__dict__[name] = slider.value
            
        self()

        time = np.arange(0, self.simulation_time)

        self.ax.plot(time, self.sh*self.scale, label='sh')
        self.ax.plot(time, self.s*self.scale, label='s')
        self.ax.plot(time, self.e*self.scale, label='e')
        self.ax.plot(time, self.i*self.scale, label='i')
        self.ax.plot(time, self.pd*self.scale, label='pd')
        self.ax.plot(time, self.d*self.scale, label='d')
        self.ax.plot(time, self.r*self.scale, label='r')
        
        # self.death_ax.plot(time, self.i*self.scale, label='i')
        self.death_ax.plot(time, self.d*self.scale, label='d')
        self.death_ax.get_autoscaley_on()
        
        self.ax.legend()
        self.ax.grid()
        self.death_ax.grid()
        self.t = 0
        
        return self.fig, self.ax
        


def funcion_escalon(simulation, t, p_active, step_time):
    # return (simulation.i<0.03)*1 + (simulation.i>=0.03)*0.10
    return (t < step_time) * 1 + (t >= step_time) * p_active


if __name__ == "__main__":
    
    N = 34e6
    I = 1
    simulation = Simulation(
        (N-I)/N, 0, I/N, 0, 0, 0, 0, 200, P_active_function=funcion_escalon
    )
    
    simulation.add_slider('permeability', valinit=0, valinterval=[0,1], valstep=0.05)
    simulation.add_slider('p_active', valinit=0.2, valinterval=[0,1], valstep=0.05)
    simulation.add_slider('step_time', valinit=50, valinterval=[0,200], valstep=1)
    
    fig, ax = simulation.plot(N)
    
    plt.show()
