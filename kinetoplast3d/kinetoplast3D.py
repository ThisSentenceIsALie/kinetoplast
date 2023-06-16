'''
Class name: kinetoplast3D.py
Author: Nathaniel Morrison
Date created: 05/23/2020
Date last modified: 01/16/2023
Python Version: 3.11.1
'''
import grid_gen3D as gg
import prob_funcs3D
import graph_funcs3D as gf
import networkx as nx
import bf_search3D as bf
import dissolusion_plot3D as dp
import os

#Class defining the 3D kinetoplast object. This should let you have multiple kinetoplasts simulants running around at once. Maybe one day they'll even interact with eachother.
class kinetoplast3D:
    #Object instantiates with a base grid of the given dimensions and probability field radius. The adjacency matrix and network just have placeholder values
    def __init__(self,xdim,ydim,zdim,rad):
        self.xdim=xdim
        self.ydim=ydim
        self.zdim=zdim
        self.rad=rad
        self.grid=gg.craft_grid3D(xdim,ydim,zdim,rad)
        self.kpg=list()
        self.kpn=''
        self.idm=list()
        self.maxi=False
        self.supersat=False
        self.flag_bound=flag_bound
        self.sat=1
        self.maxi_rad='N/A'
        self.amount=0
        if file_location[-1]!="\\":
            file_location+="\\"
        self.file_location=file_location

    #Method to add extra nodes in the boundary cells BEYOND the usual one !!!!!!!!!!NOT YET IMPLEMENTED!!!!!!!!!!!!
    def add_boundary(self,saturation):
        self.supersat=True
        self.grid=gg.add_boundary(self.grid,self.xdim,self.ydim,self.rad,saturation)
        self.sat+=saturation
        
    #Method to sprinkle maxi circles of a given radius and number throughout the grid
    def add_maxi_circles(self, maxi_rad, amount):
        self.maxi_rad=maxi_rad
        self.amount=amount
        self.maxi=True
        self.grid=gg.add_maxi_circles(self.grid,self.xdim,self.ydim,self.zdim,maxi_rad,amount)

    #Method to compile the current grid into an adjacency matrix and networkx graph object
    def compile_graph(self):
        self.kpg, idm =gg.to_graph(self.grid)
        self.kpn=gf.to_network(self.kpg, self.grid,idm)

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

    ##Method to run a dissolution search on the current kpn graph object. Will spit out the excel datafiles and a dissolution plot for each 
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
    

