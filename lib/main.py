from ScanningClass import ScanningClass
import optparse
import sys
from api import BingSearch

def main():
    parser = optparse.OptionParser('usage:%prog [options] domain.com',version="%prog 1.0")
    parser.add_option("-u",dest='URL',type='string',help='Want to Scan the URL')
    parser.add_option("-f","--dic",dest='DicFile',type='string',help='Dictionary file (add multiple "," split)')
    parser.add_option("-o","--output",dest='OutputFile',type='string',help='OutPut to file')
    parser.add_option("--nextstation",dest='NextStation',type='string',help='Check next station')
    parser.add_option("-t",'--thread',dest='ThreadNum',type='int',default=30,help='Number of threads')
    (options,args)=parser.parse_args()
    if options.URL != None and options.DicFile !=None :
        s = ScanningClass(options=options)
        s.run()
        s.write()
        sys.exit(0)
    if options.NextStation != None:
        data = BingSearch(options.NextStation)
        for each in data['d']['results']:
            print each['Title'], each['Url']
    else:
        parser.print_help()
        sys.exit(0)