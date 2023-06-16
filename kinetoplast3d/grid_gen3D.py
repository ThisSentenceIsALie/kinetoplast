'''
Module name: grid_gen3D.py
Author: Nathaniel Morrison
Date created: 06/22/2020
Date last modified: 07/05/2020
Python Version: 3.7.2
'''
from random import uniform
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy
import datetime
import time
import prob_funcs3D as prob_funcs

#Function to create a grid of points of size xdim x ydim x zdim. The grid will be broken up into 1x1x1 boxes, each with exactly one point randomly placed within it.
def craft_grid3D(xdim,ydim,zdim,rad):
    #Define the grid list
    grid=list()
    #Run through each plane of the grid
    for zbox in range(zdim):
        #Define and clear a list to house the plane
        plane=list()
        del plane[:]
        #Run through each row of the grid
        for ybox in range(ydim):
            #Define and clear a list to house the row
            row=list()
            del row[:]
            #Run through each column of the grid
            for xbox in range(xdim):
                #Choose a random (x,y) coordinate within the box
                xcoord=uniform(xbox,(xbox+1))
                ycoord=uniform(ybox,(ybox+1))
                zcoord=uniform(zbox,(zbox+1))
                #Add it as a tuple to the row
                row.append([(xcoord,ycoord,zcoord,rad),])
            #Add the row to the plane (as a shallow copy, for reasons that are hopefully obvious)
            plane.append(row.copy())
        #Add the plane to the grid
        grid.append(plane.copy())
    #Return the finished grid
    return grid

#Function to add maxi-circles of a given radius throughout the grid
def add_maxi_circles(grid,xdim,ydim,zdim,maxi_rad,amount):
    #Create as many maxi circles as desired
    for i in range(amount):
        #Get the coordinates
        x_coord=uniform(0,xdim)
        y_coord=uniform(0,ydim)
        z_coord=uniform(0,zdim)
        #Get the cell the coordinates live in
        xbox=int(np.floor(x_coord))
        ybox=int(np.floor(y_coord))
        zbox=int(np.floor(z_coord))
        #Add the node to the cell's list
        grid[zbox][ybox][xbox].append((x_coord,y_coord,z_coord,maxi_rad))
    return grid
    
#Function to assign each node a graph vertex index.
def node_mtx(grid):
    #Initialize the index list
    idm=deepcopy(grid)
    ind=0
    for zbox in range(len(grid)):
        #Run through each row of the grid
        for ybox in range(len(grid[zbox])):
            #Run through each cell in the row
            for xbox in range(len(grid[zbox][ybox])):
                #Run through each node in the cell
                for node in range(len(grid[zbox][ybox][xbox])):
                    #Assign the node an index, and replace the relevent entry in the index matrix with the index
                    idm[zbox][ybox][xbox][node]=ind
                    ind+=1
    return idm, ind

#Function to creates an adjacency matrix for the graph of links.
def to_graph(grid):
    #Record start time
    start=time.time()
    #Grab the index matrix, which is the grid with every entry replaced by an index integer, and number of nodes in the grid
    idm,num_nodes=node_mtx(grid)
    #Create an empty adjacency matrix
    g=np.zeros((num_nodes,num_nodes))
    #Create a dictionary to keep track of which pairs of nodes have already been processed to prevent repeat processing (which would increase the probability of links)
    already_tried=dict()
    #Run through each plane in the grid
    for zbox in range(len(grid)):
        print("Doing plane "+str(zbox))
        plane=grid[zbox]
        #Run through each row in the plane
        for ybox in range(len(plane)):
            print("Doing row "+str(ybox))
            row=plane[ybox]
            #Run through each cell in the row
            for xbox in range(len(row)):
                cell=row[xbox]
                #Run through each node in the cell
                for node in range(len(cell)):
                    #Grab the coordinates and the radius, as well as the assigned index in idm
                    cent1=cell[node][0:3]
                    rad1=cell[node][3]
                    node1_ind=idm[zbox][ybox][xbox][node]
                    #Run through every cell that might conceivably have a node within range of the current node. The exception to this is that maxi circles within range may not
                    #be checked here. But, that's ok, because they will have their own place in the sun when the outer loop reaches them
                    for adj_z in range(int(np.floor(zbox-2*rad1)),int(np.ceil(zbox+1+2*rad1)),1):
                        for adj_y in range(int(np.floor(ybox-2*rad1)),int(np.ceil(ybox+1+2*rad1)),1):
                            for adj_x in range(int(np.floor(xbox-2*rad1)),int(np.ceil(xbox+1+2*rad1)),1):
                                #Screen for negative indices and indices out of grid bounds. Also, don't check for links between nodes in the same cell and 
                                if adj_y>=0 and adj_x>=0 and adj_z>=0 and (xbox,ybox,zbox)!=(adj_x,adj_y,adj_z) and adj_z<len(grid):
                                    if adj_y<len(grid[adj_z]):
                                        if adj_x<len(grid[adj_z][adj_y]):
                                            adj_cell=grid[adj_z][adj_y][adj_x]
                                            #Run through each node in the adjacent cell
                                            for adj_node in range(len(adj_cell)):
                                                #Grab the second node's center, radius, and index
                                                cent2=adj_cell[adj_node][0:3]
                                                rad2=adj_cell[adj_node][3]
                                                node2_ind=idm[adj_z][adj_y][adj_x][adj_node]
                                                #Sort the indices. The lower-value index will always be the key in already_checked, which should minimize the number/size of needed
                                                #dictionary entries. Since thumbing through already_checked is (or, I guess, 'was' at this point) more than 50% the processing time,
                                                #minimizing the size of this object is critical to performance optimization
                                                ind_lis=[node1_ind,node2_ind]
                                                ind_lis.sort()
                                                #Enclosed in a try loop because if the lower-value node has not yet been encountered, trying to call its dictionary entry will result in an
                                                #error
                                                try:
                                                    #If the node pair has not yet been checked
                                                    if ind_lis[1] not in already_tried[ind_lis[0]]:
                                                        #Check for a link, create (or don't) the link, and add the pair to already_tried
                                                        already_tried, g=are_linked(cent1,cent2,rad1,rad2,node1_ind,node2_ind,already_tried,g)
                                                #If an error is raised, then the lower-value node has not yet been encountered, so this pair has obviously not yet been checked
                                                except:
                                                    #Check for a link, create (or don't) the link, and add the pair to already_tried
                                                    already_tried, g=are_linked(cent1,cent2,rad1,rad2,node1_ind,node2_ind,already_tried,g)
    #Display the time spent on compilation
    end=time.time()
    print("Time to compile: "+str(datetime.timedelta(seconds=(end-start))))
    return g, idm

#Function to detrmine if two nodes share a link based on their probability distribution overlap
def are_linked(cent1,cent2,rad1,rad2,node1_ind,node2_ind,already_tried,g):
    node_lis=[node1_ind,node2_ind]
    node_lis.sort()
    #Add this pair of nodes to the appropriate already_checked entry, or create said entry if it does not yet exist.
    try:
        #Note that the key will always be the lesser of the two indices
        already_tried[node_lis[0]].append(node_lis[1])
    except:
        already_tried[node_lis[0]]=[node_lis[1],]
    d=np.sqrt((cent1[0]-cent2[0])**2+(cent1[1]-cent2[1])**2+(cent1[2]-cent2[2])**2)
    #This is here to guarentee that maxi circles connect to everything touching their circumference
    if rad1!=rad2 and d>=abs(rad1-rad2) and d<=(rad1+rad2):
        g[node1_ind][node2_ind]=1
        g[node2_ind][node1_ind]=1
    #And maxi circles do not connect to anything else
    elif rad1!=rad2:
        pass
    #Run the prob_funcs function that randomizes the existance of a link between the kDNA loops based on the prob distribution function
    elif prob_funcs.are_linked(cent1,cent2,rad1,rad2):
        #If there is a link, mark down the existance of an edge in the adjacency matrix
        g[node1_ind][node2_ind]=1
        g[node2_ind][node1_ind]=1
    return already_tried,g

def graphite_grid(xdim,ydim,zdim):
    spacing=1
    grid=list()
    del grid[:]
    #Run through each layer in the grid
    for z in range(zdim):
        plane=list()
        del plane[:]
        #Run through each row the user wants to generate. Each row is effectively two, one for each sub-lattice, so only iterate over 1/2 the height
        for y in range(int(ydim/2)):
            row=list()
            del row[:]
            #Run through the nodes the user wants to be in each row. Two nodes are added per iteration, one for each sub-lattice, so halve the number of iterations
            for x in range(int(xdim/2)):
                #If we are on an even row
                if y%2==0:
                    #Don't do this for the first column in order to ensure the grid has "even" sides
                    if x!=0:
                        #Add the coordiantes of the node to the grid. The bottom-left point will be at (0.5,0.5). After this, nodes are spaced as equilateral triangles
                        #The plane's z and y coordinates will also all be shifted every other plane, hence the z%2 terms
                        row.append([(0.5+spacing*x+(0.5*spacing*(z%2)),0.5+y*spacing*(np.sqrt(3)/2)+(np.sqrt(1/12)*spacing*(z%2)),z,1),])
                    #Add the corresponding point in the other sub-lattice, with x-coordinate increased by 0.5*spacing and y coordinate increased by sqrt(1/12)*spacing
                    row.append([(0.5+0.5*spacing+spacing*x+(0.5*spacing*(z%2)),0.5+np.sqrt(1/12)*spacing+y*spacing*(np.sqrt(3)/2)+(np.sqrt(1/12)*spacing*(z%2)),z,1),])
                #If we are in an odd row
                else:
                    #The row's x-position has to be shifted by 1/2 the spacing to create a triangular grid
                    row.append([(0.5+spacing*x+spacing/2+(0.5*spacing*(z%2)),0.5+y*spacing*(np.sqrt(3)/2)+(np.sqrt(1/12)*spacing*(z%2)),z,1),])
                    #Don't do this for the last column in order to ensure the grid has "even" sides
                    if x!=(int(xdim/2)-1):
                        #Add the corresponding point in the other sub-lattice, with x-coordinate increased by 0.5*spacing and y coordinate increased by sqrt(1/12)*spacing
                        row.append([(0.5+0.5*spacing+spacing*x+spacing/2+(0.5*spacing*(z%2)),0.5+np.sqrt(1/12)*spacing+y*spacing*(np.sqrt(3)/2)+(np.sqrt(1/12)*spacing*(z%2)),z,1),])
            #Add the row to the grid
            plane.append(row.copy())
        grid.append(plane.copy())
    #Return the grid
    return tuple(grid)

#Function to compute Cartesian distance in R3
def dist(cent1,cent2):
    return np.sqrt((cent1[0]-cent2[0])**2+(cent1[1]-cent2[1])**2+(cent1[2]-cent2[2])**2)

#Function to convert a graphite grid into an adjacency matrix and index matrix. Different from to_graph because I can assume some things that significantly reduce computation
#time in a graphite grid
def to_graph_graphite(grid):
    #Record start time
    start=time.time()
    #Grab the index matrix, which is the grid with every entry replaced by an index integer, and number of nodes in the grid
    idm,num_nodes=node_mtx(grid)
    #Create an empty adjacency matrix
    g=np.zeros((num_nodes,num_nodes))
    #Run through each node in the grid
    for zbox in range(len(grid)):
        #Create variable to keep track of which nodes have been linked to the upper vs the lower plane
        last_connect=int((-1)**(zbox+1))
        for ybox in range(len(grid[zbox])):
            for xbox in range(len(grid[zbox][ybox])):
                for node in range(len(grid[zbox][ybox][xbox])):
                    #Get its coordinates and index
                    stuff=grid[zbox][ybox][xbox][node]
                    coords=stuff[0:3]
                    rad=stuff[3]
                    node_ind=idm[zbox][ybox][xbox][node]
                    aligned_node=False
                    connection_made=False
                    #Run through the two next-nearest planes
                    for adj_z in range(int(zbox-(rad-1)),int((zbox+2)*rad),1):
                        #Run through the two next-nearest rows
                        for adj_y in range(int((ybox-1*rad)),int((ybox+2*rad)),1):
                            #Run through the four nodes in these rows to the left and the right of the primary node, plus nodes with the same xbox
                            for adj_x in range(int(xbox-1*rad),int(xbox+3*rad),1):
                                #Screen for nonexistant planes/rows/nodes, and make sure we aren't looking fro a connect from a node to itself
                                if adj_z>=0 and adj_y>=0 and adj_x>=0 and adj_z<len(grid) and adj_y<len(grid[adj_z]) and adj_x<len(grid[adj_z][adj_y])and (adj_x,adj_y,adj_z)!=(xbox,ybox,zbox):
                                    #Run through each node in the adjacent box
                                    for adj_node in range(len(grid[adj_z][adj_y][adj_x])):
                                        #Grab its coordinates
                                        adj_stuff=grid[adj_z][adj_y][adj_x][adj_node]
                                        adj_coords=adj_stuff[0:3]
                                        adj_rad=adj_stuff[3]
                                        #If the two nodes are nearest-neighbors (hexagon edges are equal to sqrt(1/3)*spacing. Next-nearest neighbors are [spacing] apart.
                                        if dist(coords,adj_coords)<=float(np.sqrt(2/3)):
                                            #Grab the adjacent node's index and add a connection
                                            adj_ind=idm[adj_z][adj_y][adj_x][adj_node]
                                            g=graphite_add_connection(g,node_ind,adj_ind)
                                        #If the adjacent node has the same (or close enough to the same) x/y (but not z) coordinates as the primary node
                                        elif abs(coords[0]-adj_coords[0])<=0.1 and abs(coords[1]-adj_coords[1])<=0.1:
                                            #Note that the primary node is an "aligned node", with another node in a different plane aligned with it
                                            aligned_node=True
                                            #Determine the direction of the adjacent node relative to the primary node; '1'=up,'-1'=down
                                            direction=adj_coords[2]-coords[2]
                                            #If the last node to be linked to another layer pointed in the opposite direction
                                            if last_connect!=direction:
                                                #Add a connection
                                                adj_ind=idm[adj_z][adj_y][adj_x][adj_node]
                                                g=graphite_add_connection(g,node_ind,adj_ind)
                                                #Note the fact that a connection has been made between this node and an extra-planar node
                                                connection_made=True
                                        elif rad>1 and (dist(coords,adj_coords)-adj_rad)<=rad and (dist(coords,adj_coords)+adj_rad)>=rad:
                                            #Grab the adjacent node's index and add a connection
                                            adj_ind=idm[adj_z][adj_y][adj_x][adj_node]
                                            g=graphite_add_connection(g,node_ind,adj_ind)
                                    if connection_made:
                                        #Invert last_connect, since this connection is pointing in the opposite direction to the previous one
                                        last_connect=int((-1)*last_connect)
                                    
                    #If the primary node is an aligned node but no connection was made...
                    if aligned_node and not connection_made:
                        #Then we are on either the first or last plane. No connection was made because there is no plane below/above, respectively. Invert last_connect so the
                        #next aligned node does connect with something
                        last_connect=int((-1)*last_connect)
    #Display the time spent on compilation
    print("Time to compile: "+str(datetime.timedelta(seconds=(time.time()-start))))
    return g, idm

#Function to add an edge to the adjacency matrix of a hexagonal grid                 
def graphite_add_connection(g,node_ind,adj_ind):
    g[node_ind][adj_ind]=1
    g[adj_ind][node_ind]=1
    return g

#Function to plot the grid for you viewing pleasure
def grid_visualizer(grid):
    #Create seperate lists for all the x coords and all the y coords, with the indices of each list coinciding
    x=list()
    y=list()
    color_lis=('b','r','g','o')
    col=0
    for plane in grid:
        del x[:]
        del y[:]
        #Run through each row
        for row in plane:
            #Run through each cell in the row
            for el in row:
                #Run through each node in the cell, and add its coordinates to the respective lists
                for sub_el in el:
                    x.append(sub_el[0])
                    y.append(sub_el[1])
        #Create a scatter plot of the points
        plt.scatter(x,y,c=color_lis[col])
        col+=1
    #Create axes
    #plt.axis([0.0,600.0, 10000.0,20000.0])
    #Define the axes as objects
    #ax = plt.gca()
    #Turn off autoscaling, since it will try to only show one section of the plot otherwise
    #ax.set_autoscale_on(False)
    #Force the full range and domain of the grid to be plotted
    #ax.set_xlim([0,len(grid[1])])
    #ax.set_ylim([0,len(grid)])
    #Show the plot
    plt.show()
    return

#Function to figure out where in the graphite grid list to put a maxi circle
def find_box(x,y,z,spacing):
    #The zbox (the plane) is just the floor of the z-coordinate
    zbox=int(np.floor(z))
    #There are four options for the y-box (row). These come from the possible y-coordinates of grid node nearest to the maxi circle
    yi0=int(np.ceil((y-0.5-np.sqrt(1/12)*spacing-np.sqrt(1/12)*(zbox%2))/(np.sqrt(3)/2*spacing)))
    yi1=int(np.floor((y-0.5-np.sqrt(1/12)*spacing-np.sqrt(1/12)*(zbox%2))/(np.sqrt(3)/2*spacing)))
    yi2=int(np.ceil((y-0.5-np.sqrt(1/12)*(zbox%2))/(np.sqrt(3)/2*spacing)))
    yi3=int(np.floor((y-0.5-np.sqrt(1/12)*(zbox%2))/(np.sqrt(3)/2*spacing)))
    #Determine the distance between each of these possibilities and the actual maxi circle location
    ydists=[(abs(yi0-y),yi0),(abs(yi1-y),yi1),(abs(yi2-y),yi2),(abs(yi3-y),yi3)]
    #Sort them in ascending order by the first value in the two-tuple (that being the distance between the ybox and actual y-position)
    ydists.sort()
    #Run through each of the elements in the list
    for el in ydists:
        #As long as the ybox is valid, e.g. positive
        if el[1]>=0:
            #Then the first element in the list that satisfies this condition is the closest ybox
            ybox=el[1]
            break
    #Do the same as the above, but with the x-coordinate to get the xbox
    xi0=int(np.ceil((x-0.5-0.5*spacing-0.5*spacing*(zbox%2))/spacing))
    xi1=int(np.floor((x-0.5-0.5*spacing-0.5*spacing*(zbox%2))/spacing))
    xi2=int(np.ceil((x-0.5-0.5*spacing*(zbox%2))/spacing))
    xi3=int(np.floor((x-0.5-0.5*spacing*(zbox%2))/spacing))
    xdists=[(abs(xi0-x),xi0),(abs(xi1-x),xi1),(abs(xi2-x),xi2),(abs(xi3-x),xi3)]
    xdists.sort()
    for el in xdists:
        if el[1]>=0:
            xbox=el[1]
            break
    return xbox,ybox,zbox

#Function to add maxi circles to a graphite grid
def graphite_maxi_circles(grid,maxi_rad,maxi_amount,xdim,ydim,zdim):
    #Manually define the spacing
    spacing=1
    #Grab the largest values of the iterators used to craft the grid
    xr=int(xdim/2)-1
    yr=int(ydim/2)-1
    zr=zdim-1
    #Determine the min/max values of the x,y, and z coordinates of nodes in the grid
    xmin=0.5+0.5*spacing
    xmax=0.5+0.5*spacing+spacing*xr+0.5*spacing+0.5*spacing
    ymin=0.5
    ymax=0.5+np.sqrt(1/12)*spacing+yr*spacing*(np.sqrt(3)/2)+(np.sqrt(1/12)*spacing)
    xmin=0
    zmax=zr
    #Generate as many maxi circles as the user wants
    for i in range(maxi_amount):
        #Generate a random coordinate/radius tuple somewhere within the grid
        node=(uniform(xmin,xmax),uniform(ymin,ymax),uniform(0,zmax),maxi_rad)
        #Determine the box this new node is closest to
        xbox,ybox,zbox=find_box(node[0],node[1],node[2],spacing)
        #Add it to the grid
        grid[zbox][ybox][zbox].append(node)
    return grid

#Function to supersaturate a graphite grid boundary with non-random node placement. New nodes will be placed directly atop the first node, will connect to everything the first
#node connects to (and nothing more), and will not connect to other nodes in the same position
def graphite_boundary(grid,sat):
    #Run through every plane. Each plane has a super-saturated boundary; the top/bottom planes are not special
    for plane in range(len(grid)):
        #Run through the top and bottom rows
        for row in (0,(len(grid[plane])-1)):
            #Run through each point in these rows
            for node in range(len(grid[plane][row])):
                #Both subrows in these two superrows are boundary rows. So, duplicate each node
                for i in range(sat):
                    grid[plane][row][node].append(grid[plane][row][node][0])
        #Run through all the other rows
        for row in range(1,(len(grid[plane])-1),1):
            #Run through the first two and last two nodes in these rows
            for node in (0,1,(len(grid[plane][row])-2),(len(grid[plane][row])-1)):
                #These are boundary nodes. So, duplicate them
                for i in range(sat):
                    grid[plane][row][node].append(grid[plane][row][node][0])
    return grid

