#!/usr/bin/python

# Copyright 2014 Nico Lugil <nico at lugil dot be>
#
# This file is part of wifiMonitor
#
# wifiMonitor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wifiMonitor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with wifiMonitor. If not, see <http://www.gnu.org/licenses/>.

import sys    
import time
import string
import datetime
import subprocess 
import StringIO
import logging
import logging.handlers
from shutil import copyfile
import glob,os 
import re

from TimedActions import TimedActions
import lib.pythonping

LOGFILE="/tmp/wifiMonitor"
LOGFILESD="/mnt/sda1/arduino/wifiMonitor_"
RESTART_WIFI_WHEN_LOST = True
TO_PING = "192.168.1.1"
KEEP_ONLY_LAST_BACKUP = True   # if false --> will grow forever, could run out of 'disk' space
CHECK_WIFI_INTERVAL = 16  # seconds
BACKUP_INTERVAL = 3600 # seconds

def now():
      now_t=datetime.datetime.now()
      now_str=now_t.strftime("%Y-%m-%d %H:%M")
      return now_str

def copylog(single):
      # only copy last part
      if single:
         copyfile(LOGFILE+".log",LOGFILESD+"last.log")
      else:
         copyfile(LOGFILE+".log",LOGFILESD+now()+".log")

def wifi_down_up():
      subprocess.call(["wifi","down"], stdout=open(os.devnull, 'wb'))
      time.sleep(5)
      subprocess.call("wifi", stdout=open(os.devnull, 'wb'))
      time.sleep(5)

def get_wifi_info():
      p = subprocess.Popen(["iwconfig","wlan0"], stdout=subprocess.PIPE)
      out, err = p.communicate()
      m=re.search(r"Link.*dBm",out)
      if m is None:
          print "No Match found"
          return "no-info"
      else:
          return m.group(0)

def runit():

  print "log will be written to" + LOGFILE + ".log and backed up at " + LOGFILESD + "..."
     
  filelist=glob.glob(LOGFILE+"*") 
  for f in filelist: 
     #print "removing " + str(f)
     os.remove(f) 
  time.sleep(5)

  my_logger = logging.getLogger('MyLogger')
  my_logger.setLevel(logging.DEBUG)
  handler = logging.handlers.RotatingFileHandler(LOGFILE+".log", maxBytes=16384, backupCount=2)
  my_logger.addHandler(handler)

  timer_checkwifi = TimedActions(CHECK_WIFI_INTERVAL)  
  timer_cp2SD = TimedActions(BACKUP_INTERVAL) 

  n_ok=0
  n_err=0

  while True:
    try:

      wifi_down_up()
      time.sleep(15)  # give it some more time to establish connection 
      my_logger.debug("{0} : wifiMonitor (re)started with RESTART_WIFI_WHEN_LOST={1}".format(now(),RESTART_WIFI_WHEN_LOST))
      starttime=datetime.datetime.now()

      while True:
         time.sleep(5)
         if timer_checkwifi.enough_time_passed():
             link_q = get_wifi_info()
             ping_delay = lib.pythonping.do_one(TO_PING,5)  
             if ping_delay is None:
                  n_err=n_err+1
                  my_logger.debug("{0} : wifi lost".format(now()))
                  if RESTART_WIFI_WHEN_LOST:
                      wifi_down_up()
                      my_logger.debug("{0} :    restarted wifi".format(now()))
                  time.sleep(15)  # give it some more time to establish connection 
                  starttime=datetime.datetime.now()
             else:
                  n_ok=n_ok+1
                  uptime = datetime.datetime.now()-starttime
                  my_logger.debug("{0} : wifi OK, uptime={1}, ok/nok: {2}/{3} - {4}".format(now(),uptime,n_ok,n_err,link_q))
         if timer_cp2SD.enough_time_passed():
             copylog(KEEP_ONLY_LAST_BACKUP)                     
    except Exception as e:
      my_logger.debug("--- Exception caught ---")
      template = "{2} : An exception of type {0} occured. Arguments:\n{1!r}"
      message = template.format(type(e).__name__, e.args, now())
      my_logger.debug(str(message))
      my_logger.debug("----")
      copylog(KEEP_ONLY_LAST_BACKUP)                     
      time.sleep(3)
      #break

if __name__ == '__main__':
      runit()

