import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
from scipy.stats import t
from matplotlib.ticker import MaxNLocator

intensitydist = []

# Läs bilder
img_raw = np.array([cv2.imread("Grunduppgift-data/film1-1.jpg"), 
                    cv2.imread("Grunduppgift-data/film1-3.jpg"), 
                    cv2.imread("Grunduppgift-data/film2-1.jpg"),
                    cv2.imread("Grunduppgift-data/film2-2.jpg"), 
                    cv2.imread("Grunduppgift-data/film2-3.jpg"),])
for i in range(len(img_raw)):
    # Introducera litet "blur" för att hitta rätt cirklar
    img = cv2.rotate(img_raw[i], cv2.ROTATE_90_COUNTERCLOCKWISE)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.GaussianBlur(gray, (9, 9), 2)

    # Hitta centrum av de två hålen
    circles = cv2.HoughCircles(
        gray_blur,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=100,
        param1=50,
        param2=30,
        minRadius=10,
        maxRadius=130
    )

    circles = np.around(circles).astype(int)
    (x11, y11, r11), (x22, y22, r22) = circles[0][:2]
    # Ordna hålen från vänster till höger
    if x11 < x22:
        x1, y1 = x11, y11
        x2, y2 = x22, y22
    else:
        x1, y1 = x22, y22
        x2, y2 = x11, y11

    # Skapa samples längs en linje mellan cirkelcentrum
    samples = 5000
    xs = np.linspace(x1, x2, samples, endpoint=True)
    ys = np.linspace(y1, y2, samples, endpoint=True)
    profile = []

    # Ta en intensitetsfördelning längs den samplade linjen
    for x, y in zip(xs, ys):
        xi, yi = int(round(x)), int(round(y))
        profile.append(gray[yi, xi])

    profile = np.array(profile)
    intensitydist.append(profile)

# Skapa en medelintensitetsfördelning
intensitydist = np.mean(intensitydist, 0)

# Ta bort område innan första ringen (undvika onödiga bottnar)
n = len(intensitydist)

mask = np.ones(n, dtype=bool)

# Sätt marginal
margin = int(0.15 * n)
mask[:margin] = False
mask[-margin:] = False

valid_indices = np.where(mask)[0]
filtered_profile = intensitydist[mask]

# Hitta bottnar i intensitetsfördelningen med find_peaks
inv = - filtered_profile
baseline = gaussian_filter1d(inv, sigma=100)
corrected = inv - baseline
peaks, _ = find_peaks(corrected, distance=190, prominence=2, width=1, plateau_size=1)

# Manuellt lägg till 12-toppen där den "ska vara"
range12 = [peaks[3]+100, peaks[4]-100]
peak12 = np.where(corrected == np.max(corrected[range12[0]:range12[1]]))[0][0]
peaks = np.insert(peaks, 4, peak12)
peaks = valid_indices[peaks]


# Skala om till verklig längd
# Pixelavstånd mellan hålen
pixel_dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
meter_per_pixel = 0.09 / pixel_dist

# Hitta peaks i varje bild givet att vi vet ungefär vart de ska vara
window = 50
all_vals = []

for i in range(len(img_raw)-1):
    img = cv2.rotate(img_raw[i], cv2.ROTATE_90_COUNTERCLOCKWISE)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.GaussianBlur(gray, (9, 9), 2)

    circles = cv2.HoughCircles(
        gray_blur,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=100,
        param1=50,
        param2=30,
        minRadius=10,
        maxRadius=130
    )

    circles = np.around(circles).astype(int)
    (x11, y11, r11), (x22, y22, r22) = circles[0][:2]

    if x11 < x22:
        x1, y1 = x11, y11
        x2, y2 = x22, y22
        r1 = r11
        r2 = r22
    else:
        x1, y1 = x22, y22
        x2, y2 = x11, y11
        r1 = r22
        r2 = r11

    xs = np.linspace(x1, x2, samples, endpoint=True)
    ys = np.linspace(y1, y2, samples, endpoint=True)

    profile = []
    for x, y in zip(xs, ys):
        xi, yi = int(round(x)), int(round(y))
        profile.append(gray[yi, xi])

    profile = np.array(profile)
    vals = []

    # I ett fönter runt varje medelpeak, hitta minimum för aktuell bild
    for p in peaks:
        left = max(0, p - window)
        right = min(len(profile), p + window)

        local_idx = np.argmin(profile[left:right])
        true_idx = left + local_idx

        px = xs[true_idx]
        py = ys[true_idx]

        dist_pixels = np.sqrt((px - x1)**2 + (py - y1)**2)
        dist_m = dist_pixels * meter_per_pixel

        vals.append(dist_m)

    all_vals.append(vals)

    output = img.copy()


    # # Rita på bilden vart ringarna finns, för debugging
    # # Rita linje
    # cv2.line(output, (x1, y1), (x2, y2), (255, 0, 0), 2)
    # cv2.circle(output, (x1, y1), 10, (255,0,0), r1)
    # cv2.circle(output, (x2, y2), 10, (0,255,0), r2)

    # # Rita detekterade punkter
    # for p in peaks:
    #     px = int(xs[p])
    #     py = int(ys[p])
    #     cv2.circle(output, (px, py), 3, (0, 0, 255), -1)

    # cv2.namedWindow("Line detection", cv2.WINDOW_NORMAL)
    # cv2.imshow("Line detection", output)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

# Alla peakavstånd i alla bilder
all_vals = np.array(all_vals)

# Beräkna standardavvikelsen för peakavstånden
n = all_vals.shape[0]

mean_vals = np.mean(all_vals, axis=0)
std_vals = np.std(all_vals, axis=0, ddof=1)

# Ta 95% konfidensintervall
tval = t.ppf(0.975, n-1)

# instrumentfel
sigma_pixel = 1
sigma_instr = meter_per_pixel * sigma_pixel

total_std = np.sqrt(std_vals**2 + sigma_instr**2)

sigma_vals = tval * total_std / np.sqrt(n)

vals = mean_vals

print("Vals (mm):", 1000 * vals)
print("Osäkerhet (mm):", 1000 * sigma_vals)

# Visa plot över intensitetsfördelningen
distances_mm = np.linspace(0, 90, samples)
plt.style.use('ggplot')
fig, ax = plt.subplots()
plt.plot(distances_mm, intensitydist, label = 'Intensitetsfördelning')
plt.scatter(distances_mm[peaks], intensitydist[peaks], color='blue', label = 'Ringar')
plt.xlabel('Avstånd [mm]')
plt.ylabel('Intensitet [arb.]')
plt.title("Medelintensitetsfördelning")
ax.xaxis.set_major_locator(MaxNLocator(nbins=10))  # increase tick count
plt.legend()
plt.savefig('Intensitetsfördelning med bottnar.png')


# Manuellt mätta avstånd för de tre filmerna
# vals1 = np.array([22, 25.5, 37.5, 46, 47.8, 69, 73])/1000
# vals2 = np.array([22.1,26,36.6,45.6,47.4,68.7,73])/1000
# vals3 = np.array([22.1,25.8,37.7,45,47.8,68.5,72.8])/1000

# Kod för att få fram heltalsserie, gitterparameter och osäkerheter
R = (57.3/2)/1000
lam = 1.542e-10

theta = vals / (2 * R)
sigma_theta = np.sqrt((sigma_vals / (2 * R))**2)

series = 4 * np.sin(theta)**2 / lam**2
sigma_series = (8 * np.sin(theta) * np.cos(theta) / lam**2) * sigma_theta

series0 = series[-1]
sigma_series0 = sigma_series[-1]

series_norm = 20*series/series0
sigma_series_norm = series_norm * np.sqrt((sigma_series / series)**2 + (sigma_series0 / series0)**2)

hkl_real = np.array([3,4,8,11,12,16,19,20])
y = 4 * np.sin(theta)**2
weights = 1/(sigma_series**2)

coeffs, cov = np.polyfit(hkl_real, y, 1, w=weights, cov = True)
slope = coeffs[0] # y = (lambda/a)**2 x
sigma_slope = np.sqrt(cov[0,0])

a = lam/np.sqrt(slope)
sigma_a = (lam / (2*slope**(1.5)))*sigma_slope

print("Heltalserie:", ", ".join(f"{val:.2f} ± {err:.2f}" for val, err in zip(series_norm, sigma_series_norm)))
print(f"a = {(a/1e-10):.4} ± {(sigma_a/1e-10):.2} Å")