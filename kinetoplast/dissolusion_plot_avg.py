'''
Program name: dissolusion_plot_avg.py
Author: Nathaniel Morrison
Date created: 05/30/2020
Date last modified: 07/18/2020
Python Version: 3.7.2
'''
'''
Generates a plot of bf_search data
'''
import xlrd
import matplotlib.pyplot as plt
import os

#Function to load bf_search output datafile
def excel_loader(path):
    #Load the workbook
    wb=xlrd.open_workbook(path+'.xlsx')
    #Return the workbook and worksheet
    return wb, wb.sheets()[0]

#Function to gather the x-y coordinate data from the datafile
def data_retriever(ws):
    #Get total number of rows
    tot_rows=ws.nrows - 1
    #Row 0 is header. Start at row 1
    cur_row=1
    x_coords=list()
    y_coords=list()
    #Run through each row
    while cur_row<=tot_rows:
        #The x-coordinate (number of dissolutions) is the same for all points in the row
        x_coord=int(str(ws.cell(cur_row, 0)).lstrip("text: '").rstrip("'"))
        #Colummn 0 is the number of dissolutions. Starting with column 1, each entry is a pair: (component size, number of components with this size)
        cur_col=1
        y_coord_row=list()
        del y_coord_row[:]
        #Get the pair as a string
        cur_pair=str(ws.cell(cur_row,cur_col)).lstrip("text: '").rstrip("'")
        #When an empty cell is reached, it will return "mpty: ''". So, go until this is returned
        while cur_pair[0]=='(':
            #Start extracting the y_coordinate
            y_coord_raw=''
            #Run through each character in the pair string
            for el in cur_pair[1:]:
                #When we hit a comma, we're done
                if el!=',':
                    y_coord_raw+=el
                else:
                    break
            #Omit components with size <= the threshold size (10)
            if int(y_coord_raw)>10:
                y_coord_row.append(int(y_coord_raw))
            cur_col+=1
            #For the rows with maximum length, the ws object dosen't even load further empty columns, so this will return an error. If this happens, we are done processing
            #the row
            try:
                cur_pair=str(ws.cell(cur_row,cur_col)).lstrip("text: '").rstrip("'")
            except:
                break
        #Add the x and y coordinates to the master lists, with the y-values being a tuple associated with the x-value
        x_coords.append(x_coord)
        y_coords.append(tuple(y_coord_row))
        cur_row+=1
    #Return the x and y coordinate tuples
    return tuple(x_coords),tuple(y_coords)

#Function do the actual plotting
def plotter(x_coords, y_coords,export_name,io_name):
    #Create the figure object
    fig = plt.figure()
    #Generate a scatter plot with circle markers. s is the area of the markers in arbitrary units; it defaults to 20
    plt.scatter(x_coords,y_coords,marker='o',s=0.5)
    #Generate the plot title
    fig.suptitle(io_name, fontsize=20)
    #Generate the axis labels
    plt.xlabel('Dissolutions', fontsize=18)
    plt.ylabel('Nodes in Component(s)', fontsize=16)
    #Save the figure with 300 dots per inch
    fig.savefig(export_name+'_plot.png',dpi=300)
    return

#Function to find median y-value list for each x-value
def medianizer(x_master, y_master):
    x_coords=list()
    y_coords=list()
    #Sort the trials by the maximum number of dissolutions, so the first sets in each list are from the trial that had the most dissolutions before stopping
    x_master=sorted(x_master, key=len, reverse=True)
    y_master=sorted(y_master, key=len, reverse=True)
    #Run through each x-value in the longest x-list
    for i in range(len(x_master[0])):
        #Grab all the y-value tuples associated with the current x-value across all the trials
        plot_ys=[c[i] for c in y_master]
        #Sort them by the value of their first entry
        plot_ys.sort()
        #Take the median of the list, rounded up
        y_lis=plot_ys[int(len(y_master)/2)]
        #Run through each y-value in the median list
        for y_val in y_lis:
            #Add the y-value and the appropriate x-value to the plottable lists
            x_coords.append(x_master[0][i])
            y_coords.append(y_val)
        j=0
        #Check if this was the final x-value of any of the trials. If it was, delete the trial from the master list
        while j <len(y_master):
            if (i+1)==len(y_master[j]):
                y_master.pop(j)
            else:
                j+=1
    #Return the plottable coordinate lists
    return x_coords,y_coords

#Function to conduct this orchestra of chaos
if __name__=='__main__':
    direct='C:\\Users\\Nate Morrison\\Desktop\\CSULB\\KnotTheory\\Python_Output\\Kinetoplast\\Hexagonal_Grid\\To_Aggregate'
    os.chdir(direct)
    #Define the name of the both the input and output files
    io_name="RKP_NM_hexagonalGrid_9sat_dp_avg"
    export_name=direct+'\\'+io_name
    x_master=list()
    y_master=list()
    for file_name in os.listdir():
        if file_name[-5:]=='.xlsx':
            path=direct+'\\'+file_name
            wb,ws=excel_loader(path)
            x_coords, y_coords=data_retriever(ws)
            #Add them to the appropriate lists
            x_master.append(x_coords)
            y_master.append(y_coords)
    #Find the median of each x-position and return them as plottable lists
    x_coords, y_coords=medianizer(x_master, y_master)
    #Generate the plot
    plotter(x_coords,y_coords,export_name,io_name)
main()
