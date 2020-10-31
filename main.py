import socket
import threading
import json
from time import sleep
s=socket.socket()
s.bind(('localhost',1111))
s.listen()
IP=socket.gethostname()
conn_list=[]
conn_name={}
def listen(conn,addr):
	while 1:

		# print(type(conn))
		data=conn.recv(1024).decode()
		print("Data=",data)
		jdata=json.loads(data)
		# msg=jdata["message"]
		with open("data.json","w") as f:
			json.dump(jdata,f,indent=4,sort_keys=True)
		print("Done writing json")



def client_handle(conn,addr):
    with open("data.json","rb") as f:
        data=f.read()
    conn.send(data)
    listen_thread=threading.Thread(target=listen,args=[conn,addr])
    listen_thread.start()


def start(s):
	while 1:
		print("[STARTING SERVER]")
		sleep(1)
		print(f"[STARTED] In {IP}")
		conn,addr=s.accept()
		conn_list.append(conn)
		print(f"[CONNECTED]:{addr}")
		client_thread=threading.Thread(target=client_handle,args=[conn,addr])
		client_thread.start()
start(s)
