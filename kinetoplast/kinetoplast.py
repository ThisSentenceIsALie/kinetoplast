'''
Class name: kinetoplast.py
Author: Nathaniel Morrison
Date created: 05/23/2020
Date last modified: 01/12/2023
Python Version: 3.11.1
'''
import grid_gen as gg
import prob_funcs
import graph_funcs as gf
import networkx as nx
import bf_search as bf
import dissolusion_plot as dp
import numpy as np
import os

#Class defining the kinetoplast object. This should let you have multiple kinetoplasts simulants running around at once. Maybe one day they'll even interact with eachother.
class kinetoplast:
    #Object instantiates with a base grid of the given dimensions and probability field radius. The adjacency matrix and network just have placeholder values
    def __init__(self,xdim,ydim,rad,flag_bound=False,file_location='C:\\Users\\natha\\OneDrive\\Desktop\\CSULB\\kinetoplast'):
        self.xdim=xdim
        self.ydim=ydim
        self.rad=rad
        self.grid=gg.craft_grid(xdim,ydim,rad)
        self.kpg=list()
        self.kpn=''
        self.idm=list()
        self.maxi=False
        self.supersat=False
        self.reg=False
        self.ringed=False
        self.flag_bound=flag_bound
        self.sat=1
        self.maxi_rad='N/A'
        self.amount=0
        if file_location[-1]!="\\":
            file_location+="\\"
        self.file_location=file_location

    #Method to add extra nodes in the boundary cells BEYOND the usual one
    def add_boundary(self,saturation,reg=False):
        self.supersat=True
        self.reg=reg
        #The boundary can be a random placement of more nodes in each boundary cell or a stacking of additional nodes directly atop the first one
        if reg:
            self.grid=gg.add_reg_boundary(self.grid,saturation)
        else:
            self.grid=gg.add_boundary(self.grid,self.xdim,self.ydim,self.rad,saturation)

    #Method to sprinkle maxi circles of a given radius and number throughout the grid
    def add_maxi_circles(self, maxi_rad, amount):
        self.maxi_rad=maxi_rad
        self.amount=amount
        self.grid=gg.add_maxi_circles(self.grid,self.xdim,self.ydim,maxi_rad,amount)

    #Method to compile the current grid into an adjacency matrix and networkx graph object
    def compile_graph(self,ringed=False):
        self.maxi=True
        self.ringed=ringed
        self.kpg, idm =gg.to_graph(self.grid,ringed)
        self.kpn=gf.to_network(self.kpg, self.grid,idm)

    #Debug method. Uses an algebraic circle intersect formula for diagnosing problems with the integrator
    def compile_graph_alg(self):
        self.kpg, idm =gg.to_graph_alg(self.grid)
        self.kpn=gf.to_network(self.kpg, self.grid,idm)

    #Method to plot the grid, with no connections between nodes. Will pop up a pyplot figure in a seperate window
    def plot_grid(self):
        gg.grid_visualizer(self.grid)

    #Method to plot the graph, with connections between nodes. Will pop up a pyplot figure in a seperate window
    def plot_graph(self):
        gf.graph_visualizer(self.kpn)

    #Method to find the minimum degree in the graph
    def min_deg(self):
        return gf.min_deg(self.kpn)

    #Method to find the average degree in the graph
    def avg_deg(self):
        return gf.avg_deg(self.kpn)

    def _makeDirectories(self):
        if not os.path.exists(self.file_location+'data\\'):
            os.makedirs(self.file_location+'data\\')
        if not os.path.exists(self.file_location+'pics\\'):
            os.makedirs(self.file_location+'pics\\')
        return

    #Method to run a dissolution search on the current kpn graph object. Will spit out the excel datafiles and a dissolution plot for each 
    def dissolve(self, resolution, thresh, excel_name,auto_name=True):
        if auto_name:
            if self.supersat and self.maxi:
                excel_name+='_maxiSat'
            elif self.supersat:
                excel_name+='_sat'
            elif self.maxi:
                excel_name+='_maxi'
            else:
                excel_name+='_base'
        self._makeDirectories()
        results=bf.bf_search(resolution,self.kpn,thresh)
        bf.excel_io(results,resolution, self.file_location+'data\\'+excel_name)
        dp.module_main(self.file_location+'pics\\'+excel_name, self.file_location+'data\\'+excel_name)

    #Method to run a dissolution search and output component plots at the given predetermined critical points
    def dissolve_with_pics(self, resolution, thresh, excel_name,auto_name=True,picStep=500):
        if auto_name:
            if self.supersat and self.maxi:
                excel_name+='_maxiSat'
            elif self.supersat:
                excel_name+='_sat'
            elif self.maxi:
                excel_name+='_maxi'
            else:
                excel_name+='_base'
        nodenum=self.kpn.number_of_nodes()
        crit_points=list(np.linspace(0,int(nodenum-nodenum%picStep),num=int((nodenum-nodenum%picStep)/picStep+1),dtype=int))+[nodenum,]
        self._makeDirectories()
        path=self.file_location+'pics\\'+excel_name+"_componentPlots\\"
        results=bf.bf_search_with_pics(resolution,self.kpn,thresh,crit_points,path)
        bf.excel_io(results,resolution, self.file_location+'data\\'+excel_name)
        dp.module_main(self.file_location+'pics\\'+excel_name, self.file_location+'data\\'+excel_name)

    #Method to run a dissolution search and record when the boundary lyses
    def dissolve_flag_bound(self, resolution, thresh, excel_name):
        if self.supersat and self.maxi:
            excel_name+='_maxiSat'
        elif self.supersat:
            excel_name+='_sat'
        elif self.maxi:
            excel_name+='_maxi'
        else:
            excel_name+='_base'
        self._makeDirectories()
        results=bf.bf_search_flag_bound(resolution,self.kpn,thresh,self.sat)
        bf.excel_io(results,resolution, self.file_location+'data\\'+excel_name)
        dp.module_main(self.file_location+'pics\\'+excel_name,self.flag_bound, self.file_location+'data\\'+excel_name)
    


    
