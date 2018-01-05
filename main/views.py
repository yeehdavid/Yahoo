from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import StreamingHttpResponse
import datetime
import os
#import pandas as pd
import pymysql
from main.models import Task
# Create your views here.
def index(request):
    task = Task.objects.all().order_by('-created_time')
    return render(request, 'index.html', context={'tasks':task})


def create(request):
    return render(request, 'create_task.html')

def upload(request):
    if request.method == "POST":  # 请求方法为POST时，进行处理
        myFile = request.FILES.get("myfile", None)  # 获取上传的文件，如果没有文件，则默认为None
        if not myFile:
            return HttpResponse("no files for upload!")
        destination = open(os.path.join("/home/david", "codes.csv"), 'wb+')  # 打开特定的文件进行二进制的写操作
        for chunk in myFile.chunks():  # 分块写入文件
            destination.write(chunk)
        destination.close()
        #-------------------------------
        datetime_ = datetime.datetime.now()
        conn = pymysql.connect(host='127.0.0.1', user='root', passwd='344126509', db='yahoo', charset='utf8')
        cur = conn.cursor()
        cur.execute("INSERT INTO main_task (created_time, status, success, date_time) VALUES (%s,%s,%s,%s)",(datetime_, 0, int(0),str(datetime_).replace(' ','')))
        cur.connection.commit()
        os.makedirs('/home/david/codes_historical_data/'+str(datetime_).replace(' ',''))
        #-------------------------------

        return HttpResponse("任务创建成功！")


def download(request):
    # do something...
    datetime_ =  request.GET['datetime']
    #datetime_='2017-12-15 16:27:14.451398'
    def file_iterator(file_name, chunk_size=512):
        with open(file_name,'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    the_file_name = '/home/david/codes_historical_data/'+datetime_+'.zip'

    #the_file_name = '/home/david/codes_historical_data/2017-12-1517:19:28.892712.zip'
    response = StreamingHttpResponse(file_iterator(the_file_name))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(datetime_+'_data.zip')

    return response

