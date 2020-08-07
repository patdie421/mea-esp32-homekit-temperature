import sys
import socket
import signal

_server = None
accessory_name='test1'
accessory_mode='R'
accessory_token='dfsezzerdsfs'
accessory_password='555-55-555'
wifi_name=""
wifi_password=""

def signal_handler(sig, frame):
    if _server != None:
       _server.close()
    sys.exit(0)


def do_cmd(client,data):
   global wifi_name

   try:
      token,cmd=data.split(':',1)
   except:
      client.send("???")
      return None

   parameters=None
   try:
      cmd,parameters=cmd.split(':',1)
   except:
      pass

   print "<"+cmd+">"
   if cmd=='r':
      print token
      if accessory_mode=='C' or accessory_token==token:
         response="OK"
      else:
         response="BC"
   elif cmd=="W":
      try:
         name,password=parameters.split("/",1)
         wifi_name=name
         wifi_password=password
         response="OK"
      except:
         response="!!!"
   elif cmd=='?':
      response="SIM:"+accessory_name+":"+accessory_mode
   elif cmd=='w':
      response="WIFI_SSID="+wifi_name+"\nHOMEKIT_NAME="+accessory_name+"\nHOMEKIT_PASSWORD="+accessory_password+"\n"
   elif cmd=='t' and accessory_mode=='C':
      response=accessory_token
   else:
      response="???"
   print response
   client.send(response)


def server(port):

   server_addr=('0.0.0.0',port)
   _server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   _server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

   _server.bind(server_addr)
   _server.listen(1)

   while(True):
      connection, client_addr = _server.accept()
      data = connection.recv(1024)
      print data
      if data:
         do_cmd(connection,data)
      else:
         break
      connection.close()


signal.signal(signal.SIGINT, signal_handler)
server(8088)
