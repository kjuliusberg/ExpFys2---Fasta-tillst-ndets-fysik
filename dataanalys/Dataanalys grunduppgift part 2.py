import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

data_CARY = pd.read_csv('Spektroskopi-data/Transmission_kisel_OFFICIELL.csv', skiprows=1, skipfooter=194, engine='python')
data_CARY = data_CARY.dropna(axis=1, how="all")
datasets_CARY = []

for i in range(0, len(data_CARY.columns), 2):
    sub = data_CARY.iloc[:, i:i+2].copy()
    sub.columns = ['Wavelength (nm)', '%T']
    sub = sub.dropna()
    datasets_CARY.append(sub)

baseline = datasets_CARY[0]
wavelengths_CARY = baseline['Wavelength (nm)']
samples = datasets_CARY[1:]

T_values_CARY = np.array([s["%T"].values for s in samples]) / np.array([baseline["%T"].values])
T_mean_CARY = np.mean(T_values_CARY, axis=0)
T_std_CARY = np.std(T_values_CARY, axis=0)
T_SEM_CARY = T_std_CARY / np.sqrt(len(samples))
print(T_SEM_CARY)
plt.style.use('ggplot')
plt.plot(wavelengths_CARY, T_mean_CARY*100, label = 'Medelvärde av transmissionsspektra')
plt.fill_between(wavelengths_CARY, T_mean_CARY - T_SEM_CARY, T_mean_CARY + T_SEM_CARY, alpha=0.3, label="Osäkerhet (SEM)")
plt.xlabel("Våglängd [nm]")
plt.ylabel("%T")
plt.title('Transmissionsspektra för kisel med Perkin Elmer')
plt.legend()
plt.show()



datasets_PE = [pd.read_csv('Spektroskopi-data/student 07.csv', sep=";", encoding='latin1', skiprows=1, decimal=","),
        pd.read_csv('Spektroskopi-data/student 09.csv', sep=";", encoding='latin1', skiprows=1, decimal=","),
        pd.read_csv('Spektroskopi-data/student 10_1.csv', sep=";", encoding='latin1', skiprows=1, decimal=","),
        pd.read_csv('Spektroskopi-data/student 11.csv', sep=";", encoding='latin1', skiprows=1, decimal=","),
        pd.read_csv('Spektroskopi-data/student 13.csv', sep=";", encoding='latin1', skiprows=1, decimal=",")]

wavelengths_PE = datasets_PE[0]['nm']
wavelengths_PE = wavelengths_PE[268:]
T_values_PE = np.array([s['%T'].values for s in datasets_PE])
T_values_PE = T_values_PE[:, 268:]
T_mean_PE = np.mean(T_values_PE, axis=0)
T_std_PE = np.std(T_values_PE)
T_SEM_PE = T_std_PE/np.sqrt(len(datasets_PE))

plt.plot(wavelengths_PE, T_mean_PE, label = 'Medelvärde av transmissionsspektra')
plt.fill_between(wavelengths_PE, T_mean_PE - T_SEM_PE, T_mean_PE + T_SEM_PE, alpha=0.3, label="Osäkerhet (SEM)")
plt.xlabel("Våglängd [nm]")
plt.ylabel("%T")
plt.title('Transmissionsspektra för kisel med Cary 5000')
plt.legend()
plt.show()

