__author__ = "Hui Lian"
__doc__ = '''
This file compliments with generateReportFolder.sh (on Rpi).
This file will convert the files inside a folder to a timingReport excel file.
To use:

Double click this file.
Select the folder generated from generateReportFolder.sh
If all succeed, a timingReportXX.xlsx should appear in current directory
'''

try:
    import xlsxwriter                                   # if not found, auto install
except ImportError:
    import pip
    pip.main(["install", "xlsxwriter"])
    print "Please restart the script again."
    exit(0)
import re
import os
import sys
import Tkinter
import tkFileDialog

def removeChars(s):
    s=s.replace("\r\n", "")
    s=s.replace("[","")
    s=s.replace("]","")
    s=s.replace("\t", "")
    return s

def extractData(s):
    data = []
    regex=re.compile("(\d+\.\d+) +(.+)")
    s = removeChars(s)
    lines = s.split("\n")
    lines.remove("")
    count = 0
    for line in lines:
        remove = line.strip()
        matches = regex.findall(remove)
        if matches:
            #print matches
            data.extend(matches)
            count += 1
            
    print "="*5
    print "number of lines", len(lines)
    print "count: ", count
    print "="*5
    
    if len(lines) != count:
        print "[!!!] data lost"
        return None
    
    return data
    

def getFilename(prefix):
    counter = 1
    filename = "%s%02d.xlsx" % (prefix, counter)
    while os.path.exists(filename):
        counter += 1
        filename = "%s%02d.xlsx" % (prefix, counter)
    return filename

def createWorksheet(workbook, sheetname, data):
    worksheet = workbook.add_worksheet(sheetname)
    # add the data
    row, col = 0, 0
    for timestamp, activity in data:
        worksheet.write(row, col, timestamp)
        worksheet.write(row, col+1, activity)
        row += 1
    # add the analysis
    # calculate differences
    col = 2
    worksheet.write(0, col, "difference")
    for r in range(1,len(data)):
        worksheet.write(r, col, "=A%d-A%d" % (r+1, r))

    # add threshold
    row, col = 0, 5
    worksheet.write(row, col, "threshold")
    worksheet.write(row+1, col, 2)

    # check if slow
    col = 3
    for r in range(1,len(data)):
        worksheet.write(r, col, '=IF(C%d > $F$2, "slow!", "")' % (r+1))

if __name__ == "__main__":

    root = Tkinter.Tk()
    root.withdraw()
    path = tkFileDialog.askdirectory()
    root.destroy()

    name = getFilename("timingReport")
    print "generating excel sheet: %s" % name
    workbook = xlsxwriter.Workbook(name)

    FILES = ["fromAll.txt","toAll.txt",\
             "fromAndroid.txt","toAndroid.txt",\
             "fromArduino.txt","toArduino.txt",\
             "fromPc.txt","toPc.txt",\
             "fromPcToArduino.txt","fromArduinoToPc.txt"]

    for f in FILES:
        fobj = open("%s/%s" % (str(path),f) , "r")
        info = fobj.read()
        fobj.close()
        data = extractData(info)
        if data:
            createWorksheet(workbook, f, data)
            print "created Worksheet for %s" % f
        else:
            print "no data for %s" % f
        
    workbook.close()
    print "excel sheet %s generated." % name
    
    


    

