import os
import requests
import threading
import urllib.request, urllib.error, urllib.parse
import time

"""File berbentuk URL yang akan di download oleh sistem"""
url = "https://apod.nasa.gov/apod/image/1901/LOmbradellaTerraFinazzi.jpg"

""" Melakukan split untuk data(bytes) yang akan didownload """
def buildRange(value, numsplits):
    
    lst = []
    for i in range(numsplits):
        if i == 0:
            lst.append('%s-%s' % (i, int(round(1 + i * value/(numsplits*1.0) + value/(numsplits*1.0)-1, 0))))
        else:
            lst.append('%s-%s' % (int(round(1 + i * value/(numsplits*1.0),0)), int(round(1 + i * value/(numsplits*1.0) + value/(numsplits*1.0)-1, 0))))
    return lst

""" Melakukan split kepada buffer dan thread pada saat proses download berlangsung """
class SplitBufferThreads(threading.Thread):
    """ Splits the buffer to ny number of threads
        thereby, concurrently downloading through
        ny number of threads.
    """
    def __init__(self, url, byteRange):
        super(SplitBufferThreads, self).__init__()
        self.__url = url
        self.__byteRange = byteRange
        self.req = None

    def run(self):
        self.req = urllib.request.Request(self.__url,  headers={'Range': 'bytes=%s' % self.__byteRange})

    def getFileData(self):
        return urllib.request.urlopen(self.req).read()


def main(url=None, splitBy=3):
    start_time = time.time()
    """ mengecek apakah yang diinputkan url atau bukan"""
    if not url:
        print("Please Enter some url to begin download.")
        return

    """ Mengisi variabel filename dengan nama url yang di split. Filename ini nantinya akan menjadi nama file """
    fileName = url.split('/')[-1]

    """ Mengecek besar dari file yang akan didownload dalam bytes. Ketika tidak ada, maka print size tidak terdefinisi """
    sizeInBytes = requests.head(url, headers={'Accept-Encoding': 'identity'}).headers.get('content-length', None)
    print("%s bytes to download." % sizeInBytes)
    if not sizeInBytes:
        print("Size cannot be determined.")
        return
    
    """ Proses pembagian thread """
    dataLst = []
    for idx in range(splitBy):
        """ mendapatkan range dari total bytes """
        byteRange = buildRange(int(sizeInBytes), splitBy)[idx]
        """ melakukan split terhadap buffer sesuai dengan rangenya """
        bufTh = SplitBufferThreads(url, byteRange)
        bufTh.start()
        bufTh.join()
        dataLst.append(bufTh.getFileData())

    content = b''.join(dataLst)
    
    """ save data tersebut ke directory dan mengecek apakah sudah terdownload, dengan nama yang sudah terdefinisi pada filename """
    if dataLst:
        if os.path.exists(fileName):
            os.remove(fileName)
        print("--- %s seconds ---" % str(time.time() - start_time))
        with open(fileName, 'wb') as fh:
            fh.write(content)
        print("Finished Writing file %s" % fileName)

if __name__ == '__main__':
    main(url)
