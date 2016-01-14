#Python Backend for website
from flask import Flask, render_template, redirect, request
from bokeh.plotting import figure, show, output_file, vplot
from bokeh.embed import autoload_server, components
from bokeh.session import Session
from bokeh.document import Document

app=Flask(__name__)

import urllib2
import json
import pandas as pd
import numpy as np
import os
import sqlite3


@app.route('/')
def main():
    return redirect('/index_Main')

def plotbokeh(nodename):
    conn=sqlite3.connect('misodata.db')
    npriceseries=pd.read_sql('SELECT DATE, PRICE FROM LMPdata WHERE NODE="%s" AND DATE>"2015-09-20"' %(nodename),conn)
    conn.close()
    return npriceseries

def plotbokehcomp(node1, node2):
    conn=sqlite3.connect('misodata.db')
    datestart, datefinish = "2015-09-25","2015-10-01"
    comppriceseries=pd.read_sql('SELECT DATE, SUM(CASE WHEN NODE = "%s" THEN PRICE ELSE -1.0 * PRICE END) As DIFF_COST FROM LMPdata WHERE (NODE="%s" OR NODE="%s") AND (DATE>"%s" AND DATE<"%s") GROUP BY DATE' %(node1, node1, node2,datestart,datefinish),conn)
    conn.close()
    return comppriceseries
    
    

@app.route('/index_Main',methods=['GET','POST'])
def index_Main():
    if request.method =='GET':
        #conn=sqlite3.connect('misodata.db')
        #A=pd.read_sql('SELECT * FROM LMPdata LIMIT 5',conn)
        #conn.close()
        #B=A.loc[0]['NODE']
        return render_template('/Milestone_Main.html', Nodename="",node1n="",node1s="",node1t="")
    else:
        node=request.form['nodename']
        NODE_info=pd.read_csv('N_info.csv')
        #node1=request.args.get("node1")
        #Hval2=Hval.loc[0]['NODE_NAME']
        #NODE_info=pd.DataFrame({'NODE':['AMIL.EDWARDS2','AMMO.LABADIE1'],'STATE':['IL','MO'],'TYPE':['GEN','GEN']})
        if any(NODE_info.NODE_NAME==node)==False:
            nodeout=node+' is not a Node name'
            return render_template('Milestone_Main.html', Nodename=nodeout)
        else:
            nodefind=NODE_info.loc[NODE_info['NODE_NAME']==node].index.tolist()[0]
            node1n=NODE_info.loc[nodefind]['NODE_NAME']
            node1s=NODE_info.loc[nodefind]['STATE']
            node1t=NODE_info.loc[nodefind]['TYPE']
            #if nodenum=='1nodes':
            nodenum=request.form['nodenum']
            if nodenum=='1nodes':
                
                dfprice=plotbokeh(node1n)
                bdate=np.array(dfprice['DATE'], dtype=np.datetime64)
                bprice=np.array(dfprice['PRICE'])
                p1=figure(x_axis_type='datetime')
                p1.line(bdate,bprice)
                #np.array(
                #,dtype=np.datetime64)
                p1.title = ' Energy Prices for ' + node1n
                p1.xaxis.axis_label = "Date"
                p1.yaxis.axis_label = "Price/MWh"
                script, div = components(p1)
            else:
                node2=request.form['nodename2']
                dfprice=plotbokehcomp(node1n,node2)
                bdate=np.array(dfprice['DATE'], dtype=np.datetime64)
                bprice=np.array(dfprice['DIFF_COST'])
                p1=figure(x_axis_type='datetime')
                p1.line(bdate,bprice)
                p1.title = "Temporal Energy Price Differences"
                p1.xaxis.axis_label = "Date"
                p1.yaxis.axis_label = "Price/MWh (+Node1,-Node2)"
                script, div = components(p1)
                #script=bdate
                #div=bprice
                #return render_template('/Milestone_Main.html',Nodename="",node1n=node1n,node1s=node1s,node1t=node1t)
            #else:
            #    script='empty'
            #    div='empty'
            return render_template('Onenode_plot.html',node1n=node1n, script=script, div=div)

#@app.route('/Onenode_plot',methods=['GET','POST'])
#def Onenode_plot():
#    return render_template('Onenode_plot.html',node1n=node1n)

    

if __name__ == '__main__':
    app.run(port=33507)
