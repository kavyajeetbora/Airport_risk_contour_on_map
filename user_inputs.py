from airport_risk import plot_airport_risk
import time

## USER INPUTS:

## 1. AIRPORT CONSTANTS (constants of plane depeding on the plane size: large or small)
## ____________________________________________________________________________________
A = {
    "r0": 5000, ## unit is KM
    "theta0": 5, ## unit is degrees
    "k": 0.23 ## constant
}

## 2. Define all the runways present in the airport

## Frankfurt Airport
frankfurt_airport = {
    "title": "Frankfurt Airport",
    ## Contains the coordinates of each runways end to end and also the Likelihood of accident for each runway
    "runways": {  
        "L": {
            "A": (8.497104, 50.037093),
            "B": (8.533707, 50.045829),
            "P" :  0.02*10**-6 * 212235/6 ## 
        },
        "R": {
            "A":(8.534249, 50.027578),
            "B":(8.586519, 50.040053),
            "P" :  0.02*10**-6 * 212235/6
        },
        "C": {
            "A": (8.534724, 50.032642),
            "B": (8.587042, 50.045163),
            "P" :  0.02*10**-6 * 212235/6
        },
        "18": {
            "A" : (8.525902, 50.034182),
            "B" : (8.526343, 49.998493),
            "P" :  0.02*10**-6 * 100  
        }
    },  
    "epsg": 5243, ## UTM CRS code for frankfurt airport to convert the coordinates from degrees to meters
    "A": A ## other airport contants
}

## 3. Set the contour configuration:
## ______________________________________________________

contour_config = {
    "DI" : 10, ## distance_interval
    "DL": 30000, ## maximum distance of the contour (meters)
    "AI": 5, ## Angle intervals 
    "AL": 60 ## maximum angle of the contour (degrees)
} 

if __name__ == "__main__":
    ## find the contours for all the runways
    start_time = time.time()
    print("Calculating the airport risk....")
    contours = plot_airport_risk(frankfurt_airport, contour_config)
    print("Total Time Lapsed %.2f seconds to calculate the risk contours" % (time.time()-start_time))

'''
Inputs for another airport - Dallas Airport:

dallas_airport = {
    "title": "Dallas Airport",
    "runways": {
        "13R/31L": {
            "A": (-97.08322, 32.90963),
            "B": (-97.06329, 32.89029),
            "P" :  0.02*10**-6 * 600
        },
        "18R/36L": {
            "A":(-97.05465, 32.91582),
            "B":(-97.05485, 32.87902),
            "P" :  0.02*10**-6 * 2400
        },
        "18L/36R": {
            "A": (-97.05074, 32.91581),
            "B": (-97.05092, 32.87899),
            "P" :  0.02*10**-6 * 3000
        },
        "17R/35L": {
            "A" : (-97.02989, 32.91569),
            "B" : (-97.03009, 32.87891),
            "P" :  0.02*10**-6 * 2000
        },
        "17C/35C": {
            "A": (-97.02599, 32.91569),
            "B": (-97.02618, 32.87886),
            "P" :  0.02*10**-6 * 1000
        },
        "17L/35R": {
            "A": (-97.00978, 32.89835),
            "B": (-97.00992, 32.87497),
            "P" :  0.02*10**-6 * 500
        },
        "13L/31R": {
            "A": (-97.02005, 32.91132),
            "B": (-97.00085, 32.895),
            "P" :  0.02*10**-6 * 200
        }
    },  
    "epsg": 3486,
    "A": A
}

'''