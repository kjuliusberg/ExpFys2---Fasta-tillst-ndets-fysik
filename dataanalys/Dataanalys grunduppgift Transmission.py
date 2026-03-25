import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

plt.style.use('ggplot')

# -- Mätning med Cary 5000 --
# Ta in data
data_CARY = pd.read_csv('dataanalys/Spektroskopi-data/Transmission_kisel_OFFICIELL.csv', skiprows=1, skipfooter=194, engine='python')
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

# Medelvärdera, plotta och ta fram standardavvikelse
T_values_CARY = 100*np.array([s["%T"].values for s in samples]) / np.array([baseline["%T"].values])
T_mean_CARY = np.mean(T_values_CARY, axis=0)
T_std_CARY = np.std(T_values_CARY, axis=0)
T_SEM_CARY = T_std_CARY / np.sqrt(len(samples))

fig, ax = plt.subplots()
plt.plot(wavelengths_CARY, T_mean_CARY, label = 'Medelvärde av transmissionsspektra')
plt.vlines(1040, 0, 25, color = 'b', alpha = 0.75, label = '1040 nm', linestyles='dotted')
plt.fill_between(wavelengths_CARY, T_mean_CARY - T_SEM_CARY, T_mean_CARY + T_SEM_CARY, alpha=0.3, color = 'b', label="Medelfel")
plt.xlabel("Våglängd [nm]")
plt.ylabel("%T")
plt.title('Transmissionsspektra för kisel med Cary 5000')
plt.legend()
plt.savefig('Transmissionsspektra Medel Cary 5000')


# -- Mätning med PerkinElmer --
# Ta in data
datasets_PE = [pd.read_csv('dataanalys/Spektroskopi-data/student 07.csv', sep=";", encoding='latin1', skiprows=1, decimal=","),
        pd.read_csv('dataanalys/Spektroskopi-data/student 09.csv', sep=";", encoding='latin1', skiprows=1, decimal=","),
        pd.read_csv('dataanalys/Spektroskopi-data/student 10_1.csv', sep=";", encoding='latin1', skiprows=1, decimal=","),
        pd.read_csv('dataanalys/Spektroskopi-data/student 11.csv', sep=";", encoding='latin1', skiprows=1, decimal=","),
        pd.read_csv('dataanalys/Spektroskopi-data/student 13.csv', sep=";", encoding='latin1', skiprows=1, decimal=",")]


# Medelvärdera, plotta och ta fram standardavvikelse
wavelengths_PE = datasets_PE[0]['nm']
wavelengths_PE = wavelengths_PE[268:]
T_values_PE = np.array([s['%T'].values for s in datasets_PE])
T_values_PE = T_values_PE[:, 268:]

# Troubleshooting plot
# for i in range(len(T_values_PE)):
#     plt.plot(wavelengths_PE, T_values_PE[i])
#     plt.show()

T_mean_PE = np.mean(T_values_PE, axis=0)
T_std_PE = np.std(T_values_PE)
T_SEM_PE = T_std_PE/np.sqrt(len(datasets_PE))

fig, ax = plt.subplots()
plt.plot(wavelengths_PE, T_mean_PE, label = 'Medelvärde av transmissionsspektra')
plt.fill_between(wavelengths_PE, T_mean_PE - T_SEM_PE, T_mean_PE + T_SEM_PE, alpha=0.3, color = 'b', label="Medelfel")
plt.xlabel("Våglängd [nm]")
plt.ylabel("%T")
plt.title('Transmissionsspektra för kisel med Perkin Elmer 1725')
plt.legend()
plt.savefig('Transmissionsspektra Medel Perkin Elmer 1725')

