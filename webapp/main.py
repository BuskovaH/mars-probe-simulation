import numpy as np
import time
import matplotlib.pyplot as plt
import streamlit as st


units = {"length":"m", "mass":"kg", "time":"s"}
M = 6.4171*10**23 # mass of Mars in kg
m = 100 # ballpark of the mass of our probe
G = 6.67430*10**(-11) # gravitational constant in m^3/kg*s^2
delta_t = 30 #s
timesteps = 100000
radius = 33895000 # radius of Mars in meters
atm_height = 130000 # height of atmosphere in meters


def update_acceleration(frame):
    x, y, v_x, v_y = frame
    r2 = x**2 + y**2
    r = np.sqrt(r2)
    v2 = v_x**2 + v_y**2
    v = np.sqrt(v2)
    gravF_x = -((G*M*m)/(r2))*(x/r)
    gravF_y = -((G*M*m)/(r2))*(y/r)
    dragF = 0.5*rho(r2)*v2*0.42*4
    F_x = gravF_x + dragF*v_x/v
    F_y = gravF_y + dragF*v_y/v
    a_x = F_x/m
    a_y = F_y/m
    return [a_x, a_y]


def update_phasespace(frame):
    x, y, v_x, v_y = frame
    a_x, a_y = update_acceleration(frame)
    v_x = v_x + a_x*delta_t
    v_y = v_y + a_y*delta_t
    x = x + v_x*delta_t
    y = y + v_y*delta_t
    return [x, y, v_x, v_y]


def rho(r2): #this is stupid and I'm ashamed, the error is not huge for Mars though.
    pressure = 610 #Martian at ground level
    atmosphere_height = 130000 #m
    grav_acceleration = 3.72076 #m/s-2
    if r2 > radius+atm_height:
        return 0
    else:
        return pressure/(atmosphere_height*grav_acceleration)


def crashcheck(frame):
    x, y, v_x, v_y = frame
    r2 = x**2 + y**2
    if r2 < radius**2:
        print("Probe landed with speed " + str(np.sqrt(frame[2]**2 + frame[3]**2)))
        print("Angle of entry is " + str(np.arctan2(v_y, v_x)*180/np.pi))
        return True
    else:
        return False
        
def measure_eccentricity(frames):
    centroid_x = np.mean(frames[:, 0])
    centroid_y = np.mean(frames[:, 1])
    distances = np.linalg.norm(frames[:, 0:1]-np.array([centroid_x, centroid_y]), axis=1)
    print(distances)
    a = np.min(distances)
    b = np.max(distances)
    if a<b:
        return np.sqrt(1-(a*a/b/b))
    else:
        return np.sqrt(1-(b*b/a/a))
    

def plot(frames):
    lim = np.max(np.abs(frames[:, 0:1]))
    # prompt: from x and y make a scatter plot that progressively colours each point.
    fig, ax = plt.subplots()
    sc = ax.scatter(frames[:, 0], frames[:, 1], c=np.arange(len(frames[:,0])), s=5, cmap='viridis')
    center = ax.scatter(0, 0, c='red', s=10)
    circle = ax.add_patch(plt.Circle((0, 0), radius, color='red', fill=False))
    ax.set_xlabel(f"x [{units['length']}]")
    ax.set_ylabel(f"y [{units['length']}]")
    ax.set_ylim(-lim, lim)
    ax.set_xlim(-lim, lim)
    ax.set_title("Simulation of the path of m around M")
    fig.colorbar(sc, label="Timestep")
    # plt.show()
    st.pyplot(fig)


def s_to_dhms(seconds):
    days = int(seconds/86400)
    hours = int((seconds-(days*86400))/3600)
    minutes = int((seconds-(days*86400)-(hours*3600))/60)
    seconds = int(seconds-(days*86400)-(hours*3600)-(minutes*60))
    return days, hours, minutes, seconds


st.title("Simulace přistání na Marsu")
st.subheader("Webové rozhraní")
st.write("<b>Níže máte předepsáno jak daleko je vaše sonda od středu planety (v metrech). Metodou pokusu a omylu najděte takovou počáteční rychlost, aby se sonda při přistání na planetu nerozbila.</b>", unsafe_allow_html=True)


x_0 = 3*radius # starting position of the satellite in meters: pick whatever, roll a die.
y_0 = 0
v_x0 = 0  # starting speed in m/s
v_y0 = 500 # to simplify our problem, we have speed perpendicular to the position vector
  # thanks to that simplification, we also know that the beginning of the path
  # of the satellite is one of the pointy ends of an ellipse

x_0_random = np.random.randint(2,6)

try:
    x_0 = float(st.text_input(label="Počáteční poloha", placeholder = x_0_random, key="poloha v počtu poloměrů nad planetou"))
except ValueError:
    x_0 = x_0_random

try:
    v_y0=float(st.text_input(label="Počáteční rychlost v m/s", placeholder = "500", key="rychlost"))
except ValueError:
    v_y0=500
    st.write("An error was handled by pretending you entered 500 m/s for speed of probe.")    

st.button(label = "Spočítat simulaci", help = "Napiš nahoře číslo a klikni na mě!", type="primary")
  
start = time.time()
frame = [x_0, y_0, v_x0, v_y0]
frames = [frame]
for i in range(timesteps):
    frame = update_phasespace(frame)
    frames.append(frame)
    if crashcheck(frame) == True:
      break
frames = np.array(frames)
mid = time.time()
days, hours, minutes, seconds = s_to_dhms(len(frames[:,0])*delta_t)

plot(frames)

st.write("Simulated time", str(days), "days", str(hours), "hours", str(minutes), "minutes", str(seconds), "seconds")
st.write("Average velocity", np.round(np.mean(np.sqrt(frames[:, 2]**2 + frames[:, 3]**2))/1000, 1), "km/s")
end = time.time()
st.write("Simulation took", np.round(mid-start, 3), "seconds to process, with", np.round(end-mid, 3), "second overhead.")
st.write("Eccentricity ", measure_eccentricity(frames))

st.session_state

