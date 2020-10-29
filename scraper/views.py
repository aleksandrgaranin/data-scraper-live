from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from django.http import HttpResponseRedirect,HttpResponse
from .models import Date
import csv
import numpy as np



# Create your views here.

def scrape(request):
    if request.method == "POST":
        
        pageTue = requests.get('https://www.tsa.gov/coronavirus/passenger-throughput?page=0');
        pageOne = requests.get('https://www.tsa.gov/coronavirus/passenger-throughput?page=1');
        soupOne = BeautifulSoup(pageOne.text, 'html.parser');
        soupTue = BeautifulSoup(pageTue.text, 'html.parser');

        rowsOne =[]    
        rowsTue =[]      
        zOne = 0
        zTue = 0
        trsOne = soupOne.find_all('tr')
        trsTue = soupTue.find_all('tr')
        trsOne = trsOne[1:]
        trsTue = trsTue[1:]
       
        for tr in trsOne: # for every table row
            rowsOne.append([td.get_text(strip=True) for td in tr.find_all('td')]) # data row
        
        for tr in trsTue: # for every table row
            rowsTue.append([td.get_text(strip=True) for td in tr.find_all('td')]) # data row
        
        for row in rowsOne:
            if row == []:
                rowsOne.remove(row)      
            zOne=zOne+1

        for row in rowsTue:
            if row == []:
                rowsTue.remove(row)      
            zTue=zTue+1
        
        rowsOne = rowsOne[::-1]
        rowsTue = rowsTue[::-1]
        
        for i in range(zOne):
            date_raw = rowsOne[ i ][ 0 ].replace("/","")
            d = "0"
            print(date_raw)
            if len(date_raw) == 7:
                if date_raw[:2] == "10" or date_raw[:2] == "11" or date_raw[:2] == "12":
                    if len(date_raw) == 7:
                        y = date_raw[ 3: ]
                        date_mod = y + "-" + date_raw[ :1 ]+ d +"-" + date_raw[ 2:3 ]
                    else:
                        d = date_raw[:2] + d + date_raw[2:]
                        y = date_raw[ 3: ]
                        date_mod = y + "-" + date_raw[ :1 ]+ "-" + date_raw[ 2:3 ]
                else:
                    d = d + date_raw
                    y = d[ 4: ]
                    date_mod = y + "-" + d[:2 ] + "-" + d[ 2:4 ]
            elif len(date_raw) == 6:                
                dat = d + date_raw[ 0 ] + d + date_raw[ 1: ]    
                y = dat[ 4: ]                            
                date_mod = y + "-" + dat[ :2 ] + "-" + dat[ 2:4 ] 
            else:
                y = date_raw[ 4: ]
                date_mod = y + "-" + date_raw[ :2 ]+ "-" + date_raw[ 2:4 ]
            
            date = date_mod
            print(date)
            today = int(rowsOne[ i ][ 1 ].replace(",",""))
            year_ago = int(rowsOne[ i ][ 2 ].replace(",",""))
            
            today_day_before = int(rowsOne[ i-1 ][ 1 ].replace(",",""))
            year_ago_day_before = int(rowsOne[ i-1 ][ 2 ].replace(",",""))
            
            difference = round(float((today / year_ago) * 100),2)
            if i==0:
                abs_diff =0
            else:
                abs_diff = difference - round(float((today_day_before / year_ago_day_before) * 100),2) 
                abs_diff = round(abs_diff, 2)

            if Date.objects.all() is not None:
                num_results = Date.objects.filter(date = date).count()
                if num_results >=1:
                    pass
                else:
                    Date.objects.create(date=date,today=today,year_ago=year_ago,difference=difference,absolute=abs_diff)

        for i in range(zTue):
            date_raw = rowsTue[ i ][ 0 ].replace("/","")
            d = "0"
            print(date_raw)
            if len(date_raw) == 7:
                if date_raw[:2] == "10" or date_raw[:2] == "11" or date_raw[:2] == "12":
                    if len(date_raw) == 7:
                        y = date_raw[ 3: ]
                        date_mod = y + "-" + date_raw[ :1 ]+ d +"-" + date_raw[ 2:3 ]
                    else:
                        d = date_raw[:2] + d + date_raw[2:]
                        y = date_raw[ 3: ]
                        date_mod = y + "-" + date_raw[ :1 ]+ "-" + date_raw[ 2:3 ]
                else:
                    d = d + date_raw
                    y = d[ 4: ]
                    date_mod = y + "-" + d[:2 ] + "-" + d[ 2:4 ]
            elif len(date_raw) == 6:                
                dat = d + date_raw[ 0 ] + d + date_raw[ 1: ]    
                y = dat[ 4: ]                            
                date_mod = y + "-" + dat[ :2 ] + "-" + dat[ 2:4 ] 
            else:
                y = date_raw[ 4: ]
                date_mod = y + "-" + date_raw[ :2 ]+ "-" + date_raw[ 2:4 ]
            
            date = date_mod
            print(date)
            today = int(rowsTue[ i ][ 1 ].replace(",",""))
            year_ago = int(rowsTue[ i ][ 2 ].replace(",",""))
            
            today_day_before = int(rowsTue[ i-1 ][ 1 ].replace(",",""))
            year_ago_day_before = int(rowsTue[ i-1 ][ 2 ].replace(",",""))
            
            difference = round(float((today / year_ago) * 100),2)
            if i==0:
                abs_diff =0
            else:
                abs_diff = difference - round(float((today_day_before / year_ago_day_before) * 100),2) 
                abs_diff = round(abs_diff, 2)

            if Date.objects.all() is not None:
                num_results = Date.objects.filter(date = date).count()
                if num_results >=1:
                    pass
                else:
                    Date.objects.create(date=date,today=today,year_ago=year_ago,difference=difference,absolute=abs_diff)
            else:
                Date.objects.create(date=date,today=today,year_ago=year_ago,difference=difference,absolute=abs_diff)                        
        return HttpResponseRedirect('/')
    else:
        data_all = Date.objects.all()
        data_all = sorted(data_all, key= lambda u: u.date )

    return render(request, 'scraper/result.html',{'data_all':data_all})

def clear(request):
    Date.objects.all().delete()
    return render(request,'scraper/result.html')



def csv_database_write(request):
    # Get all data from Date Databse Table
    dates = Date.objects.all()
    sortedDates = sorted(dates, key= lambda u: u.date )
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="csv_dates_dbase_write.csv"'

    writer = csv.writer(response)
    writer.writerow(['date', 'this_year', 'last_year', 'difference', 'absolute'])

    for date in sortedDates:
        writer.writerow([date.date, date.today, date.year_ago, date.difference, date.absolute])

    return response
    

