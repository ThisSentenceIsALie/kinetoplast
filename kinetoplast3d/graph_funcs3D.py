'''
Module name: graph_funcs3D.py
Author: Nathaniel Morrison
Date created: 06/27/2020
Date last modified: 07/01/2020
Python Version: 3.7.2
'''
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

#Function to turn the grid and adjacency matrix into a networkx graph object
def to_network(adj_mtx,grid,idm):
    #Create an empty graph object
    G=nx.Graph()
    #Add every center as a node in the graph
    G.add_nodes_from(range((len(adj_mtx))))
    for zbox in range(len(grid)):
        #Run through each row in the grid
        for ybox in range(len(grid[zbox])):
            #Run through each cell in the row
            for xbox in range(len(grid[zbox][ybox])):
                #Run through each node in the cell
                cell=grid[zbox][ybox][xbox]
                for node in range(len(cell)):
                    #Grab the node's assigned index
                    node_ind=idm[zbox][ybox][xbox][node]
                    #Assign the center's node the coordinates in the grid
                    G.nodes[node_ind]['Coords']=cell[node]
                    #Find all vertices the current node is already linked to
                    cur_neighbors=nx.neighbors(G,node_ind)
                    #Run through the node's row in the adjacency matrix
                    for ind2 in range(len(adj_mtx[node_ind])):
                        #If there is not already an edge connecting the two nodes and the adjacency matrix says there should be
                        if ind2 not in cur_neighbors and adj_mtx[node_ind][ind2]==1:
                            #Add an edge
                            G.add_edge(node_ind,ind2)
    return G

#Function to plot a graph version of the kinetoplast model
def graph_visualizer(kpn):
    #Run throughe each edge
    for edge in kpn.edges:
        #Extract the coordinates of its two endpoints and plot them with a line connecting them
        link_x=(kpn.nodes[edge[0]]['Coords'][0],kpn.nodes[edge[1]]['Coords'][0])
        link_y=(kpn.nodes[edge[0]]['Coords'][1],kpn.nodes[edge[1]]['Coords'][1])
        plt.plot(link_x,link_y,'.b-')
    x=list()
    y=list()
    #Run through each node
    for node in kpn.nodes:
        try:
            #Collect their coordinates
            x.append(kpn.nodes[node]['Coords'][0])
            y.append(kpn.nodes[node]['Coords'][1])
        except:
            print(node)
    #Plot them all
    plt.scatter(x,y)
    #Display the plot
    plt.show()
    return

#Function to compute average degree of the graph
def avg_deg(G):
    #Get a list of two-tuples, first element being a node index and second being its degree
    lis=tuple(G.degree())
    #Extract all the degrees
    n=1
    degs=[x[n] for x in lis]
    #Return the average of this list
    return sum(degs)/len(degs)

#Function to compute minimum degree of the graph
def min_deg(G):
    #Get a list of two-tuples, first element being a node index and second being its degree
    lis=tuple(G.degree())
    #Extract all the degrees
    degs=[x[1] for x in lis]
    #Sort it in ascending order
    degs.sort()
    #Return the smallest value in this list
    return degs[0]
