import matplotlib.pyplot as plt
from math import sin
from phaseportrait import PhasePortrait2D
import numpy as np

# with open("random.txt", 'r') as file:
#     rand, = zip(*(map(float, line.split('\t')) for line in file))
    
# plt.plot(rand)
# plt.show()
# exit()


with open("data.txt", 'r') as file:
    time, sh, s, e, i, pd, d, r = zip(*(map(float, line.split('\t')) for line in file))
 

fig, ax = plt.subplots()

ax.plot(time, sh)
ax.plot(time, s)
ax.plot(time, i)
ax.plot(time, e)
ax.plot(time, pd)
ax.plot(time, d)
ax.plot(time, r)
plt.show()

exit()

fig2, ax2 = plt.subplots()
ax2.grid()
ax2.plot(time, pos, label='Posicion')
ax2.plot(time, mom, label='Momento')
ax2.legend()

fig3, ax3 = plt.subplots()

kin_cum = [sum(kin[:i])/i for i in range(1, len(kin))]
pot_cum = [sum(pot[:i])/i for i in range(1, len(pot))]

ax3.plot(kin_cum, label='E Cinética')
ax3.plot(pot_cum, label='E Potencial')
ax3.legend()

fig4, ax4 = plt.subplots()
ax4.hist(mom, bins=20)
ax4.set_title('Momento')

ax4.legend()

fig5, ax5 = plt.subplots()
ax5.hist(pos)
ax5.set_title('Posicion')

ax5.legend()


plt.show()