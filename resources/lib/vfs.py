import utils as utils
import xbmc
import xbmcvfs
import xbmcgui
import sys
from dropbox import client, rest, session

APP_KEY = 'f5wlmek6aoriqax'
APP_SECRET = 'b1461sje1kxgzet'

class Vfs:
    root_path = None

    def set_root(self,rootString):
        old_root = self.root_path
        self.root_path = rootString

        #fix slashes
        self.root_path = self.root_path.replace("\\","/")
        
        #check if trailing slash is included
        if(self.root_path[-1:] != "/"):
            self.root_path = self.root_path + "/"

        #return the old root
        return old_root
        
    def listdir(self,directory):
        return {}

    def mkdir(self,directory):
        return True

    def copy(self,source,dest):
        return True

    def rmdir(self,directory):
        return True

    def exists(self,aFile):
        return True
        
class XBMCFileSystem(Vfs):
    
    def listdir(self,directory):
        return xbmcvfs.listdir(directory)

    def mkdir(self,directory):
        return xbmcvfs.mkdir(directory)

    def copy(self,source,dest):
        return xbmcvfs.copy(source,dest)

    def rmdir(self,directory):
        return xbmcvfs.rmdir(directory,True)

    def exists(self,aFile):
        return xbmcvfs.exists(aFile)

class DropboxFileSystem(Vfs):
    client = None
    
    def __init__(self):
        user_token_key,user_token_secret = self.getToken()
        
        sess = session.DropboxSession(APP_KEY,APP_SECRET,"app_folder")

        if(user_token_key == '' and user_token_secret == ''):
            token = sess.obtain_request_token()
            url = sess.build_authorize_url(token)

            #print url in log
            utils.log("Authorize URL: " + url)
            xbmcgui.Dialog().ok(utils.getString(30010),"Check Log For Dropbox Authorize URL","Click OK When Authorized")  
            
            #if user authorized this will work
            user_token = sess.obtain_access_token(token)
            self.setToken(user_token.key,user_token.secret)
            
        else:
            sess.set_token(user_token_key,user_token_secret)
        
        self.client = client.DropboxClient(sess)
        utils.log(str(self.client.account_info()))

    def mkdir(self,directory):
        if(self.client != None):
            if(not self.exists(directory)):
                self.client.file_create_folder(directory)
            return True
        else:
            return False

    def exists(self,aFile):
        if(self.client != None):
            try:
                meta_data = self.client.metadata(aFile)
                #if we make it here the file does exist
                return True
            except:
                return False
        else:
            return False

    def copy(self,source,dest):
        if(self.client != None):
            f = open(source,'rb')
            response = self.client.put_file(dest,f,True)
            return True
        else:
            return False
            
    def setToken(self,key,secret):
        #write the token files
        token_file = open(xbmc.translatePath(utils.data_dir() + "tokens.txt"),'w')
        token_file.write("%s|%s" % (key,secret))
        token_file.close()

    def getToken(self):
        #get tokens, if they exist
        if(xbmcvfs.exists(xbmc.translatePath(utils.data_dir() + "tokens.txt"))):
            token_file = open(xbmc.translatePath(utils.data_dir() + "tokens.txt"))
            key,secret = token_file.read().split('|')
            token_file.close()

            return [key,secret]
        else:
            return ["",""]
            



            
