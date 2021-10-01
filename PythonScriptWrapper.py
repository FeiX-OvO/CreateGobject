import sys
import io
from lxml import etree
import optparse
import logging
import os
# It is importing from source

logging.basicConfig(filename='PythonScript.log', filemode='a', level=logging.DEBUG) 
log = logging.getLogger('bq.modules')

from bqapi.comm import BQCommError
from bqapi.comm import BQSession
from bqapi.util import fetch_blob

# ROOT_DIR = './'
# sys.path.append(os.path.join(ROOT_DIR, "source/"))
from GobjectAdd import gobject_core


class ScriptError(Exception):
    def __init__(self, message):
        self.message = "Script error: %s" % message
    def __str__(self):
        return self.message

class PythonScriptWrapper(object):
    
    def preprocess(self, bq):

        log.info('Options: %s' % (self.options))
        """
        1. Get the resource image
        """
        self.seg = bq.load(self.options.annotationURL)
        self.seg_name=self.seg.__dict__['name']
        log.info("process image as %s" % (self.seg_name))
        log.info("image meta: %s" % (self.seg))
        cwd= os.getcwd()

        result = fetch_blob(bq, self.options.annotationURL, dest=os.path.join(cwd,self.seg_name))
        
        if '.gz' in self.seg_name:
            os.rename(self.seg_name,self.seg_name.replace('.gz',''))
            self.seg_name=self.seg_name.replace('.gz','')

    
    def run(self):
        """
        Run Python script

        """
        bq = self.bqSession
        try:
##            bq.update_mex('Pre-process the images')
            self.preprocess(bq)
        except (Exception, ScriptError) as e:
            log.exception("Exception during preprocess")
            bq.fail_mex(msg = "Exception during pre-process: %s" % str(e))
            print('fail to preprocess')
            return
        #call script
        
        meta = bq.fetchxml('%s?meta'%self.options.imageURL)

        xml_new=gobject_core(self.seg_name, meta)

        bq.postxml(self.options.imageURL, xml_new, method='POST')
##        print('posted')

        bq.update_mex( 'Returning results')

                

    def setup(self):
        """
        Pre-run initialization

        """

        self.bqSession.update_mex('Initializing...')
        self.mex_parameter_parser(self.bqSession.mex.xmltree)
        self.output_string = "added"


    def teardown(self):
##        """
##        Post the results to the mex xml
##        """
        self.bqSession.update_mex('Returning results')
        
        outputTag = etree.Element('tag', name ='outputs')
        
        outputTag.append(etree.fromstring('<root>'+ self.output_string))
      
    def mex_parameter_parser(self, mex_xml):
        """
            Parses input of the xml and add it to options attribute (unless already set)

            @param: mex_xml
        """
        
        mex_inputs = mex_xml.xpath('tag[@name="inputs"]/tag[@name!="script_params"] | tag[@name="inputs"]/tag[@name="script_params"]/tag')
        if mex_inputs:
            for tag in mex_inputs:
                if tag.tag == 'tag' and tag.get('type', '') != 'system-input': #skip system input values
                    if not getattr(self.options,tag.get('name', ''), None):
                        log.debug('Set options with %s as %s'%(tag.get('name',''),tag.get('value','')))
                        setattr(self.options,tag.get('name',''),tag.get('value',''))
        else:
            log.debug('No Inputs Found on MEX!')

    def validate_input(self):
        """
            Check to see if a mex with token or user with password was provided.

            @return True is returned if validation credention was provided else
            False is returned
        """
        if (self.options.mexURL and self.options.token): #run module through engine service
            return True
        if (self.options.user and self.options.pwd and self.options.root): #run module locally (note: to test module)
            return True
        log.debug('Insufficient options or arguments to start this module')
        return False



    def main(self):
        parser = optparse.OptionParser()
        parser.add_option('--mex_url'          , dest="mexURL")
        parser.add_option('--module_dir'       , dest="modulePath")
        parser.add_option('--staging_path'     , dest="stagingPath")
        parser.add_option('--bisque_token'     , dest="token")
        parser.add_option('--user'             , dest="user")
        parser.add_option('--pwd'              , dest="pwd")
        parser.add_option('--root'             , dest="root")
        parser.add_option('--image_volume'     , dest="imageURL")
        parser.add_option('--annotation_volume', dest="annotationURL")
        
            
        (options, args) = parser.parse_args()

        
        fh = logging.FileHandler('scriptrun.log', mode='a')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)8s --- %(message)s ' +
                                  '(%(filename)s:%(lineno)s)',datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        log.addHandler(fh)
        

        try: #pull out the mex

            if not options.mexURL:
                options.mexURL = sys.argv[-2]
            if not options.token:
                options.token = sys.argv[-1]

        except IndexError: #no argv were set
            pass

        if not options.stagingPath:
            options.stagingPath = ''

        log.debug('\n\nPARAMS : %s \n\n Options: %s' % (args, options))
        self.options = options

        if self.validate_input():

             #initalizes if user and password are provided
            if (self.options.user and self.options.pwd and self.options.root):

                try:
                    self.bqSession = BQSession().init_local( self.options.user, self.options.pwd, bisque_root=self.options.root)
                    self.options.mexURL = self.bqSession.mex.uri

                except:
##                    print('fail to initialize mex')
                    return

             #initalizes if mex and mex token is provided
            elif (self.options.mexURL and self.options.token):

                try:
##                    print('get session')
                    self.bqSession = BQSession().init_mex(self.options.mexURL, self.options.token)
                except:
                    return



            else:
                raise ScriptError('Insufficient options or arguments to start this module')

            try:
##                print('set up')
                self.setup()
            except Exception as e:
                log.exception("Exception during setup")
##                self.bqSession.fail_mex(msg = "Exception during setup: %s" %  str(e))
                return
####
            try:
##                print('run')
                self.run()
            except (Exception, ScriptError) as e:
                log.exception("Exception during run")
##                self.bqSession.fail_mex(msg = "Exception during run: %s" % str(e))
                return
##
            try:
##                print('teardown')
                self.teardown()
            except (Exception, ScriptError) as e:
                log.exception("Exception during teardown")
                self.bqSession.fail_mex(msg = "Exception during teardown: %s" %  str(e))
                return
        
            self.bqSession.close()
        log.debug('Session Close')
        
if __name__=="__main__":
    PythonScriptWrapper().main()
