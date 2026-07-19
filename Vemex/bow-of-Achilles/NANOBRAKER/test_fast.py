import time
from kerr_engine import BlackHole, fast_signal

bh = BlackHole(M=1.0, a=0.92)
t0 = time.time()
sig = fast_signal(bh, r0=30.0, n=None)
t1 = time.time()

n = sig['n']
print('N=' + str(n))
print('elapsed=' + str(round(t1-t0, 6)) + 's')
print('Omega=' + str(sig['Omega'].min()) + ' to ' + str(sig['Omega'].max()))
print('Grad=' + str(sig['grad'].min()) + ' to ' + str(sig['grad'].max()))
