import os
import heapq
import pickle
import timeit
paddingCounter=0
reverseMapping={}
heap=[]
codes={}

#class for init node
class Node:
    def  __init__(this,char,freq):
       this.char=char
       this.freq=freq
       this.left=None
       this.right=None

    def __lt__(this, other):
        return this.freq < other.freq

    def __eq__(this, other):
        if(other == None):
            return False
        return this.freq==other.freq

#create dic contains frequency of each char
def frequencyDictionary(message):
        frequency={}
        for char in message:
            if not char in frequency:
                frequency[char]=0
            else:
                frequency[char]=frequency[char]+1
        if(len(frequency)==1):
            frequency['n']=0
        if(len(frequency)==0):
            print("Compressed")
            stop = timeit.default_timer()
            print('Time For Compress: ',stop-start)
            exit()
        return frequency

#make pariority queue and build heap
def buildHeap(frequency):
        for char in frequency:
            node=Node(char,frequency[char])
            heapq.heappush(heap,node)

#build huffman tree by extract minimum two nodes merge them and push back to heap
def extractMinimun():
        while(len(heap)>1):
            nodeA=heapq.heappop(heap)
            nodeB=heapq.heappop(heap)
            nodeC=Node(None,nodeA.freq+nodeB.freq)
            nodeC.left=nodeA
            nodeC.right=nodeB
            heapq.heappush(heap,nodeC)

#traverse through tree to get tuple contains code of each char
def treeTraverse(node,currentCode):
       if(node==None):
           return
       if(node.char!=None):
           codes[node.char]=currentCode
           reverseMapping[currentCode]=node.char
           return
       treeTraverse(node.left,currentCode+"0")
       treeTraverse(node.right,currentCode+"1")

#make code for char and save them
def makeCode():
        root=heapq.heappop(heap)
        currentCode=""
        treeTraverse(root,currentCode)

#make enconded message in form of binary using codes dictionary
def getEncoded(message):
        encodedMessage=""
        for char in message:
            encodedMessage=encodedMessage+codes[char]
        return encodedMessage

#return encoded message after adding padding and size of bytes message consume in decimal
def padEncoded(encodedMessage):
        padding=8-len(encodedMessage)%8
        for i in range(padding):
            global paddingCounter
            paddingCounter=paddingCounter+1
            encodedMessage=encodedMessage+"0"
        messageByteLength=len(encodedMessage)/8
        messageByteLength=int(messageByteLength)
        return encodedMessage,messageByteLength

#convert padencoded message in to byte array
def convertByte(padEncodedMessage):
         byteArray=bytearray()
         for i in range(0,len(padEncodedMessage),8):
             byteString=padEncodedMessage[i:i+8]
             byteArray.append(int(byteString,2))
         return byteArray

#return byteArray:size of bytes of  consume
#return byteArray2:len byteArray
def messageByteSize(message):
    byteArray=bytearray()
    byteArray2=bytearray()
    messageSizeBinary=bin(message)[2:].rjust(8,'0')
    padding=8-len(messageSizeBinary)%8
    for i in range(padding):
        messageSizeBinary="0"+messageSizeBinary

    for i in range(0,len(messageSizeBinary),8):
        byteString=messageSizeBinary[i:i+8]
        byteArray.append(int(byteString,2))

    byteArrayLen=bin(len(byteArray))[2:].rjust(8,'0')

    padding=8-len(byteArrayLen)%8
    if(padding!=8):
        for i in range(padding):
            byteArrayLen="0"+byteArrayLen

    for i in range(0,len(byteArrayLen),8):
        byteString=byteArrayLen[i:i+8]
        byteArray2.append(int(byteArrayLen,2))

    return byteArray,byteArray2

#return padding size in form of byteArray
def paddingSize(counter):

    byteArray=bytearray()
    paddingSize=bin(counter)[2:].rjust(8,'0')
    padding=8-len(paddingSize)%8
    for i in range(padding):
        paddingSize="0"+paddingSize
    byteArray.append(int(paddingSize,2))
    return byteArray


def compress(Cpath):
        #return tuple containg path and extention
        fileName,fileExtention=os.path.splitext(Cpath)
        outputPath=fileName+".bin"
        inputFile=open(Cpath,'r')
        outputFile=open(outputPath,'wb')
        message=inputFile.read().rstrip()
        frequency=frequencyDictionary(message)
        buildHeap(frequency)
        extractMinimun()
        makeCode()
        encodedMessage=getEncoded(message)
        padEncodedMessage,messageByteLength=padEncoded(encodedMessage)
        messageSize,byteSize=messageByteSize(messageByteLength)
        byteArray=convertByte(padEncodedMessage)
        outputFile.write(bytes(paddingSize(paddingCounter)))
        outputFile.write(bytes(byteSize))
        outputFile.write(bytes(messageSize))
        outputFile.write(bytes(byteArray))
        pickle.dump(reverseMapping,outputFile)
        inputFile.close()
        outputFile.close()
        print("File Compressed")
        print("Compression Rate = ",(os.path.getsize(outputPath)/os.path.getsize(Cpath))*100,"%")
        print ("{:<15} {:<15} {:<15} {:<15}".format("Char","Bytes","Code","NewCode"))
        for key,value in codes.items():
            print ("{:<15} {:<15} {:<15} {:<15}".format(key,ord(key),bin(ord(key))[2:],value))



def fileNumberAndSize(fileNumber,fileSize):
    byteFileNumber=bytearray()
    byteFileSize=bytearray()
    # messageSizeBinary=format(messageSize,'08b')

    fileNumberBinary=bin(fileNumber)[2:].rjust(8,'0')
    paddingFileNumber=8-len(fileNumberBinary)%8
    if(paddingFileNumber!=8):
        for i in range(paddingFileNumber):
            fileNumberBinary="0"+fileNumberBinary


    for i in range(0,len(fileNumberBinary),8):
       byteString=fileNumberBinary[i:i+8]
       byteFileNumber.append(int(byteString,2))


    for size in fileSize:
        fileSizeBinary=bin(size)[2:].rjust(8,'0')
        paddingFileSize=16-len(fileSizeBinary)%8
        for i in range(paddingFileSize):
            fileSizeBinary="0"+fileSizeBinary


        for i in range(0,len(fileSizeBinary),8):
            byteString=fileSizeBinary[i:i+8]
            byteFileSize.append(int(byteString,2))


    return byteFileNumber,byteFileSize



def compressFolder(Cpath,fileNumber,fileSize,message,fileNames,size):

        outputPath=Cpath+".bin"
        outputFile=open(outputPath,'wb')
        frequency=frequencyDictionary(message)
        buildHeap(frequency)
        extractMinimun()
        makeCode()
        encodedMessage=getEncoded(message)
        padEncodedMessage,messageByteLength=padEncoded(encodedMessage)
        messageSize,byteSize=messageByteSize(messageByteLength)
        byteArray=convertByte(padEncodedMessage)
        byteFileNumber,byteFileSize=fileNumberAndSize(fileNumber,fileSize)
        outputFile.write(bytes(paddingSize(paddingCounter)))
        outputFile.write(bytes(byteFileNumber))
        outputFile.write(bytes(byteFileSize))
        outputFile.write(bytes(byteSize))
        outputFile.write(bytes(messageSize))
        outputFile.write(bytes(byteArray))
        pickle.dump(reverseMapping,outputFile)
        print("Folder Compressed")
        outputFile.close()
        print("Compression Rate = ",(os.path.getsize(outputPath)/size)*100,"%")
        print ("{:<15} {:<15} {:<15} {:<15}".format("Char","Bytes","Code","NewCode"))
        for key,value in codes.items():
            print ("{:<15} {:<15} {:<15} {:<15}".format(key,ord(key),bin(ord(key))[2:],value))



#remove padding
def removePadEncoded(bitString,paddingSize):
        bitString=bitString[:-1*paddingSize]
        return bitString

#return decoded message
def getDecoded(encodedMessage,mapping):
        currentCode=""
        decodedMessage=""
        for bit in encodedMessage:
            currentCode=currentCode+bit
            if(currentCode in mapping):
                char=mapping[currentCode]
                decodedMessage=decodedMessage+char
                currentCode=""
        return decodedMessage

def decompress(Dpath):
        fileName,fileExtention=os.path.splitext(Dpath)
        outputPath=fileName+"Decompressed"+".txt"
        inputFile=open(Dpath,'rb')
        outputFile=open(outputPath,'w')
        bitString=""
        paddingSize=0
        messageSize=""
        byteMessageSize=0
        x=0
        flag=0
        flag2=0
        mapping=bytearray()
        byteString=inputFile.read(1)
        while(len(byteString)>0):

            flag=flag+1
            if(flag==1):
                #use ord to get unicode
                byteString=ord(byteString)
                #use bin to convert to binary and [2:] to remove 0b at first
                #rjust to get number in form of 8 bits
                bits=bin(byteString)[2:].rjust(8,'0')
                paddingSize=int(str(bits),2)

            elif(flag==2):
                byteString=ord(byteString)
                bits=bin(byteString)[2:].rjust(8,'0')
                byteMessageSize=int(str(bits),2)

            elif(flag>2 and byteMessageSize!=0):
                byteMessageSize=byteMessageSize-1
                byteString=ord(byteString)
                bits=bin(byteString)[2:].rjust(8,'0')
                messageSize=messageSize+bits
                x=int(str(messageSize),2)

            elif(byteMessageSize==0 and x!=0):
                byteString=ord(byteString)
                bits=bin(byteString)[2:].rjust(8,'0')
                flag2=flag2+1
                bitString=bitString+bits
                x=x-1

            else:
                mapping=mapping+byteString

            byteString=inputFile.read(1)

        if(len(mapping)==0):
            print("File Decompressed")
            stop = timeit.default_timer()
            print('Time For Decompress: ',stop-start)
            exit()

        mapping=pickle.loads(mapping)
        encodedMessage=removePadEncoded(bitString,paddingSize)
        decodedMessage=getDecoded(encodedMessage,mapping)
        outputFile.write(decodedMessage)
        print("File Decompressed")


def makeDecompressFolder(path,decodedMessage,fileNumber,Dpath,foldername,fileSize):
        fileNames=[]
        name=Dpath.split(".")
        name=name[0]
        flag=0
        counter=0
        fileNumberCounter=0
        check=os.path.exists(name)
        if(check==True):
                for file in os.listdir(name):
                    if file.endswith(".txt"):
                            file=file.split(".")
                            file=file[0]
                            fileNames.append(str(file))
                            flag=1
                            fileNumberCounter=fileNumberCounter+1

        os.mkdir(path+foldername)
        strings=[]
        i=0
        index=0
        for size in fileSize:
            string=decodedMessage[i:size+i]
            strings.append(string)
            i=i+size

        if(len(fileSize)==0):
            for number in range(0,fileNumberCounter):
                if(flag==1):
                    outputPath=path+foldername+"/"+fileNames[index]+".txt"
                if(flag==0):
                    counter=counter+1
                    outputPath=path+foldername+"/"+"Dcompressed"+str(counter)+".txt"
                index=index+1
                outputFile=open(outputPath,'w')



        for string in (strings):

             if(flag==1):
                 outputPath=path+foldername+"/"+fileNames[index]+".txt"
             if(flag==0):
                 counter=counter+1
                 outputPath=path+foldername+"/"+"Dcompressed"+str(counter)+".txt"
             index=index+1
             outputFile=open(outputPath,'w')
             outputFile.write(string)



def decompressFolder(Dpath,folderPath,foldername):
        fileName,fileExtention=os.path.splitext(Dpath)
        inputFile=open(Dpath,'rb')
        bitString=""
        paddingSize=0
        messageSize=""
        byteMessageSize=0
        fileNumber=0;
        fileSize=[]
        readingRate=0
        counter=0
        x=0
        flag=0
        flag2=0
        z=""
        mapping=bytearray()
        byteString=inputFile.read(1)

        while(len(byteString)>0):

            flag=flag+1
            if(flag==1):
                byteString=ord(byteString)
                bits=bin(byteString)[2:].rjust(8,'0')
                paddingSize=int(str(bits),2)

            elif(flag==2):
                byteString=ord(byteString)
                bits=bin(byteString)[2:].rjust(8,'0')
                fileNumber=int(str(bits),2)
                readingRate=3*fileNumber

            elif(readingRate!=0):

                counter=counter+1
                readingRate=readingRate-1
                byteString=ord(byteString)
                bits=bin(byteString)[2:].rjust(8,'0')
                z=z+bits

                if(counter==3):
                    counter=0
                    size=int(str(z),2)
                    z=""
                    fileSize.append(size)
                    fileNumber=fileNumber-1

            elif(fileNumber==0 and flag2==0):
                byteString=ord(byteString)
                bits=bin(byteString)[2:].rjust(8,'0')
                byteMessageSize=int(str(bits),2)
                flag2=1

            elif(flag2==1 and byteMessageSize!=0):
                byteMessageSize=byteMessageSize-1
                byteString=ord(byteString)
                bits=bin(byteString)[2:].rjust(8,'0')
                messageSize=messageSize+bits
                x=int(str(messageSize),2)

            elif(byteMessageSize==0 and x!=0):
                byteString=ord(byteString)
                bits=bin(byteString)[2:].rjust(8,'0')
                bitString=bitString+bits
                x=x-1

            else:
                mapping=mapping+byteString

            byteString=inputFile.read(1)


        if(len(mapping)==0):
            encodedMessage=removePadEncoded(bitString,paddingSize)
            decodedMessage=getDecoded(encodedMessage,mapping)
            makeDecompressFolder(folderPath,decodedMessage,fileNumber,Dpath,foldername,fileSize)
            print("Folder Decompressed")
            exit()

        mapping=pickle.loads(mapping)
        encodedMessage=removePadEncoded(bitString,paddingSize)
        decodedMessage=getDecoded(encodedMessage,mapping)
        makeDecompressFolder(folderPath,decodedMessage,fileNumber,Dpath,foldername,fileSize)
        print("Folder Decompressed")



path=os.getcwd()
print("1)Compress\n2)Decompress")
cflag=1
dflag=0
choise2=0
try:
    choise=input()
    choise=int(choise)
    if(choise==1):
        print("1)CompressFile\n2)CompressFolder")
        choise2=input()
        choise2=int(choise2)
        cflag=0


    if(choise==2):
        print("1)DecompressFile\n2)DecompressFolder")
        choise2=input()
        choise2=int(choise2)
        dflag=1

except ValueError:
    print("Please Choose 1 Or 2")
    exit()



if(choise2==1 and cflag==0):
    filename=input("Please Enter File Name To Compress (Without Extention) : ")
    path=path+"/"+filename+".txt"
    check=os.path.exists(path)
    if(check==True):
        start = timeit.default_timer()
        compress(path)
        stop = timeit.default_timer()
        print('Time For Compress: ',stop-start)
    else:
        print("File Not Exist")

elif(choise2==1 and dflag==1):
    filename=input("Please Enter File Name To Decompress (Without Extention)  : ")
    path=path+"/"+filename+".bin"
    check=os.path.exists(path)
    if(check==True):
        start = timeit.default_timer()
        decompress(path)
        stop = timeit.default_timer()
        print('Time For Decompress: ',stop-start)
    else:
        print("File Not Exist")

elif(choise2==2 and cflag==0):
    filename=input("Please Enter Folder Name To Compress : ")
    path=path+"/"+filename
    check=os.path.exists(path)
    if(check==True):
        fileNames=[]
        fileNamesBinary=[]
        eachMessage=""
        allMessage=""
        fileSize=[]
        flag=0
        size=0
        counter=0
        for file in os.listdir(path):
            if file.endswith(".txt"):
                    fileNames.append(str(file))
                    counter = counter+1
                    size=size+os.path.getsize(path+"/"+file)

        for file in fileNames:
            inputFile=open(path+"/"+file,'r')
            eachMessage=inputFile.read().rstrip()
            allMessage=allMessage+eachMessage
            fileSize.append(len(eachMessage))

        start = timeit.default_timer()
        compressFolder(path,counter,fileSize,allMessage,fileNames,size)
        stop = timeit.default_timer()
        print('Time For Compress Folder: ',stop-start)

    else:
        print("Folder Not Exist")

elif(choise2==2 and dflag==1):
    filename=input("Please Enter Folder Name To Decompress : ")
    folderPath=path+"/Decompressed"
    path=path+"/"+filename+".bin"
    check=os.path.exists(path)
    if(check==True):
        start = timeit.default_timer()
        decompressFolder(path,folderPath,filename)
        stop = timeit.default_timer()
        print('Time For Decompress: ',stop-start)
    else:
        print("Folder Not Exist")

else:
    print("Please Choose 1 Or 2")
