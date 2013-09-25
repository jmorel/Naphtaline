import cherrypy
from various import *

def isProjectValid(con, webName):
    """ Check that the project is an existing one.
    """
    cursor = con.cursor()
    res = False
    if webName is not None :
        query = """
        SELECT id, name
        FROM Project
        WHERE webname = %s"""
        cursor.execute(query, (webName, ))
        rows = cursor.fetchall()
        for row in rows :
            if row[0] > 0 :
                cherrypy.session[str(webName)+'_projectCode'] = row[0]
                cherrypy.session[str(webName)+'_projectName'] = row[1]
                res = True
    return res

def isCategoryValid(category):
    """ Category can only be 'bug' or 'feature'.
    """
    res = False
    if category == 'bug' or category == 'feature' :
        res = True
    return res

def isLoginValid(con, project):
    """ Check that the user is logged for this project.
    Users can be logged on various projects simultaneously
    """
    res = False
    level = cherrypy.session.get(str(project)+'_loginLevel', 0)
    res = (level > 0)
    if res :
        cursor = con.cursor()
        query = """
        SELECT project
        FROM Client
        WHERE id = %s"""
        cursor.execute(query, (cherrypy.session.get(str(project)+'_idUser', -1), ) )
        rows = cursor.fetchall()
        projectID = -2
        for row in rows :
            projectID = row[0]
        if int(projectID) != int(cherrypy.session.get(str(project)+'_projectCode', -1)) :
            res = False
    return res

def isSuperuser(project) :
    """ Check whether the user is superuser (level == 2) or not
    """
    return cherrypy.session.get(str(project)+'_loginLevel', 1) == 2

def isCreator(con, project, category, relativeID, userID):
    """Check whether the is the entry's creator or not"""
    categoryCode = {'bug' : 1, 'feature' : 2}
    cursor = con.cursor()
    query="""SELECT creator FROM Ticket WHERE category=%s AND relativeID=%s"""
    cursor.execute(query, (categoryCode[category], relativeID))
    res = False
    for row in cursor.fetchall():
        if int(row[0]) == int(userID):
            res = True
    return res
    
def isTicketIDValid(con, project, category, ticketID):
    """Check whether ticketID refers to an actuel ticket"""
    categoryCode = {'bug': 1, 'feature': 2}
    cursor = con.cursor()
    query = """
    SELECT count(*) FROM Ticket
    INNER JOIN Project
    ON Project.id = Ticket.project
    WHERE 
        Project.webname = %s
        AND Ticket.category = %s
        AND Ticket.relativeID = %s"""
    cursor.execute(query, (project, categoryCode[category], ticketID))
    res = (int(cursor.fetchone()[0]) == 1)
    return res

def checkProject(con, project) :
    if not isProjectValid(con, project) :
        con.close()
        raise cherrypy.HTTPRedirect( url('new') )

def checkCategory(con, project, category) :
    if not isCategoryValid(category) :
        con.close()
        raise cherrypy.HTTPRedirect( url(project) )

def checkLogin(con, project) :
    if not isLoginValid(con, project) :
        cherrypy.session[str(project)+'_previousPage'] = cherrypy.url()
        con.close()
        raise cherrypy.HTTPRedirect( url(project, 'login') )

def checkSuperUser(con, project) :
    if not isSuperuser(project):
        con.close()
        raise cherrypy.HTTPRedirect( url(project) )


def checkSuperUserOrCreator(con, project, category, ticketID) :
    userID = cherrypy.session.get(str(project)+'_idUser', 0)
    if not isSuperuser(project) and not isCreator(con, project, category, ticketID, userID):
        con.close()
        raise cherrypy.HTTPRedirect( url(project, category, ticketID) )
    
def checkProjectCategoryLogin(con, project, category) :
    """ This is the "normal" checking procedure
    Check that the project is valid, that we are requesting a valid category and that the user is logged in.
    """
    # is the project an existing one ?
    checkProject(con, project)
    # is the category an existing one ?
    checkCategory(con, project, category)
    # is the user logged in ?
    checkLogin(con, project)
    
#def checkProjectCategoryLoginLevel(con, project, category, ticketID) :
#    """ Checks that the user is a superuser in top of the normal procedure
#    """
#    # normal procedure
#    checkProjectCategoryLogin(con, project, category)
#    # is the user a super user or the creator ?
#    checkSuperUserOrCreator(con, project, category, ticketID)

def checkProjectLoginLevel(con, project) :
    # is the project an existing one ?
    checkProject(con, project)
    # is the user logged in ?
    checkLogin(con, project)
    # is the user a super user ?
    checkSuperUser(con, project)
    
def checkProjectLogin(con, project) :
    # is the project an existing one ?
    checkProject(con, project)
    # is the user logged in ?
    checkLogin(con, project)
    
