# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 13:16:39 2021

@author: Maarten

Please set options => Preferences => IPython console => Graphics => Graphics Backend to QT5!
"""
version=1.0

import os
import pandas as pd
from scipy import signal
import matplotlib as mpl
import matplotlib.pyplot as plt
#from IPython import get_ipython Read ^^^^
#get_ipython().run_line_magic('matPlotlib', 'qt5')
mpl.rcParams.update({'figure.autolayout': True})


class Data:
    def read(filename):
        Data.timelabel="Time (seconds)"
        Data.coords=pd.DataFrame() #columns=['x','y','xindex']
        Data.bubble=pd.DataFrame()
        Data.corr=pd.DataFrame()
        Data.dropped=[]
        Data.sub=[]
        Data.add=[]
        Data.ylabel="Shift (picometer)"
        Data.graphtitle="You didnt change the title"
        Data.error=1,"Error: Please provide full filename or check if filename exists!"
        if os.path.isfile(filename):
            Data.test = pd.read_table(filename,delimiter='\t',nrows=0)
            print(Data.test.columns[0])
            Data.filename=filename
            if 'Run' in Data.test.columns[0]:
                Data.filetype="Lionix"
                Data.error=File.readL(filename,6)
            elif 'Time' in Data.test.columns[0]:
                Data.filetype="Lionix"
                Data.error=File.readL(filename,1)
            elif 'SDK Outputs:' in Data.test.columns[0]:
                Data.filetype="PID"
                Data.error=File.readP(filename)
            else:
                Data.filetype="Delta Diagnostics"
                Data.error=File.readD(filename)
        if Data.error[0] is 1:
            print(f"\n{Data.error[1]}")
        else:
            print(f"\n{Data.error[1]}\n\n{Data.mod}")
            print(Plot.draw()[1])

    def write():
        filename=input("Please provide a filename: ") + str("_modified.xls")
        if os.path.isfile(filename):
            print("\nFile already exists!! Please provide a newname")
            Data.write()
        if len(Data.mod) > 10000:
            print("Data is very big, if you plan on using it in excel, you might consider shrinking it down")
            answer=input("Shrink Data down? (10X) (y/n/yes/no): ")
            if 'y' in answer:
                Time.shrinkdata(10)
            if answer.isnumeric():
                Time.shrinkdata(int(answer))
        Data.mod.to_csv(filename,sep='\t',decimal=',')
        return(0,f"OK: Data written to: {filename}, shrunken down {answer} times")

    def reset():
        if Data.filetype == "Lionix":
            File.readL(Data.filename,Data.skip)
        elif Data.filetype == "Delta":
            File.readD(Data.filename)
        else:
            File.readP(Data.filename)
        Data.dropped=[]
        Data.sub=[]
        #Data.coords=pd.DataFrame()
        Plot.draw()
        return(0,"OK: all ring Data restored")

    def slopecorr(*redo):
        if not redo:
            Data.coords=Data.coords.append(Plot.clicknew(2,'slope',"Please click left and right bound for slope detection")[-1])
        Data.coords=Data.coords[~Data.coords.index.duplicated(keep='last')]
        Data.corr['slope']=(Data.mod.iloc[Data.coords.loc['slope0'].xindex,~Data.mod.columns.isin(['time'],level=1)]
                                -Data.mod.iloc[Data.coords.loc['slope1'].xindex,~Data.mod.columns.isin(['time'],level=1)])/(
                                    Data.coords.loc['slope0'].x-Data.coords.loc['slope1'].x)
        print(f"Calculated slopes:\n{Data.corr['slope']}")
        for i in range(len(Data.mod.columns)-1):
            Data.mod[Data.mod.columns[i+1]]=Data.mod.iloc[:,i+1]-(Data.corr.slope[i]*Data.mod.iloc[:,0])
        Plot.draw()

    def zerocorr(*redo):
        if not redo:
            Data.coords=Data.coords.append(Plot.clicknew(1,'zero',"Please click where the plot should be 0")[-1])
        Data.coords=Data.coords[~Data.coords.index.duplicated(keep='last')]
        Data.corr['zero']=pd.DataFrame(Data.mod.iloc[Data.coords.loc['zero0'].xindex,~Data.mod.columns.isin(['time'],level=1)])
        print(f"Calculated zeros at t={Data.coords.loc['zero0'].x}:\n{Data.corr['zero']}")
        for i in range(len(Data.mod.columns)-1):
            Data.mod[Data.mod.columns[i+1]]=Data.mod.iloc[:,i+1]-Data.corr.zero[i]
        Plot.draw()

    def indexconv(values):
        lst=[]
        for i in values:
            lst.append(int(Data.mod.time.index[Data.mod.time.time==i].tolist()[0]))
        return(lst)

class File:
    def readL(filename,*skip):
        if skip:
            Data.skip=skip[0]
        if os.path.isfile(filename):
            Data.raw = pd.read_table(filename,
                                 delimiter='\t',
                                 usecols=range(0,9),
                                 skiprows=skip[0],decimal=',',
                                 names=['time', 'ring 1', 'ring 2', 'ring 3', 'ring 4', 'ring 5', 'ring 6', 'ring 7', 'ring 8']
                                 )
            Data.mod=Data.raw.copy(deep=True)

            Data.mod.columns= [['time', 'ring 1', 'ring 2', 'ring 3', 'ring 4', 'ring 5', 'ring 6', 'ring 7', 'ring 8'],
                                    ['time', 'ring 1', 'ring 2', 'ring 3', 'ring 4', 'ring 5', 'ring 6', 'ring 7', 'Reference ring']]
            return(0,f"OK: {Data.filetype} file \"{filename}\" successfully read into memory.")
        return(1,"Error: Please provide full filename or check if filename exists")


    def readD(filename):
        if os.path.isfile(filename):
            Data.raw = pd.read_table(filename,
                                 delimiter=',',
                                 usecols=range(0,7),
                                 skiprows=6,decimal='.',
                                 names=['time', 'ring 1', 'ring 2', 'ring 3', 'ring 4', 'ring 5', 'ring 6']
                                 )
            Data.mod=Data.raw.copy(deep=True)

            Data.mod.columns= [['time', 'ring 1', 'ring 2', 'ring 3', 'ring 4', 'ring 5', 'ring 6'],
                                    ['time', 'ring 1', 'ring 2', 'ring 3', 'Reference Ring', 'ring 5', 'ring 6']]
            Data.mod=Data.mod[['time','ring 1','ring 2','ring 3', 'ring 5', 'ring 6', 'ring 4']]
            return(0,f"OK: {Data.filetype} file \"{filename}\" successfully read into memory.")
        return(1,"Error: Please provide full filename or check if filename exists")

    def readP(filename):
        if os.path.isfile(filename):
            Data.raw = pd.read_table(filename,
                                 delimiter=';',
                                 usecols=range(1,2),
                                 skiprows=20,decimal=',',
                                 names=['PID']
                                 )
            Data.mod=Data.raw.copy(deep=True)

            Data.mod.columns= [['PID'],
                               ['PID']]
            Data.mod['time','time']=Data.mod.index
            Data.mod=Data.mod[['time','PID']]
            Data.ylabel="ppm"
            return(0,f"OK: {Data.filetype} file \"{filename}\" successfully read into memory.")
        return(1,"Error: Please provide full filename or check if filename exists")

class Time:
    def ctm():
        if Data.timelabel=='Time (seconds)':
            Data.mod.time=Data.mod.time/60
            if 'x' in Data.coords.columns:
                Data.coords.x=Data.coords.x/60
            print("Converting seconds to minutes")
            Data.timelabel="Time (minutes)"
        else:
            Data.mod.time=Data.mod.time*60
            if 'x' in Data.coords.columns:
                Data.coords.x=Data.coords.x*60
            print("Converting minutes to seconds")
            Data.timelabel="Time (seconds)"
        Plot.draw()

    def tsub(seconds):
        if isinstance(seconds, int):
            if seconds == 0:
                seconds=Data.mod.time.iloc[0][0]
            Data.mod.time=Data.mod.time-seconds
        else:
            return('1','Error: Time is not an integer')
        if 'x' in Data.coords.columns:
            Data.coords.x=Data.coords.x-seconds
        Plot.draw()
        if Data.timelabel=='Time (seconds)':
            return('0','OK: Moved timescale with {} seconds'.format(seconds))
        else:
            return('0','OK: Moved timescale with {} minutes'.format(seconds))

    def trim(*new):
        if new:
            Data.coords=Data.coords.append(Plot.clicknew(2,'trim',"Set a new trim range")[-1])
        if any("trim" in x for x in Data.coords.index.values):
            Data.mod.drop(range(Data.coords.xindex['trim1']+1,len(Data.mod.index)),axis=0,inplace=True)
            Data.mod.drop(range(Data.mod.index[0],Data.coords.xindex['trim0']),axis=0,inplace=True)
        else:
            Data.mod.drop(range(Data.coords.xindex['slope1']+1,len(Data.mod.index)),axis=0,inplace=True)
            Data.mod.drop(range(Data.mod.index[0],Data.coords.xindex['slope0']),axis=0,inplace=True)
        Plot.draw()

    def cut(*time):
        Data.coords=Data.coords.append(Plot.clicknew(2,'cut',"Set a range to cut out")[-1])
        Data.coords=Data.coords[~Data.coords.index.duplicated(keep='last')]
        if time:
            Data.mod.time=pd.concat(
                [Data.mod.time.time.iloc[0:Data.coords.xindex['cut0']],
                 Data.mod.time.time.iloc[Data.coords.xindex['cut0']:]
                 -(Data.coords.x['cut1']-Data.coords.x['cut0'])])
            #werkt nog niet
        Data.mod.drop(Data.mod.loc[Data.coords.xindex['cut0']:Data.coords.xindex['cut1']].index.values,axis=0,inplace=True)
        Plot.draw()

    def shrinkdata(x):
        Data.mod=Data.mod.iloc[::x,:]
        print("Shrinking Data {} times".format(x))
        Plot.draw()



class Rings:
    def drop(*rings):
        Data.derror=[]
        for i in rings:
            if i == 8:
                print("Can't drop ring 8")
            elif 'ring ' + str(i) in Data.mod.keys().get_level_values(0):
                Data.mod.drop(['ring '+str(i)],axis=1,inplace=True, level=0)
                Data.dropped.append(i)
            else:
                Data.derror.append(i)
        if len(Data.derror) > 0:
            print("\nSkipped {} Already dropped\n".format(', '.join(str(v) for v in Data.derror)))
        Data.dropped.sort()
        print("\nDropped ring(s): {}\n".format(', '.join(str(v) for v in Data.dropped)))
        Plot.draw()

    def sub(*srings):
        Data.serror=[]
        for i in srings:
            if 'ring '+str(i) in Data.mod.keys().get_level_values(0) and i not in Data.sub:
                if i == 8:
                    Data.mod.loc[:,~Data.mod.columns.isin(['time'],level=1)]=Data.mod.loc[:,~Data.mod.columns.isin(['time'],level=1)]-Data.mod['ring '+str(i)].values
                else:
                    Data.mod.loc[:,~Data.mod.columns.isin(['time','Reference ring'],level=1)]=Data.mod.loc[:,~Data.mod.columns.isin(['time','Reference ring'],level=1)]-Data.mod['ring '+str(i)].values
                Data.sub.append(i)
            else:
                Data.serror.append(i)
        if len(Data.serror) > 0:
            print("\nSkipped {}. Ring(s) are already subtracted or dropped\n".format(', '.join(str(v) for v in Data.serror)))
        Data.sub.sort()
        print("\nSubtracted ring(s): {}\n".format(', '.join(str(v) for v in Data.sub)))
        Plot.draw()

    def add(*srings):
        Data.serror=[]
        for i in srings:
            if 'ring '+str(i) in Data.mod.keys().get_level_values(0) and i not in Data.add:
                if i == 8:
                    Data.mod.loc[:,~Data.mod.columns.isin(['time'],level=1)]=Data.mod.loc[:,~Data.mod.columns.isin(['time'],level=1)]+Data.mod['ring '+str(i)].values
                else:
                    Data.mod.loc[:,~Data.mod.columns.isin(['time','Reference ring'],level=1)]=Data.mod.loc[:,~Data.mod.columns.isin(['time','Reference ring'],level=1)]+Data.mod['ring '+str(i)].values
                Data.add.append(i)
            else:
                Data.serror.append(i)
        if len(Data.serror) > 0:
            print("\nSkipped {}. Ring(s) are already added or dropped\n".format(', '.join(str(v) for v in Data.serror)))
        Data.add.sort()
        print("\nAdded ring(s): {}\n".format(', '.join(str(v) for v in Data.add)))
        Plot.draw()

    def rename():
        print("Current labels:\n\nTitle of graph: {}\n".format(Data.graphtitle))
        for i in Data.mod.columns[~Data.mod.columns.isin(['time'],level=0)]:print(str(i).replace("('","").replace("')","").replace("', '"," | "))
        Data.rename = input("Which ring(s) do you want to rename? (or Title for graph title or PID for PID): ")
        for j in Data.rename.split(","):
            if 'ring '+str(j) in Data.mod.keys().get_level_values(0) and j!='8':
                Data.nrename=input("Rename ring {} to?: ".format(j))
                Data.orename=str(list(Data.mod['ring '+str(j)].columns)[0])
                Data.mod.rename(columns={Data.orename:Data.nrename},level=1,inplace=True)
            elif j == 'title' or j == 'Title':
                Data.graphtitle=input("Rename current title: \x1B[3m{}\x1B[0m : ".format(Data.graphtitle))
            elif j == 'pid' or j == 'PID':
                 Data.prename=input("Rename {} to?: ".format(Data.mod.columns[1][1]))
                 Data.mod.rename(columns={str(list(Data.mod[str(j.upper())].columns)[0]):Data.prename},level=1,inplace=True)
            else:
                print(j,"is not a valid ring")
        print("Current labels:\n\nTitle of graph: {}\n".format(Data.graphtitle))
        for i in Data.mod.columns[1:]:print(str(i).replace("('","").replace("')","").replace("', '"," | "))
        Plot.draw()

class ByeFat:
    def mandy():
        Data.group1=[]
        Data.group2=[]
        print("Current rings:/n")
        for i in Data.mod.columns[1:]:print(str(i).replace("('","").replace("')","").replace("', '"," | "))
        Data.group = input("Which ring(s) do you want to group? ")
        for j in Data.group.split(","):
            if 'ring '+str(j) in Data.mod.keys().get_level_values(0):
                Data.groupi=input("Add ring {} to group 1 or 2?: ".format(j))
                print(type(Data.groupi))
                if Data.groupi=="1":
                    Data.group1.append("ring "+j)
                else:
                    Data.group2.append("ring "+j)
            else:
                print(j,"is not a valid ring")
        print(Data.group1,Data.group2)
        Data.mod['group1','Group 1 Avg.']=Data.mod[Data.group1].mean(axis=1)
        Data.mod['group2','Group 2 Avg.']=Data.mod[Data.group2].mean(axis=1)
        Data.mod['grdiff','Group difference 1-2']=Data.mod.group1-Data.mod.group2.values
        Data.mod['grdiff1','Group difference 2-1']=Data.mod.group2-Data.mod.group1.values
        Plot.draw()
        
    def ringavg(range,*redo):
        if not redo:
            Data.coords=Data.coords.append(Plot.clicknew(-1,'stepavg',"Please click on \"flat\" area right before temperature change.\nPress enter to stop accumulating points")[-1])
        Data.coords=Data.coords[~Data.coords.index.duplicated(keep='last')]
        Data.coords['x0']=(Data.coords.x-(range/9))
        Data.coords=Data.coords.astype(int)
        for i in Data.coords.index[Data.coords.index.str.contains('step')]:
              Data.corr[i]=pd.DataFrame(Data.mod.loc[(Data.coords.loc[i].xindex)-range:Data.coords.loc[i].xindex,~Data.mod.columns.isin(['time'],level=1)].mean())
              print(f"Calculated avg per ring at t={Data.coords.loc[i].x}:\n{Data.corr[i]}")
        
        Plot.draw()

class Plot:
    def draw(*x):
        plt.clf()
        #plt.ion()
        plt.plot(Data.mod.time,Data.mod.iloc[:,~Data.mod.columns.isin(['time'],level=1)],linewidth='1')
        plt.xlabel(Data.timelabel);plt.ylabel(Data.ylabel);plt.title(Data.graphtitle)
        plt.minorticks_on()
        plt.grid(which='major',alpha=0.5);plt.grid(which='minor',alpha=0.3,linestyle="--")
        for i in Data.coords.index:
            if any(x not in ['cut','trim'] for x in i):
                if 'slope' in i:
                    if 'slope0' in i:
                        plt.axvline(Data.coords.x.loc[i],c='black',linestyle='--', linewidth='1', label="Drift correction")
                    else:
                        plt.axvline(Data.coords.x.loc[i],c='black',linestyle='--', linewidth='1')
                elif 'bubble' in i:
                    if 'bubble0' in i:
                        plt.axvline(Data.coords.x.loc[i],c='blue',linestyle='-.', linewidth='1', label="Jump correction")
                    else:
                        plt.axvline(Data.coords.x.loc[i],c='blue',linestyle='-.', linewidth='1')
                elif 'zero' in i:
                    if 'zero0' in i:
                        plt.axvline(Data.coords.x.loc[i],c='red',linestyle='dotted', linewidth='1', label="Zero correction")
                    else:
                        plt.axvline(Data.coords.x.loc[i],c='red',linestyle='dotted', linewidth='1')
                elif 'stepavg' in i:
                    if 'stepavg0' in i:
                        plt.axvline(Data.coords.x.loc[i],c='green',linestyle='solid', linewidth='1', label="Step value")
                        plt.axvline(Data.coords.x0.loc[i],c='green',linestyle='dotted', linewidth='1')
                    else:
                        plt.axvline(Data.coords.x.loc[i],c='green',linestyle='solid', linewidth='1')
                        plt.axvline(Data.coords.x0.loc[i],c='green',linestyle='dotted', linewidth='1')
                ax = plt.gca().add_artist(plt.legend(loc='center left', bbox_to_anchor=(1,.1),fancybox=True, shadow=True, ncol=1))
        plt.legend(Data.mod.keys().get_level_values(1)[1:],
                    loc='center left', bbox_to_anchor=(1,.5),
                    fancybox=True, shadow=True, ncol=1)
        plt.draw()
        return(0,f"\nOK: Plotted {Data.filetype} \"{Data.filename}\"")


    # def click():
    #     Plot.draw()
    #     Data.coords=pd.DataFrame(plt.ginput(3,timeout=60,mouse_add=3,mouse_pop=2,mouse_stop=None),columns=['x','y']).astype(int)
    #     if len(Data.coords) < 3 or len(Data.coords.x[(Data.coords.x <0) | (Data.coords.x > int(Data.mod.time.max()))]) > 0:
    #         print("\nOut of bounds or clicked incorrectly")
    #         del Data.coords
    #         Plot.click()
    #     Data.coords['tindex']=[int(Data.mod.time[Data.mod.time.iloc[:,0]==Data.coords.iloc[0,0]].index.values),
    #                            int(Data.mod.time[Data.mod.time.iloc[:,0]==Data.coords.iloc[1,0]].index.values),
    #                            int(Data.mod.time[Data.mod.time.iloc[:,0]==Data.coords.iloc[2,0]].index.values)]
    #     Plot.draw()


    def clicknew(inputs,name,*title):
        Plot.draw()
        titlef= f"{title[0]} \nSpacebar or right mouse button to select, Backspace to remove"
        plt.title(titlef)
        if title:
            print(titlef)
        df=pd.DataFrame(plt.ginput(inputs,timeout=60,mouse_add=3,mouse_pop=None,mouse_stop=None),columns=['x','y']).astype(int).rename(index = lambda x: str(name) + str(x))
        if df.x.min() < Data.mod.time.min()[0] or df.x.max() > Data.mod.time.max()[0] or df.empty:
            print("Error: Out of bounds! Try again.")
            return(Plot.clicknew(inputs,name,*title))
        df.x.sort_values()
        df['xindex'] = Data.indexconv(list(df.x.values))
        return(0,"OK:",df)

class Rfilter:
    def bfilter(N,Wn,*x):
        b, a = signal.butter(N, Wn,*x)
        for i in range(len(Data.mod.columns)-1):
            Data.mod[Data.mod.columns[i+1]]= signal.filtfilt(b, a, Data.mod.iloc[:,i+1])
        Plot.draw()
    def rolling(*x):
        if not x:x=[100,]
        Data.mod.iloc[:,1:]=Data.mod.iloc[:,1:].rolling(x[0]).mean()
        Plot.draw()
    def bubble(*rings):
        Data.coords=Data.coords.append(Plot.clicknew(2,'bubble',"Please click left and right bound for bubble detection")[-1])
        Data.coords=Data.coords[~Data.coords.index.duplicated(keep='last')]
        Data.filter=Data.mod.copy(deep=True)
        Data.filter.drop(range(Data.coords.xindex['bubble1']+1,len(Data.filter.index)),axis=0,inplace=True)
        Data.filter.drop(range(Data.filter.index[0],Data.coords.xindex['bubble0']),axis=0,inplace=True)
        Data.filter.fillna(value=0,inplace=True)
#        plt.clf()
        b, a = signal.butter(1, .1,'high')
        # for i in range(len(Data.mod.columns[~Data.mod.columns.isin(['time'],level=0)])-1):
        #     Data.filter[Data.filter.columns[i+1]] = signal.filtfilt(b, a, Data.filter.iloc[:,i+1])
        # b, a = signal.butter(1, .1,'low')

        for i in range(len(Data.mod.columns[~Data.mod.columns.isin(['time','Reference ring'],level=1)])):
            Data.filter[Data.filter.columns[i+1]] = signal.filtfilt(b, a, Data.filter.iloc[:,i+1]).round(0)
            # fix dat hij zoekt naar begin van de slope voor de min en achter de max ipv een vast waarde +5/-5
        #     plt.plot(Data.mod.time.loc[Data.filter.iloc[:,i+1].idxmax()],Data.mod.iloc[Data.filter.iloc[:,i+1].idxmax(),i+1],'go')
        #     plt.plot(Data.mod.time.loc[Data.filter.iloc[:,i+1].idxmin()],Data.mod.iloc[Data.filter.iloc[:,i+1].idxmin(),i+1],'ro')
        #     plt.plot(Data.mod.time.loc[Data.filter.iloc[:,i+1].idxmax()],Data.filter.iloc[:,i+1].loc[Data.filter.iloc[:,i+1].idxmax()]-100,'go')
        #     plt.plot(Data.mod.time.loc[Data.filter.iloc[:,i+1].idxmin()],Data.filter.iloc[:,i+1].loc[Data.filter.iloc[:,i+1].idxmin()]-100,'ro')
        #     print(Data.filter.columns[i+1][0],"max x,y",Data.mod.time.loc[Data.filter.iloc[:,i+1].idxmax()][0],Data.mod.iloc[Data.filter.iloc[:,i+1].idxmax(),i+1],"min x,y",Data.mod.time.loc[Data.filter.iloc[:,i+1].idxmin()][0],Data.mod.iloc[Data.filter.iloc[:,i+1].idxmin(),i+1])
            Data.mod.iloc[Data.filter.iloc[:,i+1].idxmin():,i+1]=Data.mod.iloc[Data.filter.iloc[:,i+1].idxmin():,i+1]-(
                Data.mod.iloc[Data.filter.iloc[:,i+1].idxmax(),i+1]-Data.mod.iloc[Data.filter.iloc[:,i+1].idxmin(),i+1]
                )

        """
        Data.mod.bubble=Data.mod.iloc[Data.bubble.tindex[0]:Data.bubble.tindex[1],1:].diff(100).diff(100).fillna(0)
        Data.mod.bubble.max()
        for loop per ring Data geeft '0'
        Data.mod.bubble.loc[Data.mod.bubble.iloc[:,0].round(0).gt(0) == True].index.values[0]
        max Datapunt

        Data.mod.bubble.loc[Data.mod.bubble.loc[Data.mod.bubble.iloc[:,4].round(0).gt(0) == True].index.values[0]:Data.mod.bubble[Data.mod.bubble.iloc[:,4]==Data.mod.bubble.iloc[:,4].max()].iloc[:,4].index.values[0]].iloc[:,4]

        """
        # plt.plot(Data.mod.time,Data.mod.iloc[:,~Data.mod.columns.isin(['time'],level=1)],linewidth='1')
        # plt.plot(Data.filter.time,(Data.filter.iloc[:,1:]-100))
        # plt.draw()
        Plot.draw()


# #Data.read("PID meting 9 aan tatp.csv")
# Data.read("BYE Fat/MRR 6/23-12-2021-442-MRR chip 6 temp meting 0,5 graden stappen 23-12.xls")
# Data.graphtitle="MRR chip 6 temp meting 0,5 graden stappen"
# Rings.sub(8)
# Rfilter.rolling()
Data.read("C:\\Users\\ASUS\\Downloads\\20211112\\Raw Data\\12-11-2021-376- ((fys ab- 12-11-2021)_RBS.xls")

# def test():
#     return(print("test"))


# while True:
#     print("Commands:\n\n *Read")
#     command = input('Please choose an option from the menu')

#     if command == "read":
#         out=Data.read(input("input filename:"))
#     if command == "Plotrea":
#         out=Plot.draw()




#     if command =='quit':
#         break
