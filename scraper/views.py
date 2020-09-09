from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from django.http import HttpResponseRedirect,HttpResponse
from .models import Date
import csv



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
        
        rows = rows[::-1]

        for i in range(z):
            date_raw = rows[ i ][ 0 ].replace("/","")
            d = "0"
            if len(date_raw) == 7:
                d = d + date_raw
                y = d[ 4: ]
                date_mod = y + "-" + d[:2 ] + "-" + d[ 2:4 ]
            elif len(date_raw) == 6:                
                dat = d + date_raw[ 0 ] + d + date_raw[ 1: ]    
                y = dat[ 4: ]
                print(dat)            
                date_mod = y + "-" + dat[ :2 ] + "-" + dat[ 2:4 ] 
            else:
                y = date_raw[ 3: ]
                date_mod = y + "-" + date_raw[ :1 ]+ "-" + date_raw[ 2:3 ]
            date = date_mod
            today = int(rows[ i ][ 1 ].replace(",",""))
            year_ago = int(rows[ i ][ 2 ].replace(",",""))
            
            today_day_before = int(rows[ i-1 ][ 1 ].replace(",",""))
            year_ago_day_before = int(rows[ i-1 ][ 2 ].replace(",",""))
            
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
    

