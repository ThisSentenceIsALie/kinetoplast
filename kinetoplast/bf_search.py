'''
Module name: bf_search.py
Author: Nathaniel Morrison
Date created: 05/29/2020
Date last modified: 08/30/20120
Python Version: 3.7.2
'''
from random import choice
import networkx as nx
import xlsxwriter
from graph_funcs import export_graph_pic
import os

#Function to randomly remove a given number of nodes from the graph
def dissolve(n, G):
    #Iterate as many times as the user requests
    for i in range(n):
        #Remove a random node
        G.remove_node(choice(list(G.nodes)))
    #Return the resultant graph
    return G

#Same as dissolve(), but will flag whenever a boundary stack has been entirely wiped out
def dissolve_flag_bound(n,G,sat,bound_dict):
    bound_broke=False
    for i in range(n):
        node=choice(list(G.nodes))
        #If the node to be removed is flagged as a boundary node
        if G.nodes[node]['Bound?']:
            #Subtract one from its cell's dictionary entry. Or, if it dosen't have an entry yet, create one, noting that the cell contains one less node than the saturation
            try:
                bound_dict[G.nodes[node]['Cell']]-=1
            except:
                bound_dict[G.nodes[node]['Cell']]=(sat-1)
            #If the number of nodes in the cell will be 0 once this node is removed, flag this as a new break in the boundary
            if bound_dict[G.nodes[node]['Cell']]==0:
                bound_broke=True
        #Remove the node
        G.remove_node(node)
    return G, bound_dict,bound_broke

#Function to delete nodes and track the number and size of compoenents
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

#Does the same thing as bf_search(), but also records when the first and second breaks in the boundary ring appear
def bf_search_flag_bound(step,G,thresh,sat):
    master=list()
    max_size=nx.number_of_nodes(G)
    bound_dict=dict()
    first_broke=True
    second_broke=True
    bound_broke=False
    while max_size>thresh:
        cur_step_info=list()
        del cur_step_info[:]
        components=[len(c) for c in sorted(nx.connected_components(G), key=len, reverse=True)]
        prev_component=0
        for component in components:
            if component !=prev_component:
                cur_step_info.append((component,components.count(component)))
                prev_component=component
        #If we have not yet had the first hole in the boundary appear and a hole in the boundary has just appeared
        if first_broke and bound_broke:
            #Note it in the output file
            master.append(tuple(cur_step_info+['Boundary Breaks Here']))
            first_broke=False
        #If we have had one hole in the boundary appear but not two, and a new hole in the boundary has just appeared
        elif second_broke and bound_broke:
            #Flag it in the output file
            master.append(tuple(cur_step_info+['Boundary Splits in Two Here']))
            second_broke=False
        else:
            master.append(tuple(cur_step_info))
        max_size=components[0]
        G, bound_dict,bound_broke=dissolve_flag_bound(step,G,sat,bound_dict)
    return tuple(master)

#Doest the same thing as bf-search(), but also periodically exports component plots at pre-defined dissolution steps (called "critical points")
def bf_search_with_pics(step,G,thresh,crit_points,path):
    #Create a file to house the component plots, if it does not already exist
    if not os.path.exists(path):
        os.makedirs(path)
    dissolutions=0
    #Export a component plot before anything has happened
    export_graph_pic(G,dissolutions,path)
    #Define list to hold all the component zise info at every step
    master=list()
    #The largest component in G is assumed to contain all the nodes at the start
    max_size=nx.number_of_nodes(G)
    #Go until every componet in G is smaller than the given threshold size
    while max_size>thresh:
        #If we are at a critical point, export a component picture
        if dissolutions in crit_points:
            export_graph_pic(G,dissolutions,path)
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
        dissolutions+=step
    #At the end, export one last component picture
    export_graph_pic(G,dissolutions,path)
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
