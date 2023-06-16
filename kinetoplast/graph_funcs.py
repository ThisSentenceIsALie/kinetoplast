'''
Module name: graph_funcs.py
Author: Nathaniel Morrison
Date created: 05/24/2020
Date last modified: 08/30/2020
Python Version: 3.7.2
'''
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

#Function to turn the grid and adjacency matrix into a networkx graph object
def to_network(adj_mtx,grid,idm, flag_bound=False):
    #Create an empty graph object
    G=nx.Graph()
    #Add every center as a node in the graph
    G.add_nodes_from(range((len(adj_mtx))))
    cell_num=0
    #Run through each row in the grid
    for ybox in range(len(grid)):
        #Run through each cell in the row
        for xbox in range(len(grid[ybox])):
            #Run through each node in the cell
            cell=grid[ybox][xbox]
            bound_cell=False
            cell_num+=1
            for node in range(len(cell)):
                #Grab the node's assigned index
                node_ind=idm[ybox][xbox][node]
                coords=cell[node]
                #Assign the center's node the coordinates in the grid
                G.nodes[node_ind]['Coords']=coords
                #If we're flagging the boundary
                if flag_bound:
                    #If the last entry in the node tuple flags this as a boundary cell
                    if coords[-1]==True:
                        #Flag this as a boundary cell
                        bound_cell=True
                    #If the first node in this cell was flagged as a boundary, thereby flagging the whole stack as a boundary
                    if bound_cell:
                        #Give the node a 'Bound?' property with a value of True
                        G.nodes[node_ind]['Bound?']=True
                        #Assign the stack/box in which this node lives a unique "Cell" number to identify it with other nodes in the same boundary cell
                        G.nodes[node_ind]['Cell']=cell_num
                    else:
                        #Give it a value of False to maintain consistancy across all nodes
                        G.nodes[node_ind]['Bound?']=False
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

#Function to export a component plot mid-dissolution
def export_graph_pic(G,dissolutions,path):
    #Create a position dictionary, with node indices as keys and node coordinates as entries
    pos_dict=dict()
    for node in G.nodes:
        pos_dict[node]=G.nodes[node]['Coords']
    #Create an empty matplotlib figure
    fig = plt.figure(figsize=(13.333,10))
    #Draw the nodes with nx's built-in function. The function uses matplotlib to do the actual rendering, but I have a feeling it's more optimized than my code
    nx.draw_networkx_nodes(G,pos=pos_dict,node_size=5)
    #Theoretically, nx's built-in function to plot edges, nx.draw_networkx_edges(G,pos=pos_dict), should do this, but matplotlib raises an error when I try to use that.
    #So, do this part manually.
    for edge in G.edges:
        link_x=(pos_dict[edge[0]][0],pos_dict[edge[1]][0])
        link_y=(pos_dict[edge[0]][1],pos_dict[edge[1]][1])
        plt.plot(link_x,link_y,'.b-', linewidth=1, markersize=5)
    #Add the title to the figure
    fig.suptitle(('KP Model After '+str(dissolutions)+ ' Dissolutions'), fontsize=20)
    #Save the figure with 300 dots per inch
    fig.savefig(path+'after'+str(dissolutions)+'dissolutions_componentPlot.png',dpi=300)
    #Clear the figure so it dosen't interfere with the next one when it is created
    plt.clf()
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
