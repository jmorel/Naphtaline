import cherrypy

def loadTickets(con, project, category, solved):
    """ Load tickets (solved/rejected ones or active ones) corresponding to the specified project for the specified category with the specified status (if solved is True then I have to load only solved/rejected tickets)
    
    The result is a list of hash with keys id, name, severity, status (ie all values used in the list of tickets on the main page)
    Note that id is again the relative id and not the absolute one.
    
    Results are sorted depending on the value of _sortMode (value setted through the sort method)
    """
    
    codeCategory = {'bug' : 1, 'feature' : 2}
    
    cursor = con.cursor()
    query = """
    SELECT
        Ticket.relativeID,
        Ticket.name,
        Ticket.severity,
        Ticket.status
    FROM Ticket
    
    INNER JOIN Project
    ON Project.id = Ticket.project
    
    WHERE
        Project.webname = %s
        AND Ticket.category = %s"""
    if str(solved).lower() == 'true': # using str() around a boolean is pretty ugly, but it's javascript is passing text variables
        query += """
        AND (Ticket.status = 1 OR Ticket.status = 4)"""
    else:
        query += """
        AND (Ticket.status = 2 OR Ticket.status = 3)""" 
    
    query += """
    ORDER BY """
    if cherrypy.session.get(str(project)+'_sortMode','lastModDown') == 'lastModDown' :
        query += """ Ticket.lastModification DESC"""
    elif cherrypy.session.get(str(project)+'_sortMode','lastModDown') == 'lastModUp' :
        query += """ Ticket.lastModification ASC"""
    elif cherrypy.session.get(str(project)+'_sortMode','lastModDown') == 'idDown' :
        query += """ Ticket.relativeID DESC"""
    elif cherrypy.session.get(str(project)+'_sortMode','lastModDown') == 'idUp' :
        query += """ Ticket.relativeID ASC"""
    elif cherrypy.session.get(str(project)+'_sortMode','lastModDown') == 'severityDown' :
        query += """ Ticket.severity DESC"""
    elif cherrypy.session.get(str(project)+'_sortMode','lastModDown') == 'severityUp' :
        query += """ Ticket.severity ASC"""
    elif cherrypy.session.get(str(project)+'_sortMode','lastModDown') == 'statusDown' :
        query += """ Ticket.status DESC"""
    elif cherrypy.session.get(str(project)+'_sortMode','lastModDown') == 'statusUp' :
        query += """ Ticket.status ASC"""   
    cursor.execute(query, (project, codeCategory[category]))
    rows = cursor.fetchall()
    
    tickets = []
    
    for row in rows :
        ticket = { 'relativeID' : row[0], 'name' : row[1], 'severity' : row[2], 'status' : row[3] }
        tickets.append(ticket)
    return tickets

def loadSelectedTicket(con, project, category, id) :
    """ Loads and returns all data corresponding to the ticket of relative id 'id' in the project 'project' and category 'category'.
    Comments are have to be loaded through the loadComments method.
    
    The result is a hash looking like that :
        id : relative id of the ticket (int)
        name : name of the ticket (str)
        status, severity : 1 <= (int) <= 3
        creationDate, lastModification : (date) not used at the moment
        description : (str)
        files : list  of files (see below)
        comments : list of comments (see below)
    
    The files list :
        it is a list of hashes containing only two keys : "id" and "name"
        these two values allow us to retrieve the file and serve it with the real name
    """
    
    categoryCode = { 'bug' : 1, 'feature' : 2 }
    
    # default value that will be returned if no data were to be found
    ticket = {
        'id' : id,
        'name' : ' ',
        'status' : 0,
        'severity' : 0,
        'creator' : ' ',
        'creatorID' : 0,
        'maintainer' : ' ',
        'creationDate' : {'day' : 0, 'month' : 0, 'year' : 0},
        'lastModification' : {'day' : 0, 'month' : 0, 'year' : 0},
        'description' : ' ',
        'files' : []
    }
    
    cursor = con.cursor()
    
    # selecting ticket characteristics
    query = """
    SELECT
        Ticket.id,
        Ticket.name,
        Ticket.status,
        Ticket.severity,
        Author.login,
        Author.id,
        Maintainer.login,
        extract(day FROM Ticket.creationDate),
        extract(month FROM Ticket.creationDate),
        extract(year FROM Ticket.creationDate),
        extract(day FROM Ticket.lastModification),
        extract(month FROM Ticket.lastModification),
        extract(year FROM Ticket.lastModification),
        Ticket.description
    FROM Ticket
    
    INNER JOIN Project
    ON Ticket.project = Project.id
    
    INNER JOIN Client as Author
    ON Ticket.creator = Author.id
    
    LEFT JOIN Client as Maintainer
    ON Ticket.maintainer = Maintainer.id
    WHERE
        Project.webname = %s
        AND Ticket.category = %s
        AND Ticket.relativeID = %s
        
    ORDER BY
        Ticket.lastModification"""
 
    cursor.execute(query, (project, categoryCode[category], id))
    rows = cursor.fetchall()
    
    realID = None
    
    for row in rows :      
        realID = row[0]
        ticket = {
            'id' : id,
            'name' : row[1],
            'status' : row[2],
            'severity' : row[3],
            'creator' : row[4],
            'creatorID' : int(row[5]),
            'maintainer' : str(row[6]),
            'creationDate' : {'day' : int(row[7]), 'month' : int(row[8]), 'year' : int(row[9])},
            'lastModification' : {'day' : int(row[10]), 'month' : int(row[11]), 'year' : int(row[12])},
            'description' : row[13],
            'files' : []
        }
    
    # selecting attached files
    query = """
    SELECT id, name
    FROM File
    WHERE ticket = %s AND type = %s"""
    cursor.execute(query, (realID, 'ticket') )
    rows = cursor.fetchall()
    files = []
    for row in rows :
        files.append({'id' : row[0], 'name' : row[1]})
    ticket['files'] = files
    
    return ticket
    
def loadComments(con, project, category, relativeID):
    """ Load and return an ordinated (based on creation date) of all comment attached to a given ticket.
    Result is a list of hash. Each hash represents a comment and has keys 
        "id", "name", "author", "content" and "files"
        "name", "author" and "content" are strings
        "id" is an int and does not serve at the moment since the id displayed is generating on the fly for each ticket.
        "files" contains a list of hash like described before.
    """

    cursor = con.cursor()
    
    query = """
    SELECT Ticket.id
    FROM Ticket
    INNER JOIN Project
    ON Ticket.project = Project.id
    WHERE 
        Project.webname = %s 
        AND Ticket.category = %s 
        AND Ticket.relativeID = %s"""
    categoryCode = { 'bug' : 1, 'feature' : 2 } 
    cursor.execute(query, (project, categoryCode[category], relativeID))
    row = cursor.fetchone()
    ticketID = row[0]
    
    comments = []
    
    query = """
    SELECT
        Comment.id,
        Client.login,
        Comment.content,
        extract(day FROM Comment.creationDate),
        extract(month FROM Comment.creationDate),
        extract(year FROM Comment.creationDate)
    FROM Comment
    INNER JOIN Client
    ON Comment.author = Client.id
    WHERE
        Comment.ticket = %s
    ORDER BY Comment.creationDate ASC"""
    cursor.execute(query, (ticketID, ))
    rows = cursor.fetchall()
    comments = []
    for row in rows :
        # for each comment, selecting files
        query = """
        SELECT id, name
        FROM File
        WHERE ticket = %s AND type = %s"""
        cursor.execute(query, (row[0], 'comment'))
        files = []
        for file in cursor.fetchall() :
            files.append({'id' : file[0], 'name' : file[1]})
        comments.append({
            'id' : row[0],
            'author' : row[1],
            'content' : row[2],
            'date' : {'day' : int(row[3]), 'month' : int(row[4]), 'year' : int(row[5])},
            'files' : files})
    return comments

    
def updatedTickets(con, project, category, ticketID=0) :
    """ Checks whether tickets were modified or added since lastLogin.
    Also keeps updated the list of this tickets by removing the currently visited one.
    Updates the value of lastLogin in the DB.
    """
    # this is the array we will return
    unread = {'bug' : [], 'feature' : []}
    
    # first thing to do: retrieve tickets that we know are not read from 3 different sources
    # from the session
    # from the cookie
    # from the database (new unread tickets since last connection)
    
    # from session
    unreadInSession = cherrypy.session.get(str(project)+'_unread', {'bug' : [], 'feature' : []})
    # from cookie
    unreadInCookie = {'bug' : [], 'feature' : []}
    cookie = cherrypy.request.cookie
    for name in cookie.keys():
        cookieToCategory = {str(project)+'_bug': 'bug', str(project)+'_feature': 'feature'}
        if name ==  str(project)+'_bug' or name == str(project)+'_feature':
            value = cookie[name].value
            if value is not '':
                IDs = value.split(',')
                IDs = map(int, IDs)
            else:
                IDs = []
            unreadInCookie[cookieToCategory[name]] = IDs
    # from database
    newUnread = {'bug' : [], 'feature' : []}
    categoryCode = { 'bug' : 1, 'feature' : 2 }
    categoryLabel = {1 : 'bug', 2 : 'feature'}
    cursor = con.cursor()
    query = """
    SELECT
        Ticket.relativeID,
        Ticket.category
    FROM Ticket
    INNER JOIN Project
    ON Ticket.project = Project.id
    LEFT JOIN Client
    ON Ticket.lastModification > Client.lastLogin
    WHERE
        Project.webname = %s
        AND Client.id = %s"""
    cursor.execute(query, (project, cherrypy.session.get(str(project)+'_idUser') ))
    rows = cursor.fetchall()
    for row in rows :
        if row[0] not in unread[categoryLabel[row[1]]] :
            newUnread[categoryLabel[row[1]]].append(row[0])
    # updating the lastLogin field
    query = """
    UPDATE Client
    SET lastLogin = current_timestamp
    WHERE id = %s"""
    cursor.execute(query, (cherrypy.session.get(str(project)+'_idUser'), ) )
    con.commit()
    
    # blend all 3 sources together
    for type in ['bug', 'feature']:
        l = set()
        l.update(unreadInSession[type])
        l.update(unreadInCookie[type])
        l.update(newUnread[type])
        unread[type] = list(l)
            
    # removing the currently visited post
    ticketID = int(ticketID)
    if ticketID in unread[category] :
        unread[category].remove(ticketID)
        
    # saving data to the session and to the cookie
    # session
    cherrypy.session[str(project)+'_unread'] = unread
    # cookie
    # delete existing cookie
    #for cookieName in [project+'_bug', project+'_feature']:
    #    cherrypy.response.cookie[cookieName] = ''
    #    cherrypy.response.cookie[cookieName]['expires'] = 0
    # save cookie
    cookie = cherrypy.response.cookie
    for cat in ['bug', 'feature']:
        cookieName = str(project)+'_'+cat
        cookie = cherrypy.response.cookie
        cookie[cookieName] = str.join(',', map(str, unread[cat]))
        cookie[cookieName]['path'] = '/' + project
        cookie[cookieName]['max-age'] = 1036800 # this is a year
    return unread
