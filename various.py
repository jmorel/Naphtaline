from random import Random

def url(*args) :
    """ Generating url for the application.
    It just joins all strings passed as args into a big one where they are separated by '/'
    """
    url = ''
    for elt in args :
        url += '/'
        url += str(elt)
    return url

def purgeDuplicates(list):
    """ Return a copy of list purged from all duplicates """
    res = []
    for elt in list:
        if elt not in res:
            res.append(elt)
    return res

def formatText(text) :
    """ Processing "text" to ensure that it will be html compliant with the same indentation.
    """
    # protection against javascript and html
    text = text.replace('<', '&lt;')
    text = text.replace('<w', '&gt;')
    
    # processing content so that basic layout is respected
    res = ""
    for line in text.split("\n") :
        line = line.rstrip()
        i = 0
        if len(line) >= 1 :
            while line[i] == ' ' :
                i += 1
            line = '&nbsp;'*i+line[i:]+'<br/>'
            res += line
        else :
            res += '<br/>'
    text = res
    
    previous = text
    actual = previous.replace("  ","&nbsp;&nbsp;")
    while previous is not actual :
        previous = actual
        actual = previous.replace("  ","&nbsp;&nbsp;")
        text = actual
    text.replace("<br /> ", "<br/>&nbsp;") 
    return text

def unFormatText(text) :
    """ Processing "text" so that it will be displayed in a textarea without the markups.
    """
    text = text.replace("&nbsp;", " ")
    #text = text.replace("<br /> ", "\n")
    text = text.replace("<br/>", "\n")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    return text

def randomPwd() :
    """ Returns an 8 chars long password randomly generated
    """
    
    rng = Random()
    
    righthand = '23456qwertasdfgzxcvbQWERTASDFGZXCVB'
    lefthand = '789yuiophjknmYUIPHJKLNM'
    allchars = righthand + lefthand
    
    pwd = ''
    passwordLength = 8
    
    for i in range(passwordLength):
        pwd += rng.choice(allchars)
    
    return pwd

def projectLang(con, project) :
    """ Get the lang of the project
    """
    cursor = con.cursor()
    query = """
    SELECT lang FROM Project WHERE webname = %s"""
    cursor.execute(query, (project, ))
    rows = cursor.fetchall()
    lang = 'en'
    for row in rows :
        lang = row[0]
    return lang

def projectID(con, project):
    """ Get the ID of the project """
    
    cursor = con.cursor()
    query = """
    SELECT id FROM Project WHERE webname = %s"""
    cursor.execute(query, (project, ))
    rows = cursor.fetchall()
    id = 0
    for row in rows :
        id = int(row[0])
    return id
    

def formatFileName(filename) :
    """ Return the substring present after the last backslash
    It prevents files from having names such as D:\hi\picture.jpg
    """
    return filename.split('\\')[-1]