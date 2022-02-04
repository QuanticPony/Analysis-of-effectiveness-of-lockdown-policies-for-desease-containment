import matplotlib.pyplot as plt
import numpy as np
        
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