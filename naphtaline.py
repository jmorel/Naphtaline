import cherrypy
import demjson

from tickets import *
from mailing import sendMail#, sendNewTicketNotifications, sendEditTicketNotifications, sendNewCommentNotifications, sendDeleteNotifications
from postgres import getConnection
from security import *
from urls import setRoutes
from various import *
from webfaction import createEMail

from mako.template import Template
import md5
import re


from cherrypy.lib.static import serve_file
import mimetypes

import os.path
_curdir = os.path.join(os.getcwd(), os.path.dirname(__file__))

class Naphtaline :
    """ The one and only class of the Naphtaline projects.
    """
    
    #_cp_config = { 'tools.sessions.on': True }
    
    def __init__(self) :
        # parameters of the application
        #self.enableManagementByMail = False
        pass
    
    
    def projects(self, project, category, ticketID=None):
        """ Main method of the Class.
        projects will display the ticket of relative id (ie this is not the real
        id of the ticket, but the one that will be displayed, in order to get 
        consistency through notations) 'idTicket' 
        """
        
        # creating connection
        con = getConnection()
        
        # getting project lang (used to select templates afterwars)
        lang = projectLang(con, project)
        
        # verifications to ensure that the page can be displayed
        # this is necessary since values checked here are passed as GET 
        # and thus easily changed by "curious" users
        checkProjectCategoryLogin(con, project, category)
        
        # check that ticketID is a valid ID
        if not isTicketIDValid(con, project, category, ticketID):
            # go to "new ticket page"
            raise cherrypy.HTTPRedirect(url(project, category, 'new'))
            
        
        # loading details about the selected ticket
        # if the idTicket is not OK, then the selectedTicket hash will be empty
        selectedTicket = loadSelectedTicket(con, project, category, ticketID)
        selectedTicketHTML = self.getTicketHTML(project, lang, category, selectedTicket)
        
        # loading ticket's comments
        comments = loadComments(con, project, category, selectedTicket['id'])
        commentsHTML = self.getCommentsHTML(project, lang, comments)
        # loading all tickets from the selected project in the selected category
        # tickets are divided in two lists which are displayed separatly on 
        # the page
        # note that tickets are already sorted
        solved = ((selectedTicket['status'] == 1) or (selectedTicket['status'] == 4))
        #tickets = loadTickets(con, project, category, solved)
        #ticketsList = self.getTicketsListHTML(project, category, solved, lang, tickets, selectedTicket['id'])
        ticketsList = self.getTicketsList(project, category, solved, ticketID)
        
        # list of tickets containing modification since last visit
        #unread = updatedTickets(con, project, category, idTicket)
        
        # closing connection
        con.close()
        
        # generating page through template
        mytemplate = Template(filename='templates/'+lang+'/bugs.html', 
                              output_encoding='utf-8', 
                              default_filters=['decode.utf8'], 
                              input_encoding='utf-8')
        page = mytemplate.render(
            projectWebName = project,
            projectName = cherrypy.session.get(str(project)+'_projectName'),
            userLevel = cherrypy.session.get(str(project)+'_loginLevel', 1),
            category = category,
            ticketsList = ticketsList,
            selectedTicketRelativeID = selectedTicket['id'],
            selectedTicketHTML = selectedTicketHTML,
            comments = commentsHTML,
            solved = solved
        )
        
        return page
    
    def getTicketHTML(self, project, lang, category, ticket):
        mytemplate = Template(filename='templates/'+lang+'/ticket.html', 
                              output_encoding='utf-8', 
                              default_filters=['decode.utf8'], 
                              input_encoding='utf-8')
        page = mytemplate.render(
            projectWebName = project,
            category = category,
            ticket = ticket,
            userID = cherrypy.session.get(str(project)+'_idUser', 1),
            userLevel = cherrypy.session.get(str(project)+'_loginLevel', 1))
        return page
        
    
    def search(self, project, search=''):
        con = getConnection()
        checkProjectLogin(con, project)
        lang = projectLang(con, project)
        cursor = con.cursor()
        query = """
        SELECT name FROM Project WHERE webname = %s"""
        cursor.execute(query, (project, ))
        projectName = cursor.fetchone()[0]
        mytemplate = Template(filename='templates/'+lang+'/search.html', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
        tickets = []
        if search is not '':
            query = """
            SELECT
                Ticket.id,
                Ticket.name,
                Ticket.severity,
                Ticket.status,
                Ticket.category,
                Ticket.relativeID,
                ts_rank_cd(
                    setweight(to_tsvector(%(lang)s, no_accents(coalesce(Ticket.name, ''))), 'A') ||
                    setweight(to_tsvector(%(lang)s, no_accents(coalesce(Ticket.description, ''))), 'C') ||
                    setweight(to_tsvector(%(lang)s, no_accents(coalesce(concat_comments(Ticket.id), ''))), 'D'),
                    plainto_tsquery(%(lang)s,no_accents(%(search)s))) AS rank,
                ts_headline(%(lang)s, no_accents(Ticket.name) || ' ' || no_accents(Ticket.description) || ' ' || no_accents(concat_comments(Ticket.id)), plainto_tsquery(%(lang)s, no_accents(%(search)s)))
            FROM Ticket
            WHERE 
                project = %(project)s AND
                to_tsvector(
                    %(lang)s,
                    no_accents(coalesce(Ticket.name, '')) ||
                    no_accents(coalesce(Ticket.description, '')) ||
                    no_accents(coalesce(concat_comments(Ticket.id), ''))
                ) @@ plainto_tsquery(%(lang)s, no_accents(%(search)s))
            ORDER BY rank DESC"""
            # ADD NEW LANGS HERE
            lang_names = {'en': 'english',
                          'fr': 'french'}
            cursor.execute(query,
                           {'project': cherrypy.session.get(str(project)+'_projectCode'),
                            'search': search,
                            'lang': lang_names[lang]})
            rows = cursor.fetchall()
            tickets = []
            for row in rows:
                ticket = {'id': int(row[0]),
                         'name': row[1],
                         'severity': int(row[2]),
                         'status': int(row[3]),
                         'category': int(row[4]),
                         'relativeID': int(row[5]),
                         'headline': row[7] }
                tickets.append(ticket)

        
        page = mytemplate.render(
            projectWebName = project,
            projectName = projectName,
            userLevel = cherrypy.session.get(str(project)+'_loginLevel', 1),
            search = search,
            tickets = tickets
        )
        
        return page
            
    def saveComment(self, project, category, relativeID, content, files=[]):
        """ """
        con = getConnection()
        checkProjectCategoryLogin(con, project, category)
        cursor = con.cursor()
        
        # get ticket ID
        query = """
        SELECT id
        FROM Ticket
        WHERE
            relativeID = %s
            AND project = %s
            AND category = %s"""
        categoryCode = { 'bug' : 1, 'feature' : 2 }
        cursor.execute(query, (relativeID, cherrypy.session.get(str(project)+'_projectCode'), categoryCode[category]) )
        row = cursor.fetchone()
        ticketID = row[0]
        
        # save comment
        query = """
        INSERT INTO Comment(author, ticket, content)
        VALUES (%s,%s,%s);
        SELECT lastval();"""
        
        cursor.execute(query, (cherrypy.session.get(str(project)+'_idUser'), ticketID, formatText(content)) )
        commentID = int(cursor.fetchone()[0])
        
        # attaching files to the comment.
        query = """
        UPDATE File
        SET ticket = %s
        WHERE id = %s"""
        args = []
        if type(files) == type('dummy'):
            args.append((commentID, files))
        elif type(files) == type(['dummy', 'dummy']):        
            for fileID in files :
                args.append( (commentID, fileID) )
        cursor.executemany(query, args)
        con.commit()
        con.close()
        return 'ok'    
    
    def getTicketsList(self, project, category, solved, selectedTicketRelativeID=0):
        """Retrieve tickets and return html code for the tickets"""
        con = getConnection()
        checkProjectCategoryLogin(con, project, category)
        tickets = loadTickets(con, project, category, solved)
        lang = projectLang(con, project)
        unread = updatedTickets(con, project, category, selectedTicketRelativeID)
        con.close()
        ticketsList = self.getTicketsListHTML(project, category, solved, lang, tickets, selectedTicketRelativeID, unread)
        return ticketsList
        
    def getTicketsListHTML(self, project, category, solved, lang, tickets, selectedTicketRelativeID=0, unread={'bug':[], 'feature':[]}):
        """Return html for the tickets provided"""
        mytemplate = Template(filename='templates/'+lang+'/tickets_list.html', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
        ticketsList = mytemplate.render(
            projectWebName = project,
            category = category,
            tickets = tickets,
            selectedTicketRelativeID = selectedTicketRelativeID,
            sortMode = cherrypy.session.get(str(project)+'_sortMode','lastModDown'),
            unread = unread[category]
        )
        return ticketsList
    
    def getCommentsHTML(self, project, lang, comments):
        mytemplate = Template(filename='templates/'+lang+'/comments.html', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
        commentsHTML = mytemplate.render(
            projectWebName = project,
            comments = comments
        )
        return commentsHTML
    
    def getCommentsList(self, project, category, ticketRelativeID):
        con = getConnection()
        checkProjectCategoryLogin(con, project, category)
        lang = projectLang(con, project)
        comments = loadComments(con, project, category, ticketRelativeID)
        commentsHTML = self.getCommentsHTML(project, lang, comments)
        return commentsHTML
        
        
    def ticketForm(self, project, category, status=0, severity=0, name='', description='', files=[], mode='new'):       
        """Return formular used for creating and editing tickets"""
        con = getConnection()
        checkProjectCategoryLogin(con, project, category)
        lang = projectLang(con, project)
        con.close()
        mytemplate = Template(filename='templates/'+lang+'/ticket_form.html', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
        form = mytemplate.render(
            projectWebName = project,
            category = category,
            status = status,
            severity = severity,
            name = name,
            description = unFormatText(description),
            files = files,
            userLevel = cherrypy.session.get(str(project)+'_loginLevel', 1),
            mode = mode
        )
        return form
    
    def editTicketForm(self, project, category, ticketRelativeID):
        con = getConnection()
        checkProjectCategoryLogin(con, project, category)
        query = """
        SELECT 
            Ticket.id,
            Ticket.name,
            Ticket.status,
            Ticket.severity,
            Ticket.description
        FROM Ticket
        WHERE 
            project = %s
            AND category = %s
            AND relativeID = %s"""
        cursor = con.cursor()
        categoryCode = {'bug' : 1, 'feature' : 2}
        cursor.execute(query, (cherrypy.session.get(str(project)+'_projectCode'), categoryCode[category], ticketRelativeID))
        row = cursor.fetchone()
        ticketID = row[0]
        name = row[1]
        status = row[2]
        severity = row[3]
        description = row[4]
        files = []
        query = """
        SELECT 
            File.id,
            File.name
        FROM File 
        WHERE 
            File.type = 'ticket'
            AND File.ticket = %s"""
        cursor.execute(query, ( ticketID, ))
        rows = cursor.fetchall()
        for row in rows:
            files.append({'id': row[0], 'name': row[1]})
        page = self.ticketForm(project, category, status, severity, name, description, files, 'edit')
        return page
    
    def deleteFile(self, project, id):
        """Delete specified file"""
        con = getConnection()
        checkProjectLogin(con, project)
        cursor = con.cursor()
        query="""
        SELECT count(*)
        FROM File
        WHERE id = %s AND project = %s
        """
        cursor.execute(query, (id, cherrypy.session.get(str(project)+'_projectCode')))
        row = cursor.fetchone()
        nb_files = row[0]
        if nb_files == 0:
            con.close()        
            return '1' # code for "no such file available"
        elif nb_files > 1:
            con.close()
            return '2' # this should never ever happen, but just in case: "more than one file was found"
        else:
            # delete file from database
            query = """
            DELETE FROM File
            WHERE id = %s AND project = %s
            """    
            cursor.execute(query, (id, cherrypy.session.get(str(project)+'_projectCode')))
            con.commit()
            con.close()
            # delete file from HDD
            try :
                os.remove('files/'+str(id))
            except :
                pass
            # all went well
            return '0'

    def addFile(self, project, file_type, file, **kwargs):
        """Save uploaded file on HDD and in the database"""
        con = getConnection()
        checkProjectLogin(con, project)
        cursor = con.cursor()
        # insert file into database    
        query = """
        INSERT INTO File (project, name, type)
        VALUES (%s, %s, %s);
        SELECT lastval();
        """
        cursor.execute(query, (cherrypy.session.get(str(project)+'_projectCode'), formatFileName(file.filename), file_type))
        con.commit()
        id = int(cursor.fetchone()[0])
        con.close()
        # saving the file on the disk
        f = open('files/'+str(id), 'w')
        f.write(file.value)
        f.close()
        # we cannot send back a JSON object for ajaxUpload only takes string as input
        # since data to send back is made only of the id, a simple string should be enough
        return 'ok:'+str(id)

    def saveTicket(self, project, category, status, severity, name, description, files=[], **kwargs):
        """Save newly created ticket into the database"""
        con = getConnection()
        checkProjectCategoryLogin(con, project, category)
        cursor = con.cursor()

        categoryCode = {'bug' : 1, 'feature' : 2}
        
        # if ticket is created with status "being taken care of" or "solved", then the user is an admin
        # he is considered as the one who solved or is taking care of the issue.
        idMaintainer = 0
        if int(status) == 1 or int(status) == 2 :
            idMaintainer = cherrypy.session.get(str(project)+'_idUser')
        
        # saving ticket and getting the id of that ticket
        query = """
        INSERT INTO Ticket(project, category, name, description, status, severity, creator, maintainer)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        SELECT lastval();
        """
        cursor.execute(query, (
            cherrypy.session.get(str(project)+'_projectCode'),
            categoryCode[category],
            name,
            formatText(description),
            status,
            severity,
            cherrypy.session.get(str(project)+'_idUser'),
            idMaintainer)
        )
        
        # id of that last ticket created
        id = int(cursor.fetchone()[0])
        
        # relativeID of that last ticket
        query = """
        SELECT relativeID FROM Ticket WHERE id = %s"""
        cursor.execute(query, (id, ))
        relativeID = int(cursor.fetchone()[0])
        
        # attaching files to the ticket
        query = """
        UPDATE File
        SET ticket = %s
        WHERE id = %s"""
        args = []
        
        if type(files) == type('dummy'):
            args.append((id, files))
        elif type(files) == type(['dummy', 'dummy']):        
            for fileID in files :
                args.append( (id, fileID) )
        cursor.executemany(query, args)
        con.commit()
        
        con.close()
        
        data = {'error_code': 0,
                'relativeID': relativeID};
        return demjson.encode(data);

    def newTicket(self, project, category):
        """ newTicket page
        
        This method only returns the new page
        """
        con = getConnection()
        checkProjectCategoryLogin(con, project, category)
        cursor = con.cursor()
        #unread = updatedTickets(con, project, category)
        lang = projectLang(con, project)
        con.close()
        mytemplate = Template(filename='templates/'+lang+'/create.html', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
        page = mytemplate.render(
            projectWebName = project,
            projectName = cherrypy.session.get(str(project)+'_projectName'),
            userLevel = cherrypy.session.get(str(project)+'_loginLevel', 1),
            category = category,
            ticketForm = self.ticketForm(project, category),
            ticketsList = self.getTicketsList(project, category, False)
        )
        return page
    
    def editTicket(self, project, category, relativeID, status, severity, name, description, files=[]):
        """ editTicket page
        
        It works in the same way as newTicket does, but when all arguments are empty, we load values from the DB
        """
        
        con = getConnection()
        
        checkProjectCategoryLogin(con, project, category)
        checkSuperUserOrCreator(con, project, category, relativeID)
        
        categoryCode = {'bug' : 1, 'feature' : 2}
        
        cursor = con.cursor()
        lang = projectLang(con, project)
                
        # we now have a well defined session
        userID = cherrypy.session.get(str(project)+'_id')
        level = cherrypy.session.get(str(project)+'_loginLevel', 1)
        
        idMaintainer = cherrypy.session.get(str(project)+'_idUser', 0)
        
        # updating ticket
        query = """
        UPDATE Ticket
        SET
            name = %s,
            description = %s,
            status = %s,
            severity = %s,
            maintainer = %s,
            lastModification = current_timestamp
        WHERE
            relativeID = %s
            AND project = %s
            AND category = %s"""
        description = formatText(description)
        cursor.execute(query, (name, description, status, severity, idMaintainer, relativeID, cherrypy.session.get(str(project)+'_projectCode'), categoryCode[category] ))
        
        # select real id
        query = """
        SELECT id FROM Ticket
        WHERE project = %s AND relativeID = %s AND category = %s
        """
        cursor.execute(query, (cherrypy.session.get(str(project)+'_projectCode'), relativeID, categoryCode[category] ))
        ticketID = int(cursor.fetchone()[0])
        
        # attaching files to the ticket
        query = """
        UPDATE File
        SET ticket = %s
        WHERE id = %s"""
        args = []
        if type(files) == type('dummy'):
            args.append((ticketID, files))
        elif type(files) == type(['dummy', 'dummy']):        
            for fileID in files :
                args.append( (ticketID, fileID) )
        cursor.executemany(query, args)

        con.commit()
        con.close()
        
        res = {'relativeID' : relativeID}
        return demjson.encode(res)

    def deleteTicket(self, project, category, ticketID) :
        """ deleteTicket page
        
        Deletes the ticket, all files attached, all comments and all of comments' files.
        Then redirects to the home of the category.
        """
        con = getConnection()
        checkProjectCategoryLogin(con, project, category)
        checkSuperUserOrCreator(con, project, category, ticketID)
        lang = projectLang(con, project)
        categoryCode = {'bug' : 1, 'feature' : 2}
        cursor = con.cursor()
        # selecting real id
        query = """
        SELECT id
        FROM Ticket
        WHERE
            relativeID = %s
            AND project = %s
            AND category = %s"""
        categoryCode = { 'bug' : 1, 'feature' : 2 }
        cursor.execute(query, (ticketID, cherrypy.session.get(str(project)+'_projectCode'), categoryCode[category]) )
        row = cursor.fetchone()
        id = row[0]
        # delete file
        # on the disk
        query = """
        SELECT id FROM File
        WHERE
            (   type = 'ticket' AND ticket = %s     )
            OR (    type='comment' AND ticket in (SELECT id FROM Comment WHERE ticket = %s)     )
        """
        cursor.execute(query, (id, id ) )
        rows = cursor.fetchall()
        for row in rows :
            file = 'files/'+str(row[0])
            try :
                os.remove(file)
            except :
                print 'file not found or at least can\'t be deleted'
        # on the db
        query = """
        DELETE FROM File
        WHERE
            (   type = 'ticket' AND ticket = %s     )
            OR (    type='comment' AND ticket in (SELECT id FROM Comment WHERE ticket = %s)     )
        """
        cursor.execute(query, (id, id ) )
        
        # delete comments
        query = """
        DELETE FROM Comment
        WHERE ticket = %s"""
        cursor.execute(query, (id, ) )
        
        # delete ticket
        query = """
        DELETE FROM Ticket
        WHERE
            relativeID = %s
            AND project = %s
            AND category = %s
        """
        cursor.execute(query, (ticketID, cherrypy.session.get(str(project)+'_projectCode'), categoryCode[category]))
        con.commit()
        con.close()
        
        return 'ok'
    

    
    # ERROR METHOD
    
    def raiseError(self) :
        """ raising the error page
        """
        raise cherrypy.HTTPRedirect( url('new') )
    
    # LOGIN METHODS
    def logMeIn(self, project=None, category='bug', idTicket=0, login='', password='') :
        """ logMeIn form.
        """
        con = getConnection()
        checkProject(con, project)
        lang = projectLang(con, project)
        query = "SELECT name FROM project WHERE webname=%s"
        cursor = con.cursor()
        cursor.execute(query, (project, ))
        row = cursor.fetchone()
        projectName = row[0]
        con.close()
        mytemplate = Template(filename='templates/'+lang+'/login.html', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
        page = mytemplate.render(
            projectWebName = project,
            projectName = projectName,
            login = login,
            category = category,
            password = password,
            idTicket = idTicket,
            error = '',
            comingFrom = cherrypy.session.get(str(project)+'_previousPage', url(project))
        )
        return page
    
    def doLogin(self, project, login, password):
        con = getConnection()
        checkProject(con, project)
        cursor = con.cursor()
        query = """
        SELECT
            Client.id,
            Client.level
        FROM Client
        INNER JOIN Project
        ON Client.project = Project.id
        WHERE
            Client.login = %s
            AND Client.password = %s
            AND Project.webname = %s
            AND Client.allowed = True
            AND Client.isDeleted = False"""
        # encoding password
        m = md5.new()
        m.update(password)
        m.update(project)
        m.update(login)
        cursor.execute(query, (login, m.hexdigest(), project))
        # fetching the results
        id = None
        level = None
        rows = cursor.fetchall()
        for row in rows :
            id = row[0]
            level = row[1]
        # is the login ok ?
        if id == None or level == None:
            con.close()
            return 'no'
        else:
            con.close()
            # saving to the session
            cherrypy.session[str(project)+'_idUser'] = id
            cherrypy.session[str(project)+'_loginLevel'] = level
            return 'ok'
            
    
    def disconnect(self, project) :
        """ destroy session
        """
        try :
            cherrypy.session.delete()
        except :
            pass
        raise cherrypy.HTTPRedirect( url(project) )
    
    def register(self, project):
        con = getConnection()
        checkProject(con, project)
        lang = projectLang(con, project)
        mytemplate = Template(filename='templates/'+lang+'/register.html', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
        page = mytemplate.render(
            projectWebName = project,
        )
        return page
        
    def doRegister(self, projectWebName, login, pwd1, pwd2, email):
        con = getConnection()
        checkProject(con, projectWebName)
        lang = projectLang(con, projectWebName)
        # clean data
        login = login.strip()
        pwd1 = pwd1.strip()
        pwd2 = pwd2.strip()
        email = email.strip()
        # check data
        errors = {  'equalPwd': True,
            'emptyPwd': (pwd1 == '' or pwd2 == ''),
            'emptyLogin': login=='',
            'emptyEMail': email=='',
            'loginTaken': False,
            'ok': False}
        # pwd1 and pwd2 are equal
        if pwd1 != pwd2 :
                errors['equalPwd'] = False
        # login is already taken
        query = """
        SELECT count(*) FROM Client
        WHERE project = %s AND login = %s"""
        cursor = con.cursor()
        cursor.execute(query, (cherrypy.session.get(str(projectWebName)+'_projectCode'), login))
        if int(cursor.fetchone()[0]) > 0:
                errors['loginTaken'] = True
        #   return errors
        if errors['emptyPwd'] or errors['emptyLogin'] or errors['emptyEMail'] or not errors['equalPwd'] or errors['loginTaken']:
                return demjson.encode(errors)
        # no error were found, just go on with the normal procedure
        query = """
        INSERT INTO Client(login, password, project, level, allowed, mail)
        VALUES (%s, %s, %s, 1, False, %s)"""
        m = md5.new()
        m.update(pwd1)
        m.update(projectWebName)
        m.update(login)
        cursor.execute(query, (login, m.hexdigest(), cherrypy.session.get(str(projectWebName)+'_projectCode'), email))
        con.commit()
        # send emails
        # to admins
        # get projectName
        query = """
        SELECT name
        FROM Project
        WHERE Project.id = %s"""
        cursor.execute(query, (cherrypy.session.get(str(projectWebName)+'_projectCode'), ))
        projectName = cursor.fetchone()[0]
        # send mails to all admins            
        query = """
        SELECT login, mail
        FROM Client
        WHERE project = %s AND level = 2"""
        cursor.execute(query, (cherrypy.session.get(str(projectWebName)+'_projectCode'), ))
        rows = cursor.fetchall()
        for row in rows :
            emailTemplate = Template(filename='templates/'+lang+'/mails/new_user.mail', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
            emailContent = emailTemplate.render(
                to = row[1],
                userName = row[0],
                projectName = projectName,
                projectWebName = projectWebName)
            sendMail(row[1], emailContent)
            # to new user
            emailTemplate = Template(filename='templates/'+lang+'/mails/registration.mail', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
            emailContent = emailTemplate.render(
                to = email,
                userName = login,
                projectName = projectName,
                projectWebName = projectWebName,
                password = pwd1)
        sendMail(email, emailContent)
        errors['ok'] = True
        return demjson.encode(errors)              
                        
                    
    def users(self, project):
        con = getConnection()
        checkProjectLoginLevel(con, project)
        lang = projectLang(con, project)
        cursor = con.cursor()
        query = """
        SELECT name FROM Project WHERE id = %s"""
        cursor.execute(query, (cherrypy.session.get(str(project)+'_projectCode'), ))
        projectName = cursor.fetchone()[0]
        # get users
        query = """
        SELECT
            CLient.id,
            Client.login,
            Client.mail,
            Client.level,
            Client.allowed,
            Client.isDeleted
        FROM Client
        WHERE project = %s"""
        cursor.execute(query, (cherrypy.session.get(str(project)+'_projectCode'), ))
        rows = cursor.fetchall()
        users = []
        requests = []
        deleted = []
        for row in rows:
            isDeleted = row[5]
            isAllowed = row[4]
            if isDeleted:
                deleted.append({'id': row[0], 'login': row[1], 'mail': row[2], 'level': row[3]})
            elif isAllowed:
                users.append({'id': row[0], 'login': row[1], 'mail': row[2], 'level': row[3]})
            else:
                requests.append({'id': row[0], 'login': row[1], 'mail': row[2], 'level': row[3]})
        con.close()
        mytemplate = Template(filename='templates/'+lang+'/users.html', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
        page = mytemplate.render(
            projectWebName = project,
            projectName = projectName,
            users = users,
            requests = requests,
            deletedUsers = deleted
        )
        return page
    
    def deleteUser(self, project, userID):
        con = getConnection()
        checkProjectLoginLevel(con, project)
        lang = projectLang(con, project)
        cursor = con.cursor()
        # check that user does exist
        query = """
        SELECT count(*) FROM Client WHERE project = %s AND id = %s"""
        cursor.execute(query, (cherrypy.session.get(str(project)+'_projectCode'), userID))
        n = int(cursor.fetchone()[0])
        if n == 1:
            # check that user is not the project's owner
            query = """
            SELECT owner FROM Project WHERE id = %s"""
            cursor.execute(query, (cherrypy.session.get(str(project)+'_projectCode'), ))
            row = cursor.fetchone()
            ownerID = row[0]
            if int(ownerID) != int(userID) :
                # send revocation or rejection email
                query = """
                SELECT Client.mail, Client.login, Project.webname, Project.name, Client.allowed
                FROM Client
                INNER JOIN Project
                ON Client.project = Project.id
                WHERE Client.project = %s AND Client.id = %s"""
                cursor.execute(query, (cherrypy.session.get(str(project)+'_projectCode'), userID))
                row = cursor.fetchone()
                mail = row[0]
                userName = row[1]
                projectWebName = row[2]
                projectName = row[3]
                isAllowed = row[4]
                if isAllowed:
                    mailType = 'revocation'
                else:
                    mailType = 'rejection'
                emailTemplate = Template(filename='templates/'+lang+'/mails/'+mailType+'.mail', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
                email = emailTemplate.render(
                    to = mail,
                    userName = userName,
                    projectName = projectName,
                    projectWebName = projectWebName,
                )
                sendMail(mail, email)
                # delete user
                # if the user was already in the project, we don't really delete it
                # we just set isDeleted to True so that he can't log in anymore
                if isAllowed:
                    query = """
                    UPDATE Client
                    SET isDeleted = True
                    WHERE project = %s AND id = %s"""
                else:
                    query = """
                    DELETE FROM Client WHERE project = %s AND id = %s"""    
                cursor.execute(query, (cherrypy.session.get(str(project)+'_projectCode'), userID))
                con.commit()
                con.close()
                return 'ok'
            else:
                con.close()
                return 'owner'
        else:
            con.close()
            return 'no'

    def acceptUser(self, project, userID, level):
        con = getConnection()
        checkProjectLoginLevel(con, project)
        lang = projectLang(con, project)
        cursor = con.cursor()
        # check that level is a valid value
        if int(level) is not 1 and int(level) is not 2:
            con.close()
            return 'no'
        # check that user does exist
        query = """
        SELECT count(*) FROM Client WHERE project = %s AND id = %s AND allowed = False"""
        cursor.execute(query, (cherrypy.session.get(str(project)+'_projectCode'), userID))
        n = int(cursor.fetchone()[0])
        if n == 1:
            # accept user
            query = """
            UPDATE Client SET allowed = True AND level = %s WHERE project = %s AND id = %s"""
            cursor.execute(query, (level, cherrypy.session.get(str(project)+'_projectCode'), userID))
            con.commit()
            # send him an email to let him know he's in
            query = """
            SELECT Client.mail, Client.login, Project.webname, Project.name
            FROM Client
            INNER JOIN Project
            ON Client.project = Project.id
            WHERE Client.project = %s AND Client.id = %s"""
            cursor.execute(query, (cherrypy.session.get(str(project)+'_projectCode'), userID))
            row = cursor.fetchone()
            mail = row[0]
            userName = row[1]
            projectWebName = row[2]
            projectName = row[3]
            emailTemplate = Template(filename='templates/'+lang+'/mails/acceptation.mail', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
            email = emailTemplate.render(
                to = mail,
                userName = userName,
                projectName = projectName,
                projectWebName = projectWebName,
            )
            sendMail(mail, email) 
            con.close()
            return 'ok'
        else:
            con.close()
            return 'no'
    
    def updateUserLevel(self, project, userID, level):
        con = getConnection()
        checkProjectLoginLevel(con, project)
        lang = projectLang(con, project)
        cursor = con.cursor()
        # check that level is a valid value
        if int(level) is not 1 and int(level) is not 2:
            con.close()
            return 'no'
        # check that user does exist
        query = """
        SELECT count(*) FROM Client WHERE project = %s AND id = %s"""
        cursor.execute(query, (cherrypy.session.get(str(project)+'_projectCode'), userID))
        n = int(cursor.fetchone()[0])
        if n == 1:
            # update user level
            query = """
            UPDATE Client SET level = %s WHERE project = %s AND id = %s"""
            cursor.execute(query, (level, cherrypy.session.get(str(project)+'_projectCode'), userID))
            con.commit()
            # send him a mail to let him know his new status
            query = """
            SELECT Client.mail, Client.login, Project.webname, Project.name
            FROM Client
            INNER JOIN Project
            ON Client.project = Project.id
            WHERE Client.project = %s AND Client.id = %s"""
            cursor.execute(query, (cherrypy.session.get(str(project)+'_projectCode'), userID))
            row = cursor.fetchone()
            mail = row[0]
            userName = row[1]
            projectWebName = row[2]
            projectName = row[3]
            emailTemplate = Template(filename='templates/'+lang+'/mails/modification.mail', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
            email = emailTemplate.render(
                to = mail,
                userName = userName,
                projectName = projectName,
                projectWebName = projectWebName,
                level = level
            )
            sendMail(mail, email)
            con.close()
            return 'ok'
        else:
            con.close()
            return 'no'        
    
    def sendInvitations(self, project, to, msg) :
        """ sendInvitations page
        
        This is not a real page. It sends all invitations sent using the form found on the manageUsers page but has not a page on its own.
        The page displayed at the end is the manageUsers one, with a message to confirm that mails were sent.
        """
        
        con = getConnection()
        
        checkProjectLoginLevel(con, project)
        
        cursor = con.cursor()
        
        lang = projectLang(con, project)
        
        # getting author name
        query = """
        SELECT login
        FROM Client
        WHERE id = %s AND project = %s"""
        cursor.execute(query, (cherrypy.session.get(str(project)+'_idUser'), cherrypy.session.get(str(project)+'_projectCode') ) )
        rows = cursor.fetchall()
        author = 'unknown user'
        for row in rows :
            author = row[0]
        
        # processing "to" field (ie mail addresses)
        mails = to.split(';')
        for mail in mails :
            mail = mail.strip()
            emailTemplate = Template(filename='templates/'+lang+'/mails/invitation.mail', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
            email = emailTemplate.render(
                to = mail,
                msg = msg,
                author = author,
                projectName = cherrypy.session.get(str(project)+'_projectName'),
                projectWebName = project
            )
            sendMail(mail, email)
        
        con.close()
        return 'ok'

    def newProject(self, lang='en'):
        con = getConnection()
        con.close()
        langs = ['en', 'fr']
        if lang not in langs:
            lang = 'en'
        mytemplate = Template(filename='templates/'+lang+'/new_project.html', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
        page = mytemplate.render()
        return page
        
    def createProject(self, projectName, projectWebName, login, pwd1, pwd2, email, lang):
        langs = ['en', 'fr']
        if lang not in langs:
            lang = 'en'
        # clean data
        projectName = projectName.strip()
        projectWebName = projectWebName.strip().lower()
        login = login.strip()
        pwd1 = pwd1.strip()
        pwd2 = pwd2.strip()
        email = email.strip()
        # check data
        errors = {  'validChars': True,
                    'equalPwd': True,
                    'validProjectWebName': True,
                    'emptyPwd': (pwd1 == '' or pwd2 == ''),
                    'emptyLogin': login=='',
                    'emptyProjectWebName': projectWebName=='',
                    'emptyProjectName': projectName == '',
                    'emptyEMail': email=='',
                    'ok': False}
        # the webname does not contains special chars
        validChars = "0123456789abcdefghijklmnopqrstuvwxyz"
        for c in projectWebName :
            if c not in validChars :
                errors['validChars'] = False
        # pwd1 and pwd2 are equal
        if pwd1 != pwd2 :
            errors['equalPwd'] = False
        # checking that a project with the same webname does not already exists
        con = getConnection()
        cursor = con.cursor()
        query = """
        SELECT count(*)
        FROM Project
        WHERE webname = %s"""
        cursor.execute(query, (projectWebName, ))
        row = cursor.fetchone()
        if row[0] >= 1 :
            errors['validProjectWebName'] = False
        # if there are errors, just send them back to the page
        error = errors['emptyPwd'] or errors['emptyLogin'] or errors['emptyProjectWebName'] or errors['emptyProjectName'] or errors['emptyEMail']
        error = error or not errors['validChars'] or not errors['equalPwd'] or not errors['validProjectWebName']
        if error:
            return demjson.encode(errors)
        # no error were found, just go on with the normal procedure
        # create project
        query = """
        INSERT INTO Project(name, webname, lang)
        VALUES (%s, %s, %s)"""
        cursor.execute(query, (projectName, projectWebName, lang))
        con.commit()
        checkProject(con, projectWebName)
        # add superuser for the project
        query = """
        INSERT INTO Client(login, password, project, level, allowed, mail)
        VALUES (%s, %s, %s, 2, True, %s);
        SELECT lastval();"""
        m = md5.new()
        m.update(pwd1)
        m.update(projectWebName)
        m.update(login)
        cursor.execute(query, (login, m.hexdigest(), cherrypy.session.get(str(projectWebName)+'_projectCode'), email))
        adminID = int(cursor.fetchone()[0])
        # updating project owner :
        query = """
        UPDATE Project
        SET owner = %s
        WHERE webname = %s"""
        cursor.execute(query, (adminID, projectWebName))
        con.commit()
        con.close()
        # send email
        emailTemplate = Template(filename='templates/'+lang+'/mails/new_project.mail', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
        emailContent = emailTemplate.render(
            to = email,
            userName = login,
            projectName = projectName,
            projectWebName = projectWebName,
            password = pwd1
        )
        sendMail(email, emailContent)
        errors['ok'] = True
        return demjson.encode(errors)
    
    def files(self, project, id):
        """ Serves the file defined by the id.
        """
        con = getConnection()
        
        checkProjectLogin(con, project)
        
        cursor = con.cursor()
        
        # selecting file name
        name = None
        query = """
        SELECT name from File
        WHERE project = %s AND id = %s"""
        cursor.execute(query, (cherrypy.session.get(str(project)+'_projectCode'), id))
        try :
            name = cursor.fetchone()[0]
        except :
            pass
        
        con.close()
        
        # if the file was found in the database
        if(name != None) :
            # finding mimetype so that file can be served correcly
            ext = ""
            i = name.rfind('.')
            if i != -1:
                ext = name[i:].lower()
            mimetypes.init()
            mimetypes.types_map['.dwg']='image/x-dwg'
            mimetypes.types_map['.ico']='image/x-icon'
            content_type = mimetypes.types_map.get(ext, "text/plain")
            # serving file
            return serve_file(os.path.join(_curdir, './files/%s' % id), content_type = content_type, disposition="attachment", name=name)
        # the file was not found
        else :
            raise cherrypy.NotFound
    
    def setSort(self, project, mode):
        con = getConnection()
        checkProjectLogin(con, project)
        con.close()
        # all possible modes
        modes = ['lastModDown', 'lastModUp', 'idDown', 'idUp', 'severityDown', 'severityUp', 'statusDown', 'statusUp' ]
        if mode not in modes :
            return 'error: non valid mode'
        # saving value
        cherrypy.session[str(project)+'_sortMode'] = mode
        return 'mode set'
    
    def profile(self, project):
        con = getConnection()
        checkProjectLogin(con, project)
        lang = projectLang(con, project)
        
        cursor = con.cursor()
        query = """
        SELECT name FROM Project WHERE id = %s"""
        cursor.execute(query, (cherrypy.session.get(str(project)+'_projectCode'), ))
        projectName = cursor.fetchone()[0]
        query="""
        SELECT login, level, mail FROM Client WHERE id = %s"""
        cursor.execute(query, (cherrypy.session.get(str(project)+'_idUser'), ))
        row = cursor.fetchone()
        login = row[0]
        level = row[1]
        mail = row[2]
        mytemplate = Template(filename='templates/'+lang+'/profile.html', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
        page = mytemplate.render(
            projectWebName = project,
            projectName = projectName,
            userLevel = cherrypy.session.get(str(project)+'_loginLevel', 1),
            login = login,
            mail = mail
        )
        return page
    
    def updateEMail(self, project, mail):
        con = getConnection()        
        checkProjectLogin(con, project)
        cursor = con.cursor()
        query = """UPDATE Client SET mail = %s WHERE id = %s"""
        cursor.execute(query, (mail, cherrypy.session.get(str(project)+'_idUser')))
        con.commit()
        con.close()
        return 'ok'
    
    def updatePwd(self, project, pwd1, pwd2):
        con = getConnection()        
        checkProjectLogin(con, project)
        if pwd1 != pwd2:
            con.close()
            return 'no'
        cursor = con.cursor()
        query = """
        SELECT login FROM Client WHERE id = %s"""
        cursor.execute(query, (cherrypy.session.get(str(project)+'_idUser'), ))
        login = cursor.fetchone()[0]
        m = md5.new()
        m.update(pwd1)
        m.update(project)
        m.update(login)
        query = """
        UPDATE Client
        SET password = %s
        WHERE id = %s AND project = %s"""
        cursor.execute(query, (m.hexdigest(), cherrypy.session.get(str(project)+'_idUser'), cherrypy.session.get(str(project)+'_projectCode')))
        con.commit()
        con.close()
        return 'ok'
    
    def lostPassword(self, project):
        con = getConnection()
        checkProject(con, project)
        lang = projectLang(con, project)
        mytemplate = Template(filename='templates/'+lang+'/lost_password.html', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
        page = mytemplate.render(
            projectWebName = project,
        )
        return page
    
    def doLostPassword(self, projectWebName, login):
        con = getConnection()
        checkProject(con, projectWebName)
        lang = projectLang(con, projectWebName)
        cursor = con.cursor()
        login = login.strip()
        query = """
        SELECT id, mail FROM Client
        WHERE project = %s AND login = %s AND isDeleted = False"""
        cursor.execute(query, (cherrypy.session.get(str(projectWebName)+'_projectCode'), login))
        rows = cursor.fetchall()
        n = 0
        for row in rows:
            n = n + 1
            userID = int(row[0])
            mail = row[1]
        if  n == 0:
            return 'not found'
        else:
            # update the password
            newPassword = randomPwd()
            # encrypting the password
            m = md5.new()
            m.update(newPassword)
            m.update(projectWebName)
            m.update(login)
            query = """
            UPDATE Client
            SET password = %s
            WHERE id = %s AND project = %s"""
            cursor.execute(query, (m.hexdigest(), userID, cherrypy.session.get(str(projectWebName)+'_projectCode')) )
            con.commit()
            # sending email with new password
            query = """
            SELECT name FROM Project WHERE id = %s"""
            cursor.execute(query, (cherrypy.session.get(str(projectWebName)+'_projectCode'), ))
            projectName = cursor.fetchone()[0]
            emailTemplate = Template(filename='templates/'+lang+'/mails/lost_password.mail', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
            email = emailTemplate.render(
                to = mail,
                userName = login,
                projectName = projectName,
                projectWebName = projectWebName,
                newPwd = newPassword
            )
            sendMail(mail, email)
        return 'ok'