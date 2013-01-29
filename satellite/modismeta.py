"""
   class that reads the NASA hdfeos CoreMetadata.0 attribute
   and retrieves the orbitnumber, equator crossing time, 
   image lat/lon corners, etc.
"""

import types
import numpy as np
import pyhdf.SD


class metaParse:
    def __init__(self,metaDat=None,altrDat=None,filename=None):
        import re
        if (metaDat is not None) and (altrDat is not None):
            self.metaDat=metaDat
            self.altrDat=altrDat
        else:
            infile = pyhdf.SD.SD(filename)
            test=infile.attributes().keys()
            self.metaDat=infile.__getattr__('CoreMetadata.0')
            self.altrDat=infile.__getattr__('ArchiveMetadata.0')
            #infile.end()
                        
        #search for the string following the words "VALUE= "
        self.stringObject=\
             re.compile('.*VALUE\s+=\s"(?P<value>.*)"',re.DOTALL)
        #search for a string that looks like 11:22:33
        self.timeObject=\
             re.compile('.*(?P<time>\d{2}\:\d{2}\:\d{2}).*',re.DOTALL)
        #search for a string that looks like 2006-10-02
        self.dateObject=\
             re.compile('.*(?P<date>\d{4}-\d{2}-\d{2}).*',\
                        re.DOTALL)
        #search for a string that looks like "(anything between parens)"
        self.coordObject=re.compile('.*\((?P<coord>.*)\)',re.DOTALL)
        #search for a string that looks like "1234"
        self.orbitObject=\
             re.compile('.*VALUE\s+=\s(?P<orbit>\d+)\n',re.DOTALL)
        #search for a string that looks like = -9.33512459024296
        self.boxObject=re.compile('.*?=\s+([-]*\d*\.\d+).*',re.DOTALL)

    def getstring(self,theName):
        theString=self.metaDat.split(theName)
        #should break into three pieces, we want middle
        if len(theString) ==3:
            theString=theString[1]
        else:
            
            altString=self.altrDat.split(theName)
            if len(altString) == 3:
                theString=altString[1]
            else:
                raise Exception("couldn't parse %s" % (theName,))
        return theString
        
    def getbox(self):
        if self.altrDat.find('NORTHBOUNDINGCOORDINATE') > 0:
            coord_string=self.altrDat
        elif self.metaDat.find('NORTHBOUNDINGCOORDINATE') > 0:
            coord_string=self.metaDat
        else:
            raise Exception("couldn't find NORTHBOUNDINGCOORDINATE")
        out=coord_string.split('NORTHBOUNDINGCOORDINATE')
        north=self.boxObject.match(out[1]).group(1)
        NSEW=[north]
        out=coord_string.split('SOUTHBOUNDINGCOORDINATE')
        south=self.boxObject.match(out[1]).group(1)
        NSEW.append(south)
        out=coord_string.split('EASTBOUNDINGCOORDINATE')
        east=self.boxObject.match(out[1]).group(1)
        NSEW.append(east)
        out=coord_string.split('WESTBOUNDINGCOORDINATE')
        west=self.boxObject.match(out[1]).group(1)
        NSEW.append(west)
        NSEW=tuple([float(item) for item in NSEW])
        return NSEW
    
    def __call__(self,theName):
        if theName=='CORNERS':
            import string
            #look for the corner coordinates by searching for
            #the GRINGPOINTLATITUDE and GRINGPOINTLONGITUDE keywords
            #and then matching the values inside two round parenthesis
            #using the coord regular expression
            theString= self.getstring('GRINGPOINTLATITUDE')
            theMatch=self.coordObject.match(theString)
            thelats=theMatch.group('coord').split(',')
            thelats=map(string.atof,thelats)
            theString= self.getstring('GRINGPOINTLONGITUDE')
            theMatch=self.coordObject.match(theString)
            thelongs=theMatch.group('coord').split(',')
            thelongs=map(string.atof,thelongs)
            coordlist=[]
            for i in range(len(thelongs)):
                coordlist.append((thelongs[i],thelats[i]))
            value=coordlist
        #regular value
        else:
            theString= self.getstring(theName)
            #orbitnumber doesn't have quotes
            if theName=='ORBITNUMBER':
                theMatch=self.orbitObject.match(theString)
                if theMatch:
                    value=theMatch.group('orbit')
                else:
                    raise Exception("couldn't fine ORBITNUMBER")
            #expect quotes around anything else:
            else:
                theMatch=self.stringObject.match(theString)
                if theMatch:
                    value=theMatch.group('value')
                    theDate=self.dateObject.match(value)
                    if theDate:
                        value=theDate.group('date') + " UCT"
                    else:
                        theTime=self.timeObject.match(value)
                        if theTime:
                            value=theTime.group('time') + " UCT"
                else:
                    raise Exception("couldn't parse %s" % (theName,))
        return value

    def get_info(self):
        outDict={}
        outDict['nsew']=self.getbox()
        outDict['orbit']=self('ORBITNUMBER')
        outDict['filename']=self('LOCALGRANULEID')
        outDict['stopdate']=self('RANGEENDINGDATE')
        outDict['startdate']=self('RANGEBEGINNINGDATE')
        outDict['starttime']=self('RANGEBEGINNINGTIME')
        outDict['stoptime']=self('RANGEENDINGTIME')
        outDict['equatortime']=self('EQUATORCROSSINGTIME')
        outDict['equatordate']=self('EQUATORCROSSINGDATE')
        outDict['nasaProductionDate']=self('PRODUCTIONDATETIME')
        outDict['daynight']=self('DAYNIGHTFLAG')
        corners=self('CORNERS')
        cornerlats=[]
        cornerlons=[]
        for (lon,lat) in corners:
            cornerlats.append(lat)
            cornerlons.append(lon)
        outDict['cornerlats']=np.array(cornerlats)
        outDict['cornerlons']=np.array(cornerlons)
        return outDict


if __name__=='__main__':
    import sys
    filename=\
         'MYD021KM.A2010215.2145.005.2010216173817.hdf'
         #'MYD35_L2.A2010215.2145.005.2010216174714.hdf'
         #'MOD021KM.A2006275.0440.005.2008107091833.hdf'
    my_parser=metaParse(filename=filename)
    print my_parser.get_info()
