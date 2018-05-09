import numpy as np

class KalypsoADCData:
    def __init__(self,filename):
        self.filename       = filename

    NUMBER_PIXELS  = 256
    DDR_FILLING    = [0xba98,0xfedc]
    HEADER_0       = 0xABBA
    short_pattern  = [0,1,2,3,3,2,1,0]
    long_pattern   = np.repeat(short_pattern, 32)


    ############################################################################
    ## getData (shots[opt.],offset[opt.])
    ## return: data_array_stripped, shots
    ############################################################################
    def getData(self, shots = None , offset = None):

        np.set_printoptions(threshold='nan')
        if 	offset is None:
            data = np.memmap( self.filename, dtype=np.dtype('<u2'), mode='r')
        else:
            data = np.memmap( self.filename, dtype=np.dtype('<u2'), offset = (2*self.NUMBER_PIXELS*offset),mode='r')
	

        if ( shots ):
            data = data[0:shots*self.NUMBER_PIXELS]

        # Remove Header
        if (data[0] == self.HEADER_0):
            data = data[16:]
            data = np.append(data, [self.DDR_FILLING,self.DDR_FILLING,self.DDR_FILLING,self.DDR_FILLING,self.DDR_FILLING,self.DDR_FILLING,self.DDR_FILLING,self.DDR_FILLING])

        # Reshape list as an 256*whatever array
        data = np.reshape(data, (-1,self.NUMBER_PIXELS))

        ########################################################################
        ### Remove Filling at the end
        ########################################################################
    
        lines_with_filling = 0

        while (np.all(data[-1:]==self.DDR_FILLING) or np.all(data[-1:]==0x00000000)):
            data = data[0:-1,:]
            lines_with_filling += 1

        ########################################################################
        ### Data consistency check
        ########################################################################       
        shots, pixels = np.shape(data)

        high = (data & 0xC000) >> 14
        data = (data & 0x3fff)

        #if (np.any(high - self.long_pattern)):
        #    raise IOError("'"+self.filename+"': Data consistency check failed.")
            
        return data
    
class SCImage:
    def __init__(self,filename):
        self.filename = filename
        with open(filename, "rb") as f:
            binHeader = f.read(64)
            
            assert(binHeader[0] == 73 and binHeader[1] == 77)
            comntLen = binHeader[2] + 0x100 * binHeader[3]
            nPixelsX = binHeader[4] + 0x100 * binHeader[5]
            nPixelsY = binHeader[6] + 0x100 * binHeader[7]
            clrDepth = binHeader[12]+ 0x100 * binHeader[13]
            
            comment = f.read(comntLen)
            
            data = f.read(nPixelsX*nPixelsY*clrDepth)
            data = np.fromstring(data,dtype = '<u2')
            self.data = data.reshape(nPixelsY,nPixelsX)
            
    def getData(self):
        return self.data

