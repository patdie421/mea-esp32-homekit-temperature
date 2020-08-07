import sys
import socket
import json
import argparse

HOST = 'localhost'
PORT = 8088
TOKEN = None

accessories={}
debug=False

def do_request(host, port, command):

   if debug: print("request:", command)
   client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   client.connect((host, port))
   n = client.send(str.encode(command))
   data=""
   client.settimeout(5.0)
   while(1):
      try:
         d = client.recv(1024).decode()
      except:
         break;
      if len(d) > 0:
         data=data+str(d)
      else:
         break

   if len(data)==0:
      if debug: print("no response")
      data=None
   else:
      if debug: print("Response:",data)
   client.close()
   return data


def get_device_type(HOST,PORT,TOKEN):
   message = TOKEN+':?'
   response = do_request(HOST,PORT,message).split(":",2)
   if response:
      return response
   else:
      return None


def get_token(HOST,PORT,accessory_name, accessory_mode):
   if accessory_mode=='R':
      if accessory_name in accessories:
         return str(accessories[accessory_name]["token"])
      else:
         return ""
   if accessory_mode=='C':
      message=":t"
      token=do_request(HOST,PORT,message)
      if token:
         accessories[accessory_name]={ "token": token }
         with open('accessories.json', 'w') as json_file:
            json.dump(accessories, json_file)
         return str(token)
      return ""


def esp_get_wifi(HOST,PORT,TOKEN):
   message = TOKEN+":w"
   response = do_request(HOST,PORT,message)
   return response


def esp_set_wifi(HOST,PORT,TOKEN,name,password):
   message = TOKEN+":W:"+name+"/"+password
   response = do_request(HOST,PORT,message)
   if response == "OK":
      return True
   else:
      return False


def esp_restart(HOST,PORT,TOKEN):
   message = TOKEN+":r"
   response = do_request(HOST,PORT,message)
   if response == "OK":
      return True
   else:
      return False

def display_help(accessory_type, accessory_mode):
   print("help")


try:
   with open('accessories.json') as json_file:
      accessories=json.load(json_file)
except:
   with open('accessories.json', 'w') as json_file:
      json.dump(accessories, json_file)


def interactive():
   global TOKEN
   if sys.stdin.isatty():
      prompt="["+accessory_mode+"]"+accessory_type+":"+accessory_name+">"
   else:
      prompt=""
   while(1):
      try:
         if sys.version_info.major >= 3:
            cmd=input(prompt)
         else:
            cmd=raw_input(prompt)
      except:
         break
      lowercmd=cmd.lower()
      if len(cmd)>0:
         if cmd=='?' or lowercmd=='help':
            display_help(accessory_type, accessory_name)
         elif lowercmd=="quit" or lowercmd=="exit" or lowercmd=="end":
            break
         else:
            response=do_request(HOST,PORT,TOKEN+":"+cmd)
            if response:
               print(str(response))
            else:
               print(response)
   sys.exit(0)

parser = argparse.ArgumentParser()
parser.add_argument("--host", help="hostname or IP address of esp device", default="192.168.4.1")
parser.add_argument("--port", help="port of esp device")
parser.add_argument("--token", help="token")
parser.add_argument("command", help="port of esp device", nargs="*")
args=parser.parse_args()

if debug: print(args)

if args.host:
   HOST=args.host
if args.port:
   PORT=args.port

accessory_type, accessory_name, accessory_mode=get_device_type(HOST, PORT, "")

if args.token:
   TOKEN=args.token
else:
   TOKEN=get_token(HOST,PORT,accessory_name,accessory_mode)
   if TOKEN==None:
      print("can't get token")
      sys.exit(0)

if args.command:
   for i in  args.command:
      print(do_request(HOST, PORT, i))
else:
   interactive()

# esp_get_wifi(HOST,PORT,TOKEN)
# esp_set_wifi(HOST,PORT,TOKEN,"toto","titi")
# esp_get_wifi(HOST,PORT,TOKEN)
# esp_restart(HOST,PORT,TOKEN)
