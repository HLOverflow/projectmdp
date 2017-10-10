import time
from color import *

def printWithTime(s):
	print "[%s]\t %s" % (colorString(str(time.time()),YELLOW), s)