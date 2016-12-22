# -*- coding: utf-8 -*-
"""
Created on Thu Dec 08 14:57:44 2016

@author: joseph.chen
"""

import codecs
import pandas as pd
import requests
import datetime
import time
import random
from bs4 import BeautifulSoup
import sys

#DOWNLOAD_URL = 'http://www.soccerassociation.com/0/0607/A20061021.htm'
DOWNLOAD_URL = 'http://www.soccerassociation.com'
WEEK = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
MONTH = ({"January":1,"February":2,"March":3,"April":4,"May":5,"June":6,
          "July":7,"August":8,"September":9,"October":10,"November":11,
          "December":12})

def download_page(url):
    return requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) '+ 
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
    }).content


def parse_html(html):
    try:
        soup = BeautifulSoup(html,"lxml")
        
        #print soup.prettify()
        body = soup.body
        table_list = (body.contents[2].contents[1].contents[0].contents[0]
                      .contents[6].contents[2])
        for table in table_list.find_all("table"):
            #print [td.string for td in table.find_all("td")],'\n'
            if u"RESULTS" in [td.string for td in table.find_all("td")]:
                result_table = table
        
        result = ['RESULTS']
        for tr in result_table.select("tr")[1].select("tr"):
            td_list = tr.select("td")
            for td in td_list:
                if td.has_attr("class"):
                    if (td["class"][0]=="w"):
                        if td.string==None:
                            if td["bgcolor"]=="#ff0000":
                                result.append("w"+"None")
                            else:
                                result.append(td.string)
                        else:
                            try:
                                week = int(td.string)
                                result.append("w"+str(week))
                            except:
                                result.append(td.string)
                    else:
                        result.append(td.string)
                else:
                    result.append(td.string)
        return result
    except:
        return None


  
def parse_result(result): 
    
    df = pd.DataFrame(columns=["home_team_name","away_team_name",
                               "full_time_home_goal","full_time_away_goal",
                               "goal_times","match_date","week"])
    
    date_index = []
    match_index = []
    for n in range(len(result)):
        res = result[n]
        try:
            res_str = str(res)
        except:
            res_str = res
        # TODO [joseph]: There was a team called "Sheffield Wednesday" !   
        if any(wk+"," in res_str for wk in WEEK):
            date_index.append(n)
            
        if res_str[0:2] in ("w1","w2","w3","w4","w5","w6","w7","w8","w9","wN"):
            match_index.append(n)
    
#    for n in date_index:
#        print n, convert_date(result[n])

    for j,m in enumerate(match_index):
        
        k = -1
        while (-k<=len(date_index)):
            if m>date_index[k]:
                n = date_index[k]
                date = convert_date(result[n])
                break
            k -= 1
      
        
        try:
            goal_result = result[m:match_index[j+1]]           
            #print goal_result       
        except:
            goal_result = result[m:]
            #print goal_result
           
        week = goal_result[0][1:]
        home_name,away_name = goal_result[1],goal_result[3]
        home_goal,away_goal = goal_result[2].split("-")
        goal_times = {"home":[],"away":[]}
        try:
            data = goal_result[5:]
        except:
            data = []
        
        while data:
            home_goal_time = data.pop(0)
                        
            if home_goal_time==None:
                data.pop(0)
                away_goal_time = data.pop(0)
                if away_goal_time!=None:
                    away_goal_player = data.pop(0)
                    goal_times["away"].append((away_goal_time,away_goal_player))
            elif home_goal_time[0] in ('0123456789'):
                home_goal_player = data.pop(0)
                goal_times["home"].append((home_goal_time,home_goal_player))
                data.pop(0)
                away_goal_time = data.pop(0)
                if away_goal_time!=None:
                    away_goal_player = data.pop(0)
                    #print away_goal_time,away_goal_player,"!!!\n"
                    goal_times["away"].append((away_goal_time,away_goal_player))
            else:
                continue
                
#         date,week,home_name,away_name,home_goal,away_goal,goal_times,'\n' 
        df.loc[m] = [home_name,away_name,home_goal,away_goal,goal_times,date,week]

    return df
    
def convert_date(date_str):
    '''convert a date string to standard format.

    Parameters
    ----------
    date_str: String
        including information of weekday & date
         
    Returns
    -------
    date_str2: String
        in the standard date format: 'YYYY-MM-DD' 
        
    Example
    -------
    input 
        date_str: "Saturday, 3 December 2016"
    output
        date_str2: "2016-12-03"
    ''' 
    date_str2 = None
    
    try:
        d,m,y = date_str.split(" ")[1].split(u"\xa0")
        date_str2 = "-".join([y,str(MONTH[m]),d])
    except:
        d,m,y = date_str.split(" ")[1:]
        date_str2 = "-".join([y,str(MONTH[m]),d])
    finally:
        if date_str2!=None:
            return date_str2
        else:
            sys.exit("Error: [convert_date] input date string incorrect")
        
def get_all_dates(start_year,end_year):
    begin = datetime.date(int(start_year),8,1)
    end = datetime.date(int(end_year),7,31)
    date_list = []
    for i in range((end - begin).days+1):
        day = begin + datetime.timedelta(days=i)
        date_list.append("".join(str(day).split("-")))
    return date_list           
            
def get_results(start_year,end_year,waiting_time=1):
    df = pd.DataFrame()
    
    season = start_year[2:]+end_year[2:]
    for date in get_all_dates(start_year,end_year):
        url = DOWNLOAD_URL+'/0/'+season+'/A'+date+'.htm'
        html = download_page(url)
        time.sleep(waiting_time*random.random())
        if html!='PAGE ERROR':
            result = parse_html(html)
            if result!=None:
                print date, url
                df1 = parse_result(result)
                df = pd.concat([df,df1])
    return df
    


if __name__ == '__main__':
    for year in range(2015,2016):
        start_year = str(year)
        end_year = str(year+1)
        print start_year, end_year
#        start_year = "2010"
#        end_year = "2011"
        
        writer = pd.ExcelWriter("goal_times_"+start_year+"_"+end_year+".xlsx")
        df = get_results(start_year,end_year,waiting_time=1)
        df.to_excel(writer,'goal_times',index=False)
        writer.save()
    


