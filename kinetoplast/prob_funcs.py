'''
Module name: prob_funcs.py
Author: Nathaniel Morrison
Date created: 05/23/2020
Date last modified: 06/10/2020
Python Version: 3.7.2
'''
from scipy.integrate import quad, dblquad
from scipy import sqrt, cos
from numpy import arccos, isnan, pi
from random import random
import warnings
#Invalid values may periodically be found for angles and areas. These are screened for, but warning messages still pop up. So, disable warnings.
warnings.simplefilter("ignore")

#Function to define the probability function for every circle. Note that the other functions in this module do not currently support an angle (t) dependence.
def prob_func(r,t):
    return 1.5

#Function to find the cartesian distance between points p1 and p2
def dist(p1,p2):
    return sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)

def alg_area(d,r1,r2):
    A=r1**2*arccos((d**2+r1**2-r2**2)/(2*d*r1))+r2**2*arccos((d**2+r2**2-r1**2)/(2*d*r2))-sqrt(y(d,r1,r2))/2
    if isnan(A):
        A1=pi*r1**2
        A2=pi*r2**2
        if A1<A2:
            A=A1
        else:
            A=A2
    return A*prob_func(r,t)

def y(d,r1,r2):
    return (-d+r1+r2)*(d+r2-r1)*(d-r2+r1)*(d+r1+r2)

#Function to check if there is any possibility of an intersection and, if so, determine the theta values of the intersect region assuming first circle 1 is on the left and then
#assuming circle 2 is on the left.
def intersect_check(cent1,cent2,rad1,rad2):
    #Find distance from one center to the other
    d=dist(cent1,cent2)
    #If the distance between the centers is less than he sum of their radii, then an intersection is possible.
    if d<(rad1+rad2):
        #z assuming circle 1 is on the left
        z1=(d**2-rad1**2+rad2**2)/(2*d)
        #z assuming circle 2 is on the left
        z2=(d**2-rad2**2+rad1**2)/(2*d)
        #Half angle assuming circle 1 is on the left
        t1=abs(arccos(z1/rad1))
        #Half angle assuming circle 2 is on the left
        t2=abs(arccos(z2/rad2))
        return True, d,t1,t2
    #Otherwise, an intersection is not possible.
    else:
        return False, d,0,0

#Function to integrate the probability distribution function over the intersect region.
def prob_integrator(d,r1,r2):
    #Find the angle at which the edge fo circle 1 and circle 2 intersect
    th=arccos((r1**2+d**2-r2**2)/(2*d*r1))
    #If the angle does not exist, then one circle is entirely within another
    if isnan(th):
        #Figure out which circle is inside the other by determining which has a smaller area. Note that the integration of circle 2 here assumes that the probability function
        #does not depend on radius. I cannot for the life of me figure out how to get Python to correctly integrate circle 1's function over circle 2's area. I know what the
        #integral is, and if I do it halfway by hand it works out, but for whatever reason python gives a massive error when I try to make it do the double integral when and
        #only when circle 2 lies entirely to the right of the y-axis. In every other case it gives a perfect answer. In that case it dosen't, and I don't know why. So, I
        #manually integrated the radial component and am only having python integrate theta.
        A1=pi*r1**2
        A2=pi*r2**2
        if A2<A1:
            return quad(lambda r:0.5*(d*cos(r)-sqrt(cos(r)**2*d**2-d**2+r2**2))**2*prob_func(1,r),0,2*pi)[0]
        else:
            #Integrate circle 1's probability function over its entire area
            return dblquad(lambda r,t:r*prob_func(r,t),-pi,pi,lambda r:0,lambda r:r1)[0]
    #We have two cases, depending upon whether some of circle 2 lies to the left of the y-axis or not. If some of it does...
    if d-r2<=0:
        #Then integrate in two pieces. The first piece is between the interesction points. This is just integrating up to circle 1.
        A1=dblquad(lambda r,t:r*prob_func(r,t),-th,th,lambda r:0,lambda r:r1)[0]
        #The second is all other angles. Here, we must integrate up to circle 2.
        A2=dblquad(lambda r,t:r*prob_func(r,t),th,(2*pi-th),lambda r:0,lambda r:d*cos(r)+sqrt(cos(r)**2*d**2-d**2+r2**2))[0]
        #The final area is the sum of these two pieces
        return A1+A2
    #If circle 2 lies entirely to the right of the y-axis...
    elif d-r2>0:
        #Then integrate between the interesct points from the edge of circle 2 to the edge of circle 1. Note that for computational reasons this integral will produce a fairly
        #substantial error when the d is close to r2. The error declines the larger d is compared to r2.
        return dblquad(lambda r,t:r*prob_func(r,t),-th,th,lambda r:d*cos(r)-sqrt(d**2*cos(r)**2-d**2+r2**2),lambda r:r1)[0]

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

    #Function to determine probability that two loops with centers cent1 and cent2 and radii rad1 and rad2 are linked
def prob_of_link_alg(cent1,cent2,rad1,rad2):
    #Check if an intersection is possible and gather the intersect angles
    icr=intersect_check(cent1,cent2,rad1,rad2)
    #If there is an intersection...
    if icr[0]:
        #Integrate the probability function of each circle over the intersect region and multiply the results of each circle. This is the probability of a link.
        return alg_area(icr[1],rad1,rad2)/(pi*rad1**2)
    #If there is no intersection...
    else:
        #Then there is no probability of a link.
        return 0

#Function to determine if two loops with centers cent1 and cent2 and radii rad1 and rad2 are linked
def are_linked(cent1,cent2,rad1,rad2):
    #Determine the probability of a link
    prob=prob_of_link(cent1,cent2,rad1,rad2)
    #Generate a random number from - to 1. If the number happens to be leq the probability of a link, then there is a link. Otherwise, there is no link.
    if random()<=prob:
        return True
    else:
        return False

    #Function to determine if two loops with centers cent1 and cent2 and radii rad1 and rad2 are linked
def are_linked_alg(cent1,cent2,rad1,rad2):
    #Determine the probability of a link
    prob=prob_of_link_alg(cent1,cent2,rad1,rad2)
    #Generate a random number from - to 1. If the number happens to be leq the probability of a link, then there is a link. Otherwise, there is no link.
    if random()<=prob:
        return True
    else:
        return False
