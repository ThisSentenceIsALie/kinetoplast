'''
Module name: prob_funcs3D.py
Author: Nathaniel Morrison
Date created: 06/22/2020
Date last modified: 06/22/2020
Python Version: 3.7.2
'''
from scipy.integrate import tplquad
from scipy import sqrt, sin
from numpy import arccos, isnan, pi
from random import random
import warnings
#Invalid values may periodically be found for angles and areas. These are screened for, but warning messages still pop up. So, disable warnings.
warnings.simplefilter("ignore")

#Function to define the probability function for every circle. Note that the other functions in this module do not currently support an angle (t) dependence.
def prob_func(r,ph,z):
    return 1.5

#Function to find the cartesian distance between points p1 and p2
def dist(p1,p2):
    return sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2+(p1[2]-p2[2])**2)

#Function to check if there is any possibility of an intersection and, if so, determine the theta values of the intersect region assuming first circle 1 is on the left and then
#assuming circle 2 is on the left.
def intersect_check(cent1,cent2,rad1,rad2):
    #Find distance from one center to the other
    d=dist(cent1,cent2)
    #If the distance between the centers is less than he sum of their radii, then an intersection is possible.
    if d<(rad1+rad2):
        return True, d
    #Otherwise, an intersection is not possible.
    else:
        return False, d

#Function to integrate the probability distribution function over the intersect region.
def prob_integrator(d,r1,r2):
    #If sphere 1 entirely swallows sphere 2
    if (d+r2)<r1:
        #Integrate sphere 1's probability function over sphere 2's volume
        return tplquad(lambda r,z,ph: r*prob_func(r,ph,z), 0, 2*pi, lambda ph: (d-r2), lambda ph: (d+r2), lambda z,ph: 0, lambda z,ph: sqrt(r2**2+2*z*d-d**2-z**2))[0]
    #If sphere 2 entirely swallows sphere 1
    elif (r1<(d-r2)):
        #Integrate sphere 1's probability function over sphere 1's volume
        return tplquad(lambda r,z,ph: r*prob_func(r,ph,z), 0, 2*pi, lambda ph: -r1, lambda ph: r1, lambda z,ph: 0, lambda z,ph: sqrt(r1**2-z**2))[0]
    #If the sphere boundaries actually intersect somewhere
    else:
        #Determine the "midpoint" of the integration region
        zmid=r1*sin(arccos((d**2+r1**2-r2**2)/(2*r1*d)))
        #Compute the volume of the lower "half" of the integration region
        v1=tplquad(lambda r,z,ph: r*prob_func(r,ph,z), 0, 2*pi, lambda ph: (d-r2), lambda ph: zmid, lambda z,ph: 0, lambda z,ph: sqrt(r2**2+2*z*d-d**2-z**2))[0]
        #Add the volume of the upper half and return the result
        return v1+tplquad(lambda r,z,ph: r*prob_func(r,ph,z), 0, 2*pi, lambda ph: zmid, lambda ph: r1, lambda z,ph: 0, lambda z,ph: sqrt(r1**2-z**2))[0]

#Function to determine probability that two loops with centers cent1 and cent2 and radii rad1 and rad2 are linked
def prob_of_link(cent1,cent2,rad1,rad2):
    #Check if an intersection is possible and gather the intersect angles
    icr=intersect_check(cent1,cent2,rad1,rad2)
    #If there is an intersection...
    if icr[0]:
        #Integrate the probability function of each circle over the intersect region and multiply the results of each circle. This is the probability of a link.
        return prob_integrator(icr[1],rad1,rad2)/(pi*rad1**2)
    #If there is no intersection...
    else:
        #Then there is no probability of a link.
        return 0

#Function to determine if two loops with centers cent1 and cent2 and radii rad1 and rad2 are linked
def are_linked(cent1,cent2,rad1,rad2):
    #Determine the probability of a link
    prob=prob_of_link(cent1,cent2,rad1,rad2)
    #Generate a random number from 0 to 1. If the number happens to be leq the probability of a link, then there is a link. Otherwise, there is no link.
    if random()<=prob:
        return True
    else:
        return False
