from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from django.http import HttpResponseRedirect,HttpResponse
from .models import Date
import csv
import sqlite3


# Create your views here.

def scrape(request):
    if request.method == "POST":

        page = requests.get('https://www.tsa.gov/coronavirus/passenger-throughput')
        soup = BeautifulSoup(page.text, 'html.parser')

        rows =[]        
        z = 0
        trs = soup.find_all('tr')
        trs = trs[1:]

        for tr in trs: # for every table row
            rows.append([td.get_text(strip=True) for td in tr.find_all('td')]) # data row
        
        for row in rows:
            if row == []:
                rows.remove(row)      
            z=z+1
        
        for i in range(z):
            date_raw = rows[i][0].replace("/","")
            d="0"
            if len(date_raw)==7:
                d = d+date_raw
                y = d[4:]
                date_mod = y + "-" +d[:2] + "-" + d[2:4]
            elif len(date_raw)==6:
                dat = date_raw[0]+"0"+date_raw[2:] 
                d = d+dat
                date_mod = y + "-" +d[:2] + "-" + d[3:5]
            else:
                y = date_raw[3:]
                date_mod = y+"-"+date_raw[:1]+"-"+date_raw[2:3]
            date = date_mod
            today = int(rows[i][1].replace(",",""))
            year_ago = int(rows[i][2].replace(",",""))
            difference = round(float((today/year_ago)*100),2)
            
            Date.objects.create(date=date,today=today,year_ago=year_ago,difference=difference)
        return HttpResponseRedirect('/')
    else:
        data_all = Date.objects.all()

    return render(request, 'scraper/result.html',{'data_all':data_all})

def clear(request):
    Date.objects.all().delete()
    return render(request,'scraper/result.html')



def csv_database_write(request):
    # Get all data from Date Databse Table
    dates = Date.objects.all()

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="csv_dates_dbase_write.csv"'

    writer = csv.writer(response)
    writer.writerow(['date', 'this_year', 'last_yeat', 'difference', 'absolute'])

    for date in dates:
        writer.writerow([date.date, date.today, date.year_ago, date.difference, date.absolute])

    return response
    

