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
import string
import time

class TimedActions:
   def __init__(self,interval):
        self.iv=interval;
        self.last_time=time.time()  # seconds since epoch
        self.did_run=False
   def set_interval(self,interval):
        self.iv=interval;
   def enough_time_passed(self):
        if not self.did_run:
           self.did_run=True
           self.last_time=time.time()
           return True
        else:
           if (time.time()-self.last_time)>self.iv:
              self.last_time=time.time()
              return True
           else:
              return False


