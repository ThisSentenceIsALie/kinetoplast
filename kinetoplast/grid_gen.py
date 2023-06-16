'''
Module name: grid_gen.py
Author: Nathaniel Morrison
Date created: 05/21/2020
Date last modified: 08/30/2020
Python Version: 3.7.2
'''
from random import uniform
import numpy as np
import matplotlib.pyplot as plt
import prob_funcs
from copy import deepcopy
import datetime
import time

#Function to create a grid of points of size xdim x ydim. The grid will be broken up into 1x1 squares, and each square will have exactly one point randomly placed within it.
def craft_grid(xdim,ydim,rad,flag_bound=False):
    #Define the grid list
    grid=list()
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
            #If the boundary nodes need to be flagged
            if flag_bound:
                #Flag the nodes in the boundary cells with a fourth tuple entry of "True" and all other nodes with a fourth tupe lentry of "False"
                if ybox==0 or xbox==0 or ybox==(ydim-1) or xbox==(xdim-1):
                    row.append([(xcoord,ycoord,rad,True),])
                else:
                    row.append([(xcoord,ycoord,rad,False),])
            else:
                #Add it as a tuple to the row
                row.append([(xcoord,ycoord,rad),])
        #Add the row to the grid (as a shallow copy, for reasons that are hopefully obvious)
        grid.append(row.copy())
    #Return the finished grid
    return grid

#Function to super-saturate the grid boundary with 10 nodes per cell
def add_boundary(grid,xdim,ydim,rad,saturation,flag_bound=False):
    #Run through the top and bottom rows
    for xbox in range(xdim):
        #Add more nodes to each cell in the top/bottom rows
        for i in range(saturation):
            xcoord=uniform(xbox,(xbox+1))
            ycoord=uniform(0,1)
            #Flag the nodes as boundary nodes if we're flagging boundary nodes
            if flag_bound:
                grid[0][xbox].append((xcoord,ycoord,rad,True))
            else:
                grid[0][xbox].append((xcoord,ycoord,rad))
            xcoord=uniform(xbox,(xbox+1))
            ycoord=uniform((ydim-1),ydim)
            if flag_boundary:
                grid[(ydim-1)][xbox].append((xcoord,ycoord,rad,True))
            else:
                grid[(ydim-1)][xbox].append((xcoord,ycoord,rad))
    #Do same for the leftmost and rightmost columns. Omit the corner cells, since these are already done in the above loop
    for ybox in range(1,(ydim-1),1):
        for i in range(saturation):
            xcoord=uniform(0,1)
            ycoord=uniform(ybox,(ybox+1))
            if flag_bound:
                grid[ybox][0].append((xcoord,ycoord,rad,True))
            else:
                grid[ybox][0].append((xcoord,ycoord,rad))
            xcoord=uniform((xdim-1),xdim)
            ycoord=uniform(ybox,(ybox+1))
            if flag_bound:
                grid[ybox][(xdim-1)].append((xcoord,ycoord,rad,True))
            else:
                grid[ybox][(xdim-1)].append((xcoord,ycoord,rad))
    return grid

#Function to add maxi-circles of a given radius throughout the grid
def add_maxi_circles(grid,xdim,ydim,maxi_rad,amount,hexg=False,flag_bound=False):
    #Create as many maxi circles as desired
    for i in range(amount):
        #Get the coordinates
        x_coord=uniform(0,xdim)
        y_coord=uniform(0,ydim)
        #Get the cell the coordinates live in
        xbox=int(np.floor(x_coord))
        ybox=int(np.floor(y_coord))
        #if we are in a hexagonal grid, then there is more work to do to figure out where in the grid to put the new node
        if hexg:
            maxi_tup=[x_coord,y_coord,maxi_rad]
            #Initialize d0 to be the maximum possible distance between two nodes in the grid
            d0=dist((0,0),(xdim,ydim))
            #Run through every row, every node stack in the row, and every node in the stack
            for band in range(len(grid)):
                for stack in range(len(grid[band])):
                    for node in grid[band][stack]:
                        #Find the distance from this node to the maxi circle
                        d=dist(node,maxi_tup)
                        #If this node is closer to the maxi circle than the previous closest node, note it's indices
                        if d<d0:
                            maxi_ind=(band,stack)
                            d0=d
            #Add the new node to the stack closest to its position. Flag it as being not a boundary, even if it winds up in a boundary cell, if we're flagging the boundary
            if flag_bound:
                grid[maxi_ind[0]][maxi_ind[1]].append(tuple(maxi_tup+[False]))
            else:
                grid[maxi_ind[0]][maxi_ind[1]].append(tuple(maxi_tup))
        else:
            #Add the node to the cell's list
            if flag_bound:
                grid[ybox][xbox].append((x_coord,y_coord,maxi_rad,False))
            else:
                grid[ybox][xbox].append((x_coord,y_coord,maxi_rad))
    return grid

#Function to compute the Cartesian distance between two points x and y
def dist(x,y):
    return np.sqrt((x[0]-y[0])**2+(x[1]-y[1])**2)
    
#Function to plot the grid for you viewing pleasure
def grid_visualizer(grid):
    #Create seperate lists for all the x coords and all the y coords, with the indices of each list coinciding
    x=list()
    y=list()
    #Run through each row
    for row in grid:
        #Run through each cell in the row
        for el in row:
            #Run through each node in the cell, and add its coordinates to the respective lists
            for sub_el in el:
                x.append(sub_el[0])
                y.append(sub_el[1])
    #Create a scatter plot of the points
    plt.scatter(x,y)
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

#Function to assign each node a graph vertex index.
def node_mtx(grid):
    #Initialize the index list
    idm=deepcopy(grid)
    ind=0
    #Run through each row of the grid
    for ybox in range(len(grid)):
        #Run through each cell in the row
        for xbox in range(len(grid[ybox])):
            #Run through each node in the cell
            for node in range(len(grid[ybox][xbox])):
                #Assign the node an index, and replace the relevent entry in the index matrix with the index
                idm[ybox][xbox][node]=ind
                ind+=1
    return idm, ind

#Function to creates an adjacency matrix for the graph of links.
def to_graph(grid,ringed=False):
    ymax=len(grid)
    xmax=len(grid[0])
    #Record start time
    start=time.time()
    #Grab the index matrix, which is the grid with every entry replaced by an index integer, and number of nodes in the grid
    idm,num_nodes=node_mtx(grid)
    #Create an empty adjacency matrix
    g=np.zeros((num_nodes,num_nodes))
    #Create a dictionary to keep track of which pairs of nodes have already been processed to prevent repeat processing (which would increase the probability of links)
    already_tried=dict()
    #Run through each row in the grid
    for ybox in range(ymax):
        row=grid[ybox]
        #Run through each cell in the row
        for xbox in range(xmax):
            cell=row[xbox]
            #Run through each node in the cell
            for node in range(len(cell)):
                #If we are ringing and this is a boundary box, we don't want to test for links via integration with any of the other nodes beyond the base node. Instead, later
                #on a connection will be made between any node the base node connects to and all other nodes in the stack.
                if ringed and (ybox==0 or ybox==(ymax-1) or xbox==0 or ybox==(xmax-1)) and node!=0:
                    break
                #Grab the coordinates and the radius, as well as the assigned index in idm
                cent1=cell[node][0:2]
                rad1=cell[node][2]
                node1_ind=idm[ybox][xbox][node]
                #Run through every cell that might conceivably have a node within range of the current node. The exception to this is that maxi circles within range may not
                #be checked here. But, that's ok, because they will have their own place in the sun when the outer loop reaches them
                for adj_y in range(int(np.floor(ybox-2*rad1)),int(np.ceil(ybox+1+2*rad1)),1):
                    for adj_x in range(int(np.floor(xbox-2*rad1)),int(np.ceil(xbox+1+2*rad1)),1):
                        #Screen for negative indices and indices out of grid bounds. Also, don't check for links between nodes in the same cell and 
                        if adj_y>=0 and adj_x>=0 and (xbox,ybox)!=(adj_x,adj_y) and adj_y<len(grid):
                            if adj_x<len(grid[adj_y]):
                                adj_cell=grid[adj_y][adj_x]
                                #Run through each node in the adjacent cell
                                for adj_node in range(len(adj_cell)):
                                    #Grab the second node's center, radius, and index
                                    cent2=adj_cell[adj_node][0:2]
                                    rad2=adj_cell[adj_node][2]
                                    node2_ind=idm[adj_y][adj_x][adj_node]
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
    #Ensures all boundary stacks link to adjacent boundary stacks if desired. This is a very non-optimal implementation. It would be much better to integrate this into the
    #above loop rather thabn do an entirely seperate one. However, this is the easiest solution right now and with the present algorithm and usage does not add a noticable
    #amount of processing time.
    if ringed:
        #Grab the height/width of the grid
        ymax=len(grid)
        xmax=len(grid[0])
        #Run through every box and node in the top/bottom rows
        for row in (0,(ymax-1)):
            for box in range(0,(xmax)):
                node_0_ind=idm[row][box][0]
                for node in range(len(grid[row][box])):
                    #Grab the node's index
                    node_ind=idm[row][box][node]
                    #Run through the two boxes to the left/right of this box (also boundary cells)
                    for adj_box in ((box-1),(box+1)):
                        if adj_box>=0 and adj_box<xmax:
                            #Run through each node in the adjacent cell
                            for adj_node in range(len(grid[row][adj_box])):
                                #Establish a link between the two nodes
                                adj_node_ind=idm[row][adj_box][adj_node]
                                g=graphite_add_connection(g,node_ind,adj_node_ind)
                    #Run through the other boxes that might have a node in range. I'm assuming rad=1, since it always seems to these days.
                    for adj_row in ((row-1),(row+1)):
                        for adj_box in ((box-1),box,(box+1)):
                            if adj_row>=0 and adj_box>=0 and adj_row<ymax and adj_box<xmax:
                                #Run through each node in the boxes
                                for adj_node in range(len(grid[adj_row][adj_box])):
                                    #If the node has a link to the base node in the boundary stack
                                    adj_ind=idm[adj_row][adj_box][adj_node]
                                    if g[node_0_ind][adj_ind]==1:
                                        #Add a connection between the node and the current boundary node
                                        g=graphite_add_connection(g,node_ind,adj_ind)
        #Do the same as the above, but with the leftmost/rightmost columns, excluding corners. The corners happen naturally when doing the others
        for row in range(1,ymax,1):
            for box in (0,(xmax-1)):
                for node in range(len(grid[row][box])):
                    node_ind=idm[row][box][node]
                    for adj_row in ((row-1),(row-1)):
                        for adj_node in range(len(grid[adj_row][box])):
                            adj_node_ind=idm[adj_row][box][adj_node]
                            g=graphite_add_connection(g,node_ind,adj_node_ind)
                    for adj_row in ((row-1),row,(row+1)):
                        for adj_box in ((box-1),(box+1)):
                            if adj_row>=0 and adj_box>=0 and adj_row<ymax and adj_box<xmax:
                                for adj_node in range(len(grid[adj_row][adj_box])):
                                    adj_ind=idm[adj_row][adj_box][adj_node]
                                    if g[node_0_ind][adj_ind]==1:
                                        g=graphite_add_connection(g,node_ind,adj_ind)
    #Display the time spent on compilation
    end=time.time()
    print("Time to compile: "+str(datetime.timedelta(seconds=(end-start))))
    return g, idm

#Function to convert a hex grid into an adjacency matrix and index matrix. Different from to_graph because I can assume some things that significantly reduce computation
#time in a hex grid. Like where every edge will be which removes the need for probability function integration
def to_graph_hex(grid,spacing):
    #Record start time
    start=time.time()
    #Grab the index matrix, which is the grid with every entry replaced by an index integer, and number of nodes in the grid
    idm,num_nodes=node_mtx(grid)
    #Create an empty adjacency matrix
    g=np.zeros((num_nodes,num_nodes))
    #Run through each node in the grid
    for ybox in range(len(grid)):
        for xbox in range(len(grid[ybox])):
            for node in range(len(grid[ybox][xbox])):
                #Get its coordinates and index
                stuff=grid[ybox][xbox][node]
                coords=stuff[0:2]
                rad=stuff[2]
                node_ind=idm[ybox][xbox][node]
                #Run through the two next-nearest rows
                for adj_y in range(int((ybox-1*rad)),int((ybox+2*rad)),1):
                    #Run through the four nodes in these rows to the left and the right of the primary node, plus nodes with the same xbox
                    for adj_x in range(int(xbox-1*rad),int(xbox+3*rad),1):
                        #Screen for nonexistant rows/nodes, and make sure we aren't looking for a connect from a node to itself
                        if adj_y>=0 and adj_x>=0 and adj_y<len(grid) and adj_x<len(grid[adj_y])and (adj_x,adj_y)!=(xbox,ybox):
                            #Run through each node in the adjacent stack
                            for adj_node in range(len(grid[adj_y][adj_x])):
                                #Grab its coordinates
                                adj_stuff=grid[adj_y][adj_x][adj_node]
                                adj_coords=adj_stuff[0:2]
                                adj_rad=adj_stuff[2]
                                #If the two nodes are nearest-neighbors (hexagon edges are equal to sqrt(1/3)*spacing. Next-nearest neighbors are [spacing] apart.
                                if dist(coords,adj_coords)<=float(np.sqrt(2/3)*spacing):
                                    #Grab the adjacent node's index and add a connection
                                    adj_ind=idm[adj_y][adj_x][adj_node]
                                    g=graphite_add_connection(g,node_ind,adj_ind)
                                #If one of the nodes is a maxi cricle
                                elif rad!=adj_rad and (dist(coords,adj_coords)-adj_rad)<=rad and (dist(coords,adj_coords)+adj_rad)>=rad:
                                    #Grab the adjacent node's index and add a connection
                                    adj_ind=idm[adj_y][adj_x][adj_node]
                                    g=graphite_add_connection(g,node_ind,adj_ind)
    #Display the time spent on compilation
    print("Time to compile: "+str(datetime.timedelta(seconds=(time.time()-start))))
    return g, idm

#Function to add an edge to the adjacency matrix of a hexagonal grid. Works like are_linked() below, but dosen't integrate proability functions                 
def graphite_add_connection(g,node_ind,adj_ind):
    g[node_ind][adj_ind]=1
    g[adj_ind][node_ind]=1
    return g

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
    d=np.sqrt((cent1[0]-cent2[0])**2+(cent1[1]-cent2[1])**2)
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

#Function to generate a regular hexagonal grid by overlaying two regular triangular grids
def hexagonal_grid(spacing, ydim, xdim, rad=0.5,flag_bound=False):
    grid=list()
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
                    #If we're flagging the boundary, this node will be a boundary node if it is in the first row, last row, last column, or second column
                    if flag_bound:
                        if y==0 or y==(int(ydim/2)-1) or x==1 or x==(int(xdim/2)-1):
                            row.append([(0.5+spacing*x,0.5+y*spacing*(np.sqrt(3)/2),1,True),])
                        else:
                            row.append([(0.5+spacing*x,0.5+y*spacing*(np.sqrt(3)/2),1,False),])
                    else:
                        #Add the coordiantes of the node to the grid. The bottom-left point will be at (0.5,0.5). After this, nodes are spaced as equilateral triangles
                        row.append([(0.5+spacing*x,0.5+y*spacing*(np.sqrt(3)/2),1),])
                #If we're flagging the boundary, this node will be a boundary node if it is in the first row, last row, first column, or last column
                if flag_bound:
                    if y==0 or y==(int(ydim/2)-1) or x==0 or x==(int(xdim/2)-1):
                        row.append([(0.5+0.5*spacing+spacing*x,0.5+np.sqrt(1/12)*spacing+y*spacing*(np.sqrt(3)/2),1,True),])
                    else:
                        row.append([(0.5+0.5*spacing+spacing*x,0.5+np.sqrt(1/12)*spacing+y*spacing*(np.sqrt(3)/2),1,False),])
                else:
                    #Add the corresponding point in the other sub-lattice, with x-coordinate increased by 0.5*spacing and y coordinate increased by sqrt(1/12)*spacing
                    row.append([(0.5+0.5*spacing+spacing*x,0.5+np.sqrt(1/12)*spacing+y*spacing*(np.sqrt(3)/2),1),])
            #If we are in an odd row
            else:
                #If we're flagging the boundary, this node will be a boundary node if it is in the first row, last row, first column, or last column
                if flag_bound:
                    if y==0 or y==(int(ydim/2)-1) or x==0 or x==(int(xdim/2)-1):
                        row.append([(0.5+spacing*x+spacing/2,0.5+y*spacing*(np.sqrt(3)/2),1,True),])
                    else:
                        row.append([(0.5+spacing*x+spacing/2,0.5+y*spacing*(np.sqrt(3)/2),1,False),])
                else:
                    #The row's x-position has to be shifted by 1/2 the spacing to create a triangular grid
                    row.append([(0.5+spacing*x+spacing/2,0.5+y*spacing*(np.sqrt(3)/2),1),])
                #Don't do this for the last column in order to ensure the grid has "even" sides
                if x!=(int(xdim/2)-1):
                    #If we're flagging the boundary, this node will be a boundary node if it is in the first row, last row, first column, or second-to-last column
                    if flag_bound:
                        if y==0 or y==(int(ydim/2)-1) or x==0 or x==(int(xdim/2)-2):
                            row.append([(0.5+0.5*spacing+spacing*x+spacing/2,0.5+np.sqrt(1/12)*spacing+y*spacing*(np.sqrt(3)/2),1,True),])
                        else:
                            row.append([(0.5+0.5*spacing+spacing*x+spacing/2,0.5+np.sqrt(1/12)*spacing+y*spacing*(np.sqrt(3)/2),1,False),])
                    else:
                        #Add the corresponding point in the other sub-lattice, with x-coordinate increased by 0.5*spacing and y coordinate increased by sqrt(1/12)*spacing
                        row.append([(0.5+0.5*spacing+spacing*x+spacing/2,0.5+np.sqrt(1/12)*spacing+y*spacing*(np.sqrt(3)/2),1),])
        #Add the row to the grid
        grid.append(row.copy())
    #Return the grid
    return tuple(grid)

#Function to supersaturate a hexagonal grid boundary with non-random node placement. New nodes will be placed directly atop the first node, will connect to everything the first
#node connects to (and nothing more), and will not connect to other nodes in the same position. Unlike add_reg_boundary() below, the hex grid is special in that there are
#effectively two columns' worth of boundary nodes on either side, as opposed to the one column on each side which add_reg_boundary() assumes
def hexagonal_boundary(grid,sat):
    #Run through the top and bottom rows
    for row in (0,(len(grid)-1)):
        #Run through each point in these rows
        for node in range(len(grid[row])):
            #Both subrows in these two superrows are boundary rows. So, duplicate each node
            for i in range(sat):
                grid[row][node].append(grid[row][node][0])
    #Run through all the other rows
    for row in range(1,(len(grid)-1),1):
        #Run through the first two and last two nodes in these rows
        for node in (0,1,(len(grid[row])-2),(len(grid[row])-1)):
            #These are boundary nodes. So, duplicate them
            for i in range(sat):
                grid[row][node].append(grid[row][node][0])
    return grid

#Function to generate a regular rectangular grid
def rectangular_grid(rows, columns, spacing=1,rad=1,flag_bound=False):
    grid=list()
    #Run through each row
    for y in range(rows):
        row=list()
        del row[:]
        #Run through each column
        for x in range(columns):
            #If we're flagging the boundary, do that
            if flag_bound:
                if y==0 or y==(rows-1) or x==0 or x==(columns-1):
                    row.append([(x,y,rad,True),])
                else:
                    row.append([(x,y,rad,False),])
            else:
                #Add the coordinates as a node to the row
                row.append([(x,y,rad),])
        #Add the row to the grid
        grid.append(row.copy())
    #Return the grid
    return grid

#Function to generate a regular triangular grid
def triangular_grid(rows, num_in_row, spacing=1,rad=1,flag_bound=False):
     grid=list()
     #Run through each row the user wants to generate
     for y in range(rows):
         row=list()
         del row[:]
         #Run through the nodes the user wants to be in each row
         for x in range(num_in_row):
             #If we are on an even row
             if y%2==0:
                 #If we're flagging the boundary, do that
                 if flag_bound:
                     if y==0 or y==(rows-1) or x==0 or x==(num_in_row-1):
                         row.append([(0.5+spacing*x,0.5+y*spacing*(np.sqrt(3)/2),rad,True),])
                     else:
                         row.append([(0.5+spacing*x,0.5+y*spacing*(np.sqrt(3)/2),rad,False),])
                 else:
                     #Add the coordiantes of the node to the grid. The bottom-left point will be at (0.5,0.5). After this, nodes are spaced as equilateral triangles
                     row.append([(0.5+spacing*x,0.5+y*spacing*(np.sqrt(3)/2),rad),])
            #If we are in an odd row
             else:
                 #If we're flagging the boundary, do that
                 if flag_bound:
                     if y==0 or y==(rows-1) or x==0 or x==(num_in_row-1):
                         row.append([(0.5+spacing*x+spacing/2,0.5+y*spacing*(np.sqrt(3)/2),rad,True),])
                     else:
                         row.append([(0.5+spacing*x+spacing/2,0.5+y*spacing*(np.sqrt(3)/2),rad,False),])
                 else:
                     #The row's x-position has to be shifted by 1/2 the spacing to create a triangular grid
                     row.append([(0.5+spacing*x+spacing/2,0.5+y*spacing*(np.sqrt(3)/2),rad),])
         #Add the row to the grid
         grid.append(row.copy())
     #Return the grid
     return grid, spacing

#Adds a regular boundary (new points placed directly atop existing ones) to a triangular, rectangular, or regularized randomized grid
def add_reg_boundary(grid,saturation):
    #Grab number of rows/columns
    ymax=len(grid)-1
    xmax=len(grid[0])-1
    #Supersaturate the entire bottom/top rows
    for row in (0,ymax):
        for stack in range(len(grid[row])):
            cur_node=grid[row][stack][0]
            for i in range(saturation):
                #Each new node is a duplicate of the existing node. Incidentally, this removes the need for a flag_bound dichotomy
                grid[row][stack].append(cur_node)
    #Supersaturate the entire first/last columns, excluding the corners as these were already done in the above step
    for row in range(1,ymax,1):
        for stack in (0,xmax):
            cur_node=grid[row][stack][0]
            for i in range(saturation):
                grid[row][stack].append(cur_node)
    return grid

#Generates an adjacency and index matrix using a rectantular grid
def to_graph_rectangular(grid):
    #Grab the radius of 'standard" nodes in the base grid
    base_rad=grid[0][0][0][2]
    #Record start time
    start=time.time()
    #Grab the index matrix, which is the grid with every entry replaced by an index integer, and number of nodes in the grid
    idm,num_nodes=node_mtx(grid)
    #Create an empty adjacency matrix
    g=np.zeros((num_nodes,num_nodes))
    #Run through each node in the grid
    for row in range(len(grid)):
         for stack in range(len(grid[row])):
             for node in range(len(grid[row][stack])):
                 #Retrieve the coordinates and radius, as well as the node's index
                 stuff=grid[row][stack][node]
                 coords=stuff[0:2]
                 rad=stuff[2]
                 node_ind=idm[row][stack][node]
                 #If this is not a maxi circle
                 if rad==base_rad:
                     #Run through the four nearest-neighbor stacks
                     for adj_nodes in [(row-1,stack),(row+1,stack),(row,stack-1),(row,stack+1)]:
                         #Make sure it exists
                         if adj_nodes[0]>=0 and adj_nodes[0]<len(grid) and adj_nodes[1]>=0 and adj_nodes[1]<len(grid[0]):
                             #Run through every node in the stack
                             for adj_node in range(len(grid[adj_nodes[0]][adj_nodes[1]])):
                                 #Grab the adjacent node's coordiantes and radius
                                 adj_stuff=grid[adj_nodes[0]][adj_nodes[1]][adj_node]
                                 adj_coords=adj_stuff[0:2]
                                 adj_rad=adj_stuff[2]
                                 #If the adjacent node is not a maxi circle
                                 if adj_rad==rad:
                                     #And they are nearest neighbors (this is guarenteed in the current scheme, since seperation=radius=1. But, if this ever changes, this will
                                     #be here to acomodate the new algorithm)
                                     if (dist(coords,adj_coords)-rad)<=0.001:
                                         #Retrieve the adacent node's index and create a link in the adjacency matrix
                                         adj_ind=idm[adj_nodes[0]][adj_nodes[1]][adj_node]
                                         g[node_ind][adj_ind]=1
                                         g[adj_ind][node_ind]=1
                 #If this node is a maxi circle
                 else:
                     #Run through every node in the grid
                     for adj_row in range(len(grid)):
                         for adj_stack in range(len(grid[adj_row])):
                             for adj_node in range(len(grid[adj_row][adj_stack])):
                                 adj_stuff=grid[adj_row][adj_stack][adj_node]
                                 adj_coords=adj_stuff[0:2]
                                 adj_rad=adj_stuff[2]
                                 d=dist(adj_coords, coords)
                                 #If the probability field of the adjacent node intersects the periphery of the maxi cirlce's field
                                 if d<(adj_rad+rad) and d>abs(adj_rad-rad):
                                     #Add a connection in the adjacency matrix
                                     adj_ind=idm[adj_row][adj_stack][adj_node]
                                     g[node_ind][adj_ind]=1
                                     g[adj_ind][node_ind]=1
    #Display the time spent on compilation
    print("Time to compile: "+str(datetime.timedelta(seconds=(time.time()-start))))
    return tuple(g), tuple(idm)

#Generates an adjacency and index matrix using a triangular grid
def to_graph_triangular(grid,spacing):
    #Grab the radius of 'standard" nodes in the base grid
    base_rad=grid[0][0][0][2]
    #Record start time
    start=time.time()
    #Grab the index matrix, which is the grid with every entry replaced by an index integer, and number of nodes in the grid
    idm,num_nodes=node_mtx(grid)
    #Create an empty adjacency matrix
    g=np.zeros((num_nodes,num_nodes))
    #Run through each node in the grid
    for row in range(len(grid)):
         for stack in range(len(grid[row])):
             for node in range(len(grid[row][stack])):
                 #Retrieve the coordinates and radius, as well as the node's index
                 stuff=grid[row][stack][node]
                 coords=stuff[0:2]
                 rad=stuff[2]
                 node_ind=idm[row][stack][node]
                 #If this is not a maxi circle
                 if rad==base_rad:
                     #Run through the six nearest-neighbor stacks
                     for adj_nodes in [(row+1,stack),(row+1,stack+1),(row,stack-1),(row,stack+1),(row-1,stack),(row,stack+1),(row+1,stack-1),(row-1,stack-1)]:
                         #Make sure it exists
                         if adj_nodes[0]>=0 and adj_nodes[0]<len(grid) and adj_nodes[1]>=0 and adj_nodes[1]<len(grid[0]):
                             #Run through every node in the stack
                             for adj_node in range(len(grid[adj_nodes[0]][adj_nodes[1]])):
                                 #Grab the adjacent node's coordiantes and radius
                                 adj_stuff=grid[adj_nodes[0]][adj_nodes[1]][adj_node]
                                 adj_coords=adj_stuff[0:2]
                                 adj_rad=adj_stuff[2]
                                 #If the adjacent node is not a maxi circle
                                 if adj_rad==rad:
                                     #And they are nearest neighbors (this is guarenteed in the current scheme, since seperation=radius=1. But, if this ever changes, this will
                                     #be here to acomodate the new algorithm)
                                     if (dist(coords,adj_coords)-rad)<=0.001:
                                         #Retrieve the adacent node's index and create a link in the adjacency matrix
                                         adj_ind=idm[adj_nodes[0]][adj_nodes[1]][adj_node]
                                         g[node_ind][adj_ind]=1
                                         g[adj_ind][node_ind]=1
                 #If this node is a maxi circle
                 else:
                     #Run through every node in the grid
                     for adj_row in range(len(grid)):
                         for adj_stack in range(len(grid[adj_row])):
                             for adj_node in range(len(grid[adj_row][adj_stack])):
                                 adj_stuff=grid[adj_row][adj_stack][adj_node]
                                 adj_coords=adj_stuff[0:2]
                                 adj_rad=adj_stuff[2]
                                 d=dist(adj_coords, coords)
                                 #If the probability field of the adjacent node intersects the periphery of the maxi cirlce's field
                                 if d<(adj_rad+rad) and d>abs(adj_rad-rad):
                                     #Add a connection in the adjacency matrix
                                     adj_ind=idm[adj_row][adj_stack][adj_node]
                                     g[node_ind][adj_ind]=1
                                     g[adj_ind][node_ind]=1
                                
    #Display the time spent on compilation
    print("Time to compile: "+str(datetime.timedelta(seconds=(time.time()-start))))
    return tuple(g), tuple(idm)

