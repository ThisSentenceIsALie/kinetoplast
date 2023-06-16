'''
File name: new_search_manager.py
Author: Nathaniel Morrison
Date created: 01/10/2023
Date last modified: 01/16/2023
Python Version: 3.11.1
'''
'''
Like search_conductor, but better in every way. Especially the new auto-generated file heirarchy system, now compatable with other people's computers too!
'''
import numpy as np
from hkinetoplast import hkinetoplast
from kinetoplast import kinetoplast
from time import localtime, strftime, time
from datetime import timedelta
import os
import pickle
from copy import deepcopy
from compTracker import compTracker


def run_hkinetoplast_search(rows=10, columns=10, boundary_sat=0,iterations=100,resolution=50,thresh=10,file_location='C:\\Users\\natha\\OneDrive\\Desktop\\CSULB\\kinetoplast\\',use_prev_file=''):
    kp=hkinetoplast(columns,rows)
    date=strftime("%Y-%m-%d %H:%M:%S", localtime())[0:10].replace('-','')
    excel_name_base=date+'_RKP_NM_hexagonalGrid_sat'+str(boundary_sat+1)
    #All files from this run will go into a folder. If a folder of the same name already esitss, make a new one.
    if not os.path.exists(file_location+excel_name_base):
        os.makedirs(file_location+excel_name_base)
    else:
        k=1
        while os.path.exists(file_location+excel_name_base+'_ind'+str(k)):
            k+=1
        excel_name_base+='_ind'+str(k)
        os.makedirs(file_location+excel_name_base)
    kp=hkinetoplast(columns,rows,file_location=file_location+excel_name_base)
    if boundary_sat>0:
        #Do that
        kp.add_boundary(boundary_sat)
    #If we are using the same model, with random elements held fixed, as in another run, pull the numpy grid, networkx grid, and adjacency matrix from the previous file. Add these to the existing file, too, and update the kinetoplast object
    if use_prev_file!='':
        cgg,cidm,ckpn=load_graph(file_location+use_prev_file)
        serialize_graph(cgg,cidm,ckpn,file_location+excel_name_base)
        kp.grid=cgg
        kp.idm=cidm
        kp.kpn=deepcopy(ckpn)
    #If this is a fresh graph, compile it, export the graph objects, and make a deep copy of kpn so it can be repeatedly dissolved without needed recompilation
    else:
        kp.compile_graph()
        ckpn=deepcopy(kp.kpn)
        serialize_graph(kp.grid,kp.idm,ckpn,file_location+excel_name_base)
    #Do this as many times as the user requests
    for i in range(iterations):
        #Generate the output file name
        excel_name=excel_name_base+'_iter'+str((i+1))
        if i==0 or i==1:
            kp.dissolve_with_pics(resolution,thresh,excel_name,auto_name=False,picStep=500)
        else:
            kp.dissolve(resolution,thresh,excel_name,auto_name=False)
        kp.kpn=deepcopy(ckpn)
    ct=compTracker(file_location+excel_name_base,autogenFolder=True,thresh=0)
    ct.plotLargestComp()
    ct.plotSecondLargestComp()
    ct.export_data(outfolder='C:\\Users\\natha\\OneDrive\\Desktop\\CSULB\\kinetoplast\\to_aggregate\\',extraName='_'+excel_name_base)
    freadme=open(file_location+excel_name_base+'\\readme.txt','w')
    freadme.write("Date: "+strftime("%Y-%m-%d %H:%M:%S", localtime())[0:10]+'\n')
    freadme.write("Type: Hexagonal\n")
    freadme.write("Number of nodes: "+str(ckpn.number_of_nodes())+'\n')
    freadme.write("Rows: "+str(kp.xdim)+'\n')
    freadme.write("Columns: "+str(kp.ydim)+'\n')
    freadme.write("Probability field radius: "+str(kp.rad)+'\n')
    freadme.write("Average degree: "+str(kp.avg_deg())+'\n')
    freadme.write("Boundary saturation: "+str(kp.sat)+'\n')
    freadme.write("Number of maxicircles: "+str(kp.amount)+str('\n'))
    freadme.write('Maxicircle radius: '+str(kp.maxi_rad))
    freadme.close()
    return

def run_kinetoplast_search(rows=10, columns=10, boundary_sat=0,iterations=100,resolution=50,thresh=10,rad=0.95,file_location='C:\\Users\\natha\\OneDrive\\Desktop\\CSULB\\kinetoplast\\',use_prev_file=''):
    kp=kinetoplast(columns,rows,rad,file_location=file_location)
    #Gather start time of computation
    start=time()
    date=strftime("%Y-%m-%d %H:%M:%S", localtime())[0:10].replace('-','')
    excel_name_base=date+'_RKP_NM_randomGrid_sat'+str(boundary_sat+1)
    #All files from this run will go into a folder. If a folder of the same name already esitss, make a new one.
    if not os.path.exists(file_location+excel_name_base):
        os.makedirs(file_location+excel_name_base)
    else:
        k=1
        while os.path.exists(file_location+excel_name_base+'_ind'+str(k)):
            k+=1
        excel_name_base+='_ind'+str(k)
        os.makedirs(file_location+excel_name_base)
    kp=hkinetoplast(columns,rows,file_location=file_location+excel_name_base)
    if boundary_sat>0:
        #Do that
        kp.add_boundary(boundary_sat)
    #If we are using the same model, with random elements held fixed, as in another run, pull the numpy grid, networkx grid, and adjacency matrix from the previous file. Add these to the existing file, too, and update the kinetoplast object
    if use_prev_file!='':
        cgg,cidm,ckpn=load_graph(file_location+use_prev_file)
        serialize_graph(cgg,cidm,ckpn,file_location+excel_name_base)
        kp.grid=cgg
        kp.idm=cidm
        kp.kpn=deepcopy(ckpn)
    #If this is a fresh graph, compile it, export the graph objects, and make a deep copy of kpn so it can be repeatedly dissolved without needed recompilation
    else:
        kp.compile_graph()
        ckpn=deepcopy(kp.kpn)
        serialize_graph(kp.grid,kp.idm,ckpn,file_location+excel_name_base)
    #Do this as many times as the user requests
    for i in range(iterations):
        #Generate the output file name
        excel_name=excel_name_base+'_iter'+str((i+1))
        if i==0 or i==1:
            kp.dissolve_with_pics(resolution,thresh,excel_name,auto_name=False,picStep=500)
        else:
            kp.dissolve(resolution,thresh,excel_name,auto_name=False)
        kp.kpn=deepcopy(ckpn)
    ct=compTracker(file_location+excel_name_base,autogenFolder=True,thresh=0)
    ct.plotLargestComp()
    ct.plotSecondLargestComp()
    ct.export_data(outfolder='C:\\Users\\natha\\OneDrive\\Desktop\\CSULB\\kinetoplast\\to_aggregate\\',extraName='_'+excel_name_base)
    freadme=open(file_location+excel_name_base+'\\readme.txt','w')
    freadme.write("Date: "+strftime("%Y-%m-%d %H:%M:%S", localtime())[0:10]+'\n')
    freadme.write("Type: Random\n")
    freadme.write("Number of nodes: "+str(ckpn.number_of_nodes())+'\n')
    freadme.write("Rows: "+str(kp.xdim)+'\n')
    freadme.write("Columns: "+str(kp.ydim)+'\n')
    freadme.write("Probability field radius: "+str(kp.rad)+'\n')
    freadme.write("Average degree: "+str(kp.avg_deg())+'\n')
    freadme.write("Boundary saturation: "+str(kp.sat)+'\n')
    if kp.reg and kp.ringed:
        freadme.write("Boundary type: Ringed\n")
    elif kp.reg:
        freadme.write("Boundary type: Regular\n")
    else:
        freadme.write("Boundary type: Random\n")
    freadme.write("Number of maxicircles: "+str(kp.amount)+str('\n'))
    freadme.write('Maxicircle radius: '+str(kp.maxi_rad))
    freadme.close()
    return
        
        

def serialize_graph(gg,idm,kpn,folder):
    f=open(folder+"\\grid.txt",'wb')
    pickle.dump(gg,f)
    f.close()
    del f
    #f=open(folder+"\\kpg.txt",'wb')
    #pickle.dump(kpg,f)
    #f.close()
    #del f
    f=open(folder+"\\idm.txt",'wb')
    pickle.dump(idm,f)
    f.close()
    del f
    f=open(folder+"\\kpn.txt",'wb')
    pickle.dump(kpn,f)
    f.close()
    del f
    return

def load_graph(folder):
    f=open(folder+"\\grid.txt",'rb')
    gg=pickle.load(f)
    f.close()
    del f
    #f=open(folder+"\\kpg.txt",'rb')
    #kpg=pickle.load(f)
    #f.close()
    #del f
    f=open(folder+"\\idm.txt",'rb')
    idm=pickle.load(f)
    f.close()
    del f
    f=open(folder+"\\kpn.txt",'rb')
    kpn=pickle.load(f)
    f.close()
    del f
    return gg,idm,kpn

if __name__=="__main__":
    for sat in range(5,21):
        start=time()
        run_hkinetoplast_search(rows=100, columns=100, boundary_sat=sat,iterations=100,resolution=50,thresh=50,file_location='C:\\Users\\natha\\OneDrive\\Desktop\\CSULB\\kinetoplast\\',use_prev_file='')
        end=time()
        print("Saturation "+str(sat)+" complete; time taken: "+str(timedelta(seconds=(end-start))))

    for sat in range(0,21):
        start=time()
        run_kinetoplast_search(rows=71, columns=71, boundary_sat=sat,iterations=100,resolution=50,thresh=50,file_location='C:\\Users\\natha\\OneDrive\\Desktop\\CSULB\\kinetoplast\\',use_prev_file='')
        end=time()
        print("Saturation "+str(sat)+" complete; time taken: "+str(timedelta(seconds=(end-start))))
