import numpy as np

vals1 = np.array([22, 25.5, 37.5, 46, 47.8, 58.5, 69, 73]) / 1000
vals2 = np.array([22.1, 26, 36.6, 45.6, 47.4, 58.5, 68.7, 73]) / 1000
vals3 = np.array([22.1, 25.8, 37.7, 45, 47.8, 58.5, 68.5, 72.8]) / 1000

vals = (vals1 + vals2 + vals3)/3

R = (57.3/2)/1000

theta =  vals/(2*R)

lam = 1.542e-10

series = 4*np.sin(theta)**2/lam**2

series0 = series[7]

print(20*series/series0)

a = (20/series0)**0.5

print(a)
