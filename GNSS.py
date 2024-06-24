import pigpio
import RGB1602
import io
import timeX
import math
import sys
import pynmea2
import serial
import difflib
import re
def main():
    regex="[\*]{1}[1234567890ABCDEF]{2}"
    checksum=re.compile(regex)
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=0.9)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
    lcd=RGB1602.RGB1602(16,2)
    RX=5 
    snr1=0
    snr2=0
    lat1=0
    lat_dir1=0
    lon1=0
    lon_dir1=0
    lat2=0
    lat_dir2=0
    lon2=0
    lon_dir2=0
    count = None
    data = None
    allowedmessages = ["GGA","GSV","RMC","GSA"]
    antenna_works=False
    GSVS=[]
    GSVS2=[]
    line = None
    parsed_message= None
    parsed_messages_list = None

    while 1:
        try:
                pi = pigpio.pi()
                pi.set_mode(RX, pigpio.INPUT)
                pi.bb_serial_read_open(RX, 9600, 8)
                openned_antenna2=True
        except KeyboardInterrupt:
                sys.exit()
        except:
                pi.bb_serial_read_close(RX)
                pi.stop()
                openned_antenna2=False
        try:
            line = sio.readline()
        except:
            pass

        if line:
            message_identifier=line[3:6]
            if line[0].startswith("$"):
               antenna_works=True
               parsed_message = pynmea2.parse(line)
               if message_identifier == allowedmessages[0]:
                        lat1=parsed_message.lat
                        lat_dir1=parsed_message.lat_dir
                        lon1=parsed_message.lon
                        lon_dir1=parsed_message.lon_dir
               if  message_identifier == allowedmessages[1]:
                        if parsed_message.msg_num==1:
                            snr1=0
                        msgcounter=parsed_message.num_messages
                       
msg_snr_list=[parsed_message.snr_1,parsed_message.snr_2,parsed_message.snr_3,parsed_message.snr_4]
for snr in msg_snr_list:
                            if snr:
                                GSVS.append(int(snr))
                            GSVS.sort(reverse=True)
if msgcounter == parsed_message.msg_num:
                            snr1=sum(GSVS[:5])
                            GSVS.clear()
if openned_antenna2:
                antenna_works=True
                count, data = pi.bb_serial_read(RX)
                if count>0:
                        line2 = data.decode("utf-8","ignore")
                        separatelines = line2.splitlines()
                        parsed_messages_list = [pynmea2.parse(separatelines[x]) for x in range(len(separatelines))  if separatelines[x].startswith("$GP") and re.fullmatch(checksum, separatelines[x][-3:])]
                        raw_messages_list_2 = [separatelines[x] for x in range(len(separatelines))  if separatelines[x].startswith("$GP") and re.fullmatch(checksum, separatelines[x][-3:])]
                        for x in range(len(parsed_messages_list)):
                                    if raw_messages_list_2[x][3:6] == allowedmessages[0]:
                                            lat2=parsed_messages_list[x].lat
                                            lat_dir2=parsed_messages_list[x].lat_dir
                                            lon2=parsed_messages_list[x].lon
                                            lon_dir2=parsed_messages_list[x].lon_dir
                                    if raw_messages_list_2[x][3:6]==allowedmessages[1]:
                                        msgcounter2=parsed_messages_list[x].num_messages
                                       
msg_snr_list=[parsed_messages_list[x].snr_1,parsed_messages_list[x].snr_2,parsed_messages_list[x].snr_3,parsed_messages_list[x].snr_4]
for snr2 in msg_snr_list:
                                            if snr2:
                                                GSVS2.append(int(snr2))
                                            GSVS2.sort(reverse=True)
snr2=sum(GSVS2[:5])
if msgcounter2==parsed_messages_list[x].msg_num:
                                            GSVS2.clear()
if antenna_works:
            printonLCD(snr2,snr1,lat1,lat_dir1,lat2,lat_dir2,lon1,lon_dir1,lon2,lon_dir2,lcd)
try:
                pi.bb_serial_read_close(RX)
                pi.stop()
                openned_antenna2=False
except KeyboardInterrupt:
                sys.exit()
except:
            pass
def printonLCD(snr2,snr1,lat1,lat_dir1,lat2,lat_dir2,lon1,lon_dir1,lon2,lon_dir2,lcd):
       if snr1>=snr2:
            lcd.setCursor(0,0)
            lcd.printout(lat1)
            lcd.printout(lat_dir1)
            lcd.setCursor(0,1)
            lcd.printout(lon1)
            lcd.printout(lon_dir1)
            lcd.setCursor(0,0)
       else:
            lcd.setCursor(0,0)
            lcd.printout(lat2)
            lcd.printout(lat_dir2)
            lcd.setCursor(0,1)
            lcd.printout(lon2)
            lcd.printout(lon_dir2)
            lcd.setCursor(0,0)
if __name__=="__main__":
    main()
