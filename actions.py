
import cherrypy

def doAddComment(con, project, category, idEntry, content, **kwargs) :
    """ Process arguments from a "new comment" request
    Return the id of the newly created comment
    """
    cursor = con.cursor()
    
    files = []
    
    # saving files
    for key in kwargs.keys() :
        
        if 'file' in key :
            
            file = kwargs[key]
            # creating the file in the database
            
            query = """
            INSERT INTO File (project, name, type)
            VALUES (%s, %s, %s);
            SELECT lastval();
            """
            cursor.execute(query, (cherrypy.session.get(str(project)+'_projectCode'), file.filename, 'comment'))
            id = int(cursor.fetchone()[0])
            # adding the file to the list of attached files
            files.append({'id' : id, 'name' : file.filename})
            # saving the file on the disk
            f = open('files/'+str(id), 'w')
            f.write(file.file.read())
            f.close()
    
    ## saving comment
    
    # getting the real id of the post
    query = """
    SELECT id
    FROM Entry
    WHERE
        relativeID = %s
        AND project = %s
        AND category = %s"""
    categoryCode = { 'bug' : 1, 'feature' : 2 }
    cursor.execute(query, (idEntry, cherrypy.session.get(str(project)+'_projectCode'), categoryCode[category]) )
    row = cursor.fetchone()
    id = row[0]
    
    # saving comment
    query = """
    INSERT INTO Comment(author, entry, content)
    VALUES (%s,%s,%s);
    SELECT lastval();"""
    
    content = self.formatText(content)
    
    cursor.execute(query, (cherrypy.session.get(str(project)+'_idUser'), id, content) )
    idComment = int(cursor.fetchone()[0])
    
    # attaching files to the comment.
    query = """
    UPDATE File
    SET entry = %s
    WHERE id = %s"""
    args = []
    for file in files :
        args.append( (idComment, file['id']) )
    cursor.executemany(query, args)
    
    con.commit()
    
    return idComment