'''
Module name: bf_search3D.py
Author: Nathaniel Morrison
Date created: 06/29/2020
Date last modified: 06/29/2020
Python Version: 3.7.2
'''
from random import choice
import networkx as nx
import xlsxwriter
import os


#Function to randomly remove a given number of nodes from the graph
def dissolve(n, G):
    #Iterate as many times as the user requests
    for i in range(n):
        #Remove a random node
        G.remove_node(choice(list(G.nodes)))
    #Return the resultant graph
    return G

#Function to delte nodes and track the number and size of components
def bf_search(step,G,thresh):
    #Define list to hold all the component zise info at every step
    master=list()
    #The largest component in G is assumed to contain all the nodes at the start
    max_size=nx.number_of_nodes(G)
    #Go until every componet in G is smaller than the given threshold size
    while max_size>thresh:
        #Define list to hold all the component sizes at this step
        cur_step_info=list()
        del cur_step_info[:]
        #Generate a list of component sizes. There will be one entry for each component, being the number of nodes in the component. The list will be in descending order.
        components=[len(c) for c in sorted(nx.connected_components(G), key=len, reverse=True)]
        prev_component=0
        #Run through each component length
        for component in components:
            #If the components with this length have not already been tallied
            if component !=prev_component:
                #Add a two-tuple to the current step list, the first element being the length of the component, the second being the number of components with this length
                cur_step_info.append((component,components.count(component)))
                prev_component=component
        #Add the current step info to the master list
        master.append(tuple(cur_step_info))
        #Get the largest component at this step
        max_size=components[0]
        #Dissolve more nodes in G
        G=dissolve(step,G)
    #Return the master list
    return tuple(master)

#Function to write results to file
def excel_io(master,step_size, excel_name):
    #Create output file
    workbook=xlsxwriter.Workbook(excel_name+".xlsx")
    #Add a worksheet to the output file
    worksheet = workbook.add_worksheet()
    #Add header
    worksheet.write(0, 0, 'Dissolutions; Step size = '+str(step_size))
    worksheet.write(0, 1, 'From here on, columns give pairs of numbers, 1st being component size and 2nd being the number of components of that size')
    cur_row=1
    #Run through each step
    for step in master:
        #Write the number of dissolutions at this step in the left column
        worksheet.write(cur_row, 0, str(((cur_row-1)*step_size)))
        cur_col=1
        #Run through each component size tuple
        for component in step:
            #Write the tuple to the file
            worksheet.write(cur_row, cur_col, str(component))
            cur_col+=1
        cur_row+=1
    #Closet the output workbook
    workbook.close()
    return
