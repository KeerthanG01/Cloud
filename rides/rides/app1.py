
from flask import Flask, render_template,\
jsonify,request,abort
import requests
from datetime import datetime
from flask_mysqldb import MySQL
app=Flask(__name__)
app.config['MYSQL_HOST'] = 'cloud_db1_1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD']='password'
app.config['MYSQL_DB'] = 'rides'
app.config['MYSQL_PORT'] = 3306
mysql = MySQL(app)

@app.route("/api/v1/db/clear",methods=["POST"])
def clear_db():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM rides_m")
        mysql.connection.commit()
        cursor.close()
        return " ",200
    except Exception as e:
        return " ",404
@app.route('/api/v1/_count', methods=["GET"])
def http_count():
        if(request.method == 'GET'):
                 dic={}
                 dic["flag"]=7
                 resp = requests.post('http://127.0.0.1:80/api/v1/db/read', json = dic)
                 res= resp.json()["result"]
                 if(len(res) == 0):
                          return " ",204
                 else:
                        return "["+str(res[0])+"]",200
        else:
                " ",405
@app.route('/api/v1/_count', methods=["DELETE"])
def reset_count():
    if(request.method == "DELETE"):
        dic={}
        dic["flag"]=8
        y=requests.post("http://127.0.0.1:80/api/v1/db/write",json=dic)
        res=y.json()["result"]
        if(res==-1):
            return " ",400
        else:
            return " ",200
    else:
        return " ",405

@app.route("/api/v1/db/write",methods=["POST"])
def write_to_db():
    flag=request.get_json()["flag"]
    if(flag == 1):
        username=request.get_json()["username"]
        password=request.get_json()["password"]
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("INSERT INTO users_m (Name,Password) values (%s,%s)", (username,password))
            dic={}
            dic["result"]=1
            mysql.connection.commit()
            cursor.close()
            return dic
        except:
            dic={}
            dic["result"]=2
            mysql.connection.commit()
            cursor.close()
            return dic
    if(flag==2):
        username=request.get_json()["username"]
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM users_m WHERE Name=%s",(username,))
        dic={}
        dic["result"]=1
        mysql.connection.commit()
        cursor.close()
        return dic
    if(flag==3):
        dic={}
        source=request.get_json()["source"]
        destination=request.get_json()["destination"]
        username=request.get_json()["created_by"]
        timestamp=request.get_json()["timestamp"]
        cursor= mysql.connection.cursor()
        src=int(source)
        dst=int(destination)
        if src < 0 or dst > 198 :
            dic["result"] = -1
            return dic
        if(source == destination):
            dic["result"]=0
            return dic
        else:
            cursor.execute("INSERT INTO rides_m(Source,Destination,Created_by,timestamp) values (%s,%s,%s,%s)",(source,destination,username,timestamp))
            dic["result"]=1
            mysql.connection.commit()
            mysql.connection.commit()
            cursor.close()
        return dic
    if(flag==4):
        username=request.get_json()["username"]
        rideid=request.get_json()["rideid"]
        cursor=mysql.connection.cursor()
        cursor.execute("INSERT INTO ridetable(ID,Username) values(%s,%s)",(rideid,username));
        mysql.connection.commit()
        cursor.close()
        dic={}
        dic["result"]=1
        return dic
    if(flag==6):
        print("Hello")
        rideid=request.get_json()["rideid"]
        cursor=mysql.connection.cursor()
        cursor.execute("DELETE FROM rides_m WHERE ID=%s",(rideid,))
        print("World")
        mysql.connection.commit()
        cursor.close()
        dic={}
        dic["value"]=1
        print(dic)
        return dic
    if(flag==7):
        dic={}
        cursor=mysql.connection.cursor()
        try:
             cursor.execute("UPDATE calls SET count=count+1")
             dic["result"]=1
        except Exception as e:
            dic["result"]=-1
        mysql.connection.commit()
        cursor.close()
        return dic
    if(flag==8):
        dic={}
        cursor=mysql.connection.cursor()
        try:
             cursor.execute("UPDATE calls SET count=0")
             dic["result"]=1
        except Exception as e:
            dic["result"]=-1
        mysql.connection.commit()
        cursor.close()
        return dic

@app.route("/api/v1/db/read",methods=["POST"])
def read_from_db():
    flag=request.get_json()["flag"]
    if flag==1:
        source=request.get_json()["source"]
        destination=request.get_json()["destination"]
        time=datetime.now()
        if source==destination:
            dic={}
            dic["value"]= -1
            return dic
        src=int(source)
        dst=int(destination)
        if src < 0 or dst > 198 :
            dic={}
            dic["value"] = -2
            return dic
        cursor =mysql.connection.cursor()
        cursor.execute("SELECT * FROM rides_m WHERE Source = %s and Destination= %s",(source,destination))
        row=cursor.fetchall()
        if(len(row)==0):
            dic={}
            dic["value"]=0
            return dic
        else:
            dic={}
            dic["value"]= -3
            li=[]
            for x in row:
                di={}
                timestamp=str(x[4])
                print(timestamp)
                datetime_object = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                if(datetime_object > time):
                    di={}
                    dic["value"]=1
                    timestamp=datetime_object.strftime("%d-%m-%Y:%S-%M-%H")
                    di["rideId"]=x[0]
                    di["created_by"]=x[3]
                    #datetime_object = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                    timestamp=datetime_object.strftime("%d-%m-%Y:%S-%M-%H")
                    di["timestamp"]=timestamp
                    li.append(di)

            dic["1"]=li
            return dic


    if flag==4:
        cursor=mysql.connection.cursor()
        dic={}
        dic.clear()
        #li=[]
        rideid=request.get_json()["rideid"]
        username=request.get_json()["username"]
        y=requests.get(" http://CC-LoadBalancer-641901057.us-east-1.elb.amazonaws.com/api/v1/users", headers={'Origin':'http://18.210.146.113'})
        z=y.text
        if(username not in z):
            dic["1"] = 0
            #li.append(0)
        else:
            dic["1"] = 1
            #li.append(1)
        cursor.execute("SELECT * from rides_m where ID=%s",(rideid,))
        a=cursor.fetchone()
        if(len(a)==0):
            dic["2"]=0
            #li.append(0)
        else:
            dic["2"]=1
            #li.append(1)
        cursor.close()
        #dic["1"]=li
        return dic

    if flag==5:
        dic={}
        dic["1"]=0
        rideid=request.get_json()["rideid"]
        cursor=mysql.connection.cursor()
        cursor.execute("SELECT * FROM rides_m WHERE ID=%s",(rideid,))
        a=cursor.fetchone()
        if(not(a)):
            dic["1"]=1
            return dic
        else:
            dic["rideId"]=rideid
            cursor.execute("SELECT * FROM rides_m WHERE ID=%s",(rideid,))
            a=cursor.fetchone()
            dic["created_by"]=a[3]
            cursor.execute("SELECT * FROM ridetable WHERE ID=%s",(rideid,))
            a=cursor.fetchall()
            li=[]
            for row in a :
                li.append(row[1])
            dic["users"]=li
            cursor.execute("SELECT * FROM rides_m WHERE ID=%s",(rideid,))
            a=cursor.fetchone()
            timestamp=str(a[4])
            datetime_object = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            timestamp=datetime_object.strftime("%d-%m-%Y:%S-%M-%H")
            dic["timestamp"]=timestamp
            dic["source"]=a[1]
            dic["destination"]=a[2]
            return dic
    if flag==6:
        rideid=request.get_json()["rideid"]
        cursor=mysql.connection.cursor()
        cursor.execute("SELECT * FROM rides_m WHERE ID=%s",(rideid,))
        a=cursor.fetchall()
        dic={}
        if len(a)==0:
            dic["1"]=1
        else:
            dic["1"]=0
        return dic

    if flag==7:
        cursor=mysql.connection.cursor()
        cursor.execute("SELECT count FROM calls")
        res=cursor.fetchall()
        l=[]
        for i in res:
            l.append(i[0])
        mysql.connection.commit()
        cursor.close()
        dic={}
        dic["result"]=l
        return dic
    if flag==9:
        cursor=mysql.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM rides_m");
        count=cursor.fetchone()[0]
        l=[]
        l.append(count)
        dic={}
        dic["result"]=l
        return dic
    else:
        username=request.get_json()["username"]
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users_m WHERE Name=%s", (username,))
        a=cursor.fetchall()
        if len(a)==0:
            dic={}
            dic["value"]=0
            cursor.close()
            return dic
        else :
            dic={}
            dic["value"]=1
            cursor.close()
            return dic


@app.route("/api/v1/rides",methods=["POST"])
def create_ride():
    dic={}
    dic["flag"]=7
    y=requests.post("http://127.0.0.1:80/api/v1/db/write",json=dic)
    res=y.json()["result"]
    if(res==-1):
        return " ",400
    dic.clear()
    if(request.method == "POST"):
        dic={}
        dic['flag']=3
        dic['created_by']=request.get_json()["created_by"]
        dic['source']=request.get_json()["source"]
        dic['destination']=request.get_json()["destination"]
        timestamp=request.get_json()["timestamp"]
        datetime_object = datetime.strptime(timestamp, '%d-%m-%Y:%S-%M-%H')
        timestamp=datetime_object.strftime("%Y-%m-%d:%H-%M-%S")
        dic['timestamp']=timestamp
        dic1={}
        dic1["flag"]=3
        dic1["username"]=request.get_json()["created_by"]
        x=requests.get(" http://CC-LoadBalancer-641901057.us-east-1.elb.amazonaws.com/api/v1/users", headers={'Origin':'http://18.210.146.113'})
        status=x.text
        if(dic['created_by'] not in status):
            return "User does not exist",400
        else:
            x=requests.post("http://127.0.0.1:80/api/v1/db/write",json=dic)
            status=x.json()["result"]
            if(status == -1):
                return "Invalid Source/Destination",400
            if(status==0):
                return "Invalid Source/Destination",400
            if(status ==1):
                return " ",201
    else:
        return " ",405

@app.route("/api/v1/rides",methods=["GET"])
def list_rides():
    dic={}
    dic["flag"]=7
    y=requests.post("http://127.0.0.1:80/api/v1/db/write",json=dic)
    res=y.json()["result"]
    if(res==-1):
        return " ",400
    dic.clear()
    if(request.method == "GET"):
        source = request.args['source']
        destination = request.args['destination']
        dic={}
        dic["flag"]=1
        dic["source"]=source
        dic["destination"]=destination
        x=requests.post("http://127.0.0.1:80/api/v1/db/read",json=dic)
        status=x.json().get("value")
        if(status==0):
            return " ",204
        elif(status == -1):
            return "Invalid Source/Destination",400
        elif(status == -2):
            return "Invalid Source/Destination",400
        elif(status == -3):
            return " ",204
        else:
            dic=x.json()
            lis=dic.get("1")
            return jsonify(lis),200
    else:
        return " ",405

@app.route("/api/v1/rides/<rideid>",methods=["POST"])
def join_ride(rideid):
    dic={}
    dic["flag"]=7
    y=requests.post("http://127.0.0.1:80/api/v1/db/write",json=dic)
    res=y.json()["result"]
    if(res==-1):
        return " ",400
    dic.clear()
    if(request.method=="POST"):
        username=request.get_json()["username"]
        dic={}
        dic["flag"]=4
        dic["rideid"]=rideid
        dic["username"]=username
        x=requests.post("http://127.0.0.1:80/api/v1/db/read",json=dic)
        dic1=x.json()
        a=dic1["1"]
        b=dic1["2"]
        if(a==0 and b==1):
          return " ",204
        elif(a==1 and b==0):
          return " ",204
        elif(a==0 and b==0):
          return " ",204
        else:
          x=requests.post("http://127.0.0.1:80/api/v1/db/write",json=dic)
          status=x.json()["result"]
          if(status):
            return " ",200
          else:
            return " ",204
    else:
        return " ",405

@app.route("/api/v1/rides/<rideid>",methods=["GET"])
def list_ride_details(rideid):
    dic={}
    dic["flag"]=7
    y=requests.post("http://127.0.0.1:80/api/v1/db/write",json=dic)
    res=y.json()["result"]
    if(res==-1):
        return " ",400
    dic.clear()
    if(request.method=="GET"):
        dic={}
        dic["rideid"]=rideid
        dic["flag"]=5
        x=requests.post("http://127.0.0.1:80/api/v1/db/read",json=dic)
        a=x.json().get("1")
        if(a):
            return " ",204
        else:
            di={}
            di=x.json()
            del di["1"]
            return di,200
    else:
        return " ",405
@app.route("/api/v1/rides/count",methods=["GET"])
def rides_count():
    if(request.method=="GET"):
        dic={}
        dic["flag"]=9
        x=requests.post("http://127.0.0.1:80/api/v1/db/read",json=dic)
        l=x.json()["result"]
        return jsonify(l),200
    else:
        return " ",405
@app.route("/api/v1/rides/<rideid>",methods=["DELETE"])
def delete_ride(rideid):
    dic={}
    dic["flag"]=7
    y=requests.post("http://127.0.0.1:80/api/v1/db/write",json=dic)
    res=y.json()["result"]
    if(res==-1):
        return " ",400
    dic.clear()
    if(request.method=="DELETE"):
        dic={}
        dic["flag"]=6
        dic["rideid"]=rideid
        x=requests.post("http://127.0.0.1:80/api/v1/db/read",json=dic)
        a=x.json()["1"]
        if(a):
            return "Ride does not exist",400
        x=requests.post("http://127.0.0.1:80/api/v1/db/write",json=dic)
        a=x.json()["value"]
        if(a):
            return " ",200
    else:
        return " ",405

if __name__ == '__main__':
    app.debug=True
    app.run(host="0.0.0.0",port=80)