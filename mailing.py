import cherrypy
from various import *
from mako.template import Template
import smtplib

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate, make_msgid
from email import Encoders
from email.Header import Header

from passwords import smtp_server, smtp_login, smtp_password

def getSMTPServer() :
    server = smtplib.SMTP(smtp_server)
    server.login(smtp_login, smtp_password)
    return server

def sendMail(to, mail) :
    """ Send a mail to a specified address. The mail comes from noreply@naphtaline.com and should never be responded to
    """
    try :
        server = getSMTPServer()
        server.sendmail('noreply@naphtaline.com', to, mail)
        server.quit()
    except :
        pass


def send_mail(mail):
  
    msg = MIMEMultipart()
    msg.set_charset('utf-8')
    msg['From'] = mail['From']
    msg['Bcc'] = COMMASPACE.join(mail['To'])
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = mail['Subject']
    msg['Reply-To'] = mail['Reply-To']
    msg['Message-ID'] = mail['Message-ID']
    msg['In-Reply-To'] = mail['In-Reply-To']
    #msg['Content-Type'] = 'text/plain; charset=UTF-8'
    
    msg.attach( MIMEText(mail['text'], _charset="utf-8") )
  
    for f in mail['files']:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open('./files/%s' % f['id'],"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % f['name'])
        msg.attach(part)
    
    try:
        smtp = getSMTPServer()
        content = msg.as_string()
        smtp.sendmail(mail['Reply-To'], mail['To'], content)
        smtp.close()
    except :
        pass

def sendNewEntryNotifications(con, lang, project, category, id, files) :
    
    cursor = con.cursor()
    
    # list of recipients
    query = """
    SELECT mail
    FROM Client
    WHERE
        subscription = True
        AND allowed = True
        AND project = %s
    """
    cursor.execute(query, (projectID(con, project), ))
    recipients = []
    for row in cursor.fetchall() :
        recipients.append(row[0])
    
    # content of the message
    query = """
    SELECT
        Entry.relativeID,
        Entry.name,
        Entry.description,
        Entry.status,
        Entry.severity,
        Client.login,
        Client.mail,
        extract( day FROM Entry.creationDate),
        extract( month FROM Entry.creationDate),
        extract( year FROM Entry.creationDate)
    FROM Entry
    INNER JOIN Client
    ON Entry.creator = Client.id
    WHERE Entry.id = %s"""
    cursor.execute(query, (id, ))
    row = cursor.fetchone()
    relativeID = int(row[0])
    title = row[1]
    description = unFormatText(row[2])
    status = int(row[3])
    severity = int(row[4])
    creator = row[5]
    creatorMail = row[6]
    day = row[7]
    month = row[8]
    year = row[9]
    
    # creating Message-ID for this entry, and therefore the entry-point for the thread
    messageID = make_msgid()
    query = """
    UPDATE Entry SET lastMessageID = %s WHERE id = %s"""
    cursor.execute(query, (messageID,id))
    con.commit()
    
    mytemplate = Template(filename='templates/'+lang+'/mails/newEntry.mail', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
    text = mytemplate.render(
        creator = creator,
        title = title,
        description = description,
        files = files,
        status = status,
        severity = severity
    )
    category = category[0].upper()+category[1:].lower()
    
    h = Header()
    h.append(category, 'utf-8')
    h.append(u'#'+str(relativeID)+u':', 'utf-8')
    h.append(title, 'utf-8')
    
    mail = {
        'From' : creator + ' <' + creatorMail + '>',
        'To' : recipients,
        'Subject' : h,
        'Reply-To' : project + '@projects.naphtaline.net',
        'Message-ID' : messageID,
        'In-Reply-To' : '',
        'text' : text,
        'files' : files,
    }
    
    send_mail(mail)

def sendEditEntryNotifications(con, lang, project, category, id, files) :
    
    cursor = con.cursor()
    
    # list of recipients
    query = """
    SELECT mail
    FROM Client
    WHERE
        subscription = True
        AND allowed = True
        AND project = %s
    """
    cursor.execute(query, (projectID(con, project), ))
    recipients = []
    for row in cursor.fetchall() :
        recipients.append(row[0])
    
    # content of the message
    query = """
    SELECT
        Entry.relativeID,
        Entry.name,
        Entry.description,
        Entry.status,
        Entry.severity,
        Client.login,
        Client.mail,
        extract( day FROM Entry.creationDate),
        extract( month FROM Entry.creationDate),
        extract( year FROM Entry.creationDate),
        Entry.lastMessageID
    FROM Entry
    INNER JOIN Client
    ON Entry.maintainer = Client.id
    WHERE Entry.id = %s"""
    cursor.execute(query, (id, ))
    
    row = cursor.fetchone()
    relativeID = int(row[0])
    title = row[1]
    description = unFormatText(row[2])
    status = int(row[3])
    severity = int(row[4])
    maintainer = row[5]
    maintainerMail = row[6]
    day = row[7]
    month = row[8]
    year = row[9]
    inReplyTo = row[10]
    
    # updating Message-ID
    messageID = make_msgid()
    query = """
    UPDATE Entry SET lastMessageID = %s WHERE id = %s"""
    cursor.execute(query, (messageID,id))
    con.commit()
    
    mytemplate = Template(filename='templates/'+lang+'/mails/editEntry.mail', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
    text = mytemplate.render(
        title = title,
        description = description,
        files = files,
        status = status,
        severity = severity,
        category = category,
        relativeID = relativeID,
        maintainer = maintainer
    )
    category = category[0].upper()+category[1:].lower()
    
    h = Header()
    h.append(u'Re:', 'utf-8')
    h.append(category, 'utf-8')
    h.append(u'#'+str(relativeID)+u':', 'utf-8')
    h.append(title, 'utf-8')
    
    mail = {
        'From' : maintainer + ' <' + maintainerMail + '>',
        'To' : recipients,
        'Subject' : h,
        'Reply-To' : project + '@projects.naphtaline.net',
        'Message-ID' : messageID,
        'In-Reply-To' : inReplyTo,
        'text' : text,
        'files' : files,
    }
    
    send_mail(mail)
  
def sendNewCommentNotifications(con, lang, project, category, id, content, files) :
    
    cursor = con.cursor()
    
    # creating the list of recipients
    query = """
    SELECT mail
    FROM Client
    WHERE
        subscription = True
        AND allowed = True
        AND project = %s
    """
    cursor.execute(query, (projectID(con, project), ))
    recipients = []
    for row in cursor.fetchall() :
        recipients.append(row[0])
    
    # creating the message
    query = """
    SELECT
        Client.login,
        Client.mail,
        Comment.entry,
        extract( day FROM Comment.creationDate),
        extract( month FROM Comment.creationDate),
        extract( year FROM Comment.creationDate),
        Entry.name,
        Entry.relativeID,
        Entry.lastMessageID
    FROM Comment
    INNER JOIN Entry
    ON Comment.entry = Entry.id
    INNER JOIN Client
    ON Comment.author = Client.id
    WHERE Comment.id = %s"""
    cursor.execute(query, (id, ))
    row = cursor.fetchone()
    author = row[0]
    authorMail = row[1]
    idEntry = int(row[2])
    day = int(row[3])
    month = int(row[4])
    year = int(row[5])
    title = row[6]
    relativeID = int(row[7])
    inReplyTo = row[8]
    
    # updating Message-ID
    messageID = make_msgid()
    query = """
    UPDATE Entry SET lastMessageID = %s WHERE id = %s"""
    cursor.execute(query, (messageID,id))
    con.commit()
    
    mytemplate = Template(filename='templates/'+lang+'/mails/newcomment.mail', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
    text = mytemplate.render(
        author = author,
        comment = content,
        files = files
    )
    category = category[0].upper()+category[1:].lower()
    
    h = Header()
    h.append(u'Re:', 'utf-8')
    h.append(category, 'utf-8')
    h.append(u'#'+str(relativeID)+u':', 'utf-8')
    h.append(title, 'utf-8')
    
    mail = {
        'From' : author + ' <' + authorMail + '>',
        'To' : recipients,
        'Subject' : h,
        'Reply-To' : project + '@projects.naphtaline.net',
        'Message-ID' : messageID,
        'In-Reply-To' : inReplyTo,
        'text' : text,
        'files' : files,
    }
    
    send_mail(mail)

def sendDeleteNotifications(con, lang, project, category, relativeID, userID):
    """ Send a notification in case of delete """
    cursor = con.cursor()
    # creating the list of recipients
    query = """
    SELECT mail
    FROM Client
    WHERE
        subscription = True
        AND allowed = True
        AND project = %s"""
    cursor.execute(query, (projectID(con, project), ))
    recipients = []
    for row in cursor.fetchall() :
        recipients.append(row[0])
    # get message content
    query = """
    SELECT name, lastMessageID
    FROM Entry
    WHERE relativeID = %s AND category = %s"""
    categoryCode = {'bug' : 1, 'feature' : 2}
    cursor.execute(query, (relativeID, categoryCode[category]))
    row = cursor.fetchone()
    title = row[0]
    inReplyTo = row[1]
    # user caracteristics (the one who deleted the entry)
    query = """SELECT login, mail FROM Client WHERE id=%s"""
    cursor.execute(query, (userID, ))
    row = cursor.fetchone()
    author = row[0]
    authorMail = row[1]
    # load template
    mytemplate = Template(filename='templates/'+lang+'/mails/delete.mail', output_encoding='utf-8', default_filters=['decode.utf8'], input_encoding='utf-8')
    text = mytemplate.render(creator = author)
    category = category[0].upper()+category[1:].lower()
        
    h = Header()
    h.append(u'Re:', 'utf-8')
    h.append(category, 'utf-8')
    h.append(u'#'+str(relativeID)+u':', 'utf-8')
    h.append(title, 'utf-8')
    
    # make messageID
    # no need to save it to the database : the entry will be deleted
    messageID = make_msgid()

    mail = {'From' : author + ' <' + authorMail + '>',
            'To' : recipients,
            'Subject' : h,
            'Reply-To' : project + '@projects.naphtaline.net',
            'Message-ID' : messageID,
            'In-Reply-To' : inReplyTo,
            'text' : text,
            'files' : []}
    
    send_mail(mail)
