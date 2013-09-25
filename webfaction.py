import xmlrpclib
from passwords import wf_login, wf_password

def createEMail(project):
    try:
        server = xmlrpclib.ServerProxy('https://api.webfaction.com/') 
        session_id, account = server.login(wf_login, wf_password) 
        data = server.create_email(session_id, 
                            '%s@projects.naphtaline.net' % project,
                            # targets
                            '/home/'+wf_login+'/bin/processIncomingMail.py')
        print data
    except Exception, e:
        print e
