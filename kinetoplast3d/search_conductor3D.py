'''
Module name: search_conductor3D.py
Author: Nathaniel Morrison
Date created: 06/29/2020
Date last modified: 06/29/2020
Python Version: 3.7.2
'''
from time import localtime, strftime, time
from datetime import timedelta
import grid_gen3D as gg
import graph_funcs3D as gf
import bf_search3D as bf
import dissolusion_plot3D as dp
from joblib import Parallel, delayed
from kinetoplast3D import kinetoplast3D
import os

#The function that will run in parallel
def task(i):
    cwd = os.getcwd()
    #Manually input all parameters here
    rad=1
    rows=70
    columns=70
    planes=1
    boundary_sat=0
    maxi_rad=2
    maxi_amount=0
    resolution=1
    thresh=10
    #Get the current date
    date=strftime("%Y-%m-%d %H:%M:%S", localtime())[0:10].replace('-','')
    #Generate the output file name
    excel_name=date+'_RKP_NM_randomGrid3D_'+str((i+1))
    #Delete the kp object if it already exists
    try:
        del kp
    except:
        pass
    #Instantiate the kp object
    kp=kinetoplast3D(rows,columns,planes,rad)
    #If the user wants to super-saturate the boundary
    if boundary_sat>0:
        #Do that
        kp.add_boundary(boundary_sat)
    #If the user wants to add maxi circles
    if maxi_amount>0:
        #Do that
        kp.add_maxi_circles(maxi_rad,maxi_amount)
    #Compile the grid into a graph
    kp.compile_graph()
    deg_file=open(cwd+"degs"+str(i)+".txt",'w')
    deg_file.write((str(kp.avg_deg())+", "+str(kp.min_deg())))
    deg_file.close()
    #Run the dissolution simulation
    kp.dissolve(resolution,thresh,excel_name)
    return
    
#Function to do a dissolution search using a 3D random grid
def randomized_search(iterations,threads):
    #Gather start time of computation
    start=time()
    lis=range(iterations)
    #Do the iterations in parallel. n_jobs=number of cores to use, verbose=10 => print timing for each individual process,
    #delayed([name of function to be parallelized])([argument]) defines the function to be parallelized, and for [argument] in [argument list] iterates the argument.
    Parallel(n_jobs=threads,verbose=10)(delayed(task)(p) for p in lis)
    #Print the current iteration and the time elapsed.
    print("Done. Time elapsed: "+str(timedelta(seconds=(time()-start))))
    return

def graphite_search(xdim,ydim,zdim,sat,maxi_rad,maxi_amount,iterations,res,thresh):
    from hkinetoplast3D import hkinetoplast3D
    start=time()
    #Do this as many times as the user requests
    for i in range(iterations):
        #Get the current date
        date=strftime("%Y-%m-%d %H:%M:%S", localtime())[0:10].replace('-','')
        #Generate the output file name
        excel_name=date+'_RKP_NM_hexagonalGrid3D_'+str((i+1))
        #Delete the kp object if it already exists
        try:
            del kp
        except:
            pass
        #Instantiate the kp object
        kp=hkinetoplast3D(xdim,ydim,zdim)
        #If the user wants to super-saturate the boundary
        if sat>0:
            #Do that
            kp.add_boundary(sat)
        #If the user wants to add maxi circles
        if maxi_amount>0:
            #Do that
            kp.add_maxi_circles(maxi_rad,maxi_amount)
        #Compile the grid into a graph
        kp.compile_graph()
        #Run the dissolution simulation
        kp.dissolve(res,thresh,excel_name)
        #Print the current iteration and the time elapsed.
        print("Iteration "+str((i+1))+" done. Time elapsed: "+str(timedelta(seconds=(time()-start))))
    return
    
#Function to let this run independent of another script
def main():
    #Collect logisitcal parameters and do the search
    iterations=int(input("Enter number of iterations: "))
    threads=int(input("Enter number of threads: "))
    randomized_search(iterations,threads)
#main()
    
