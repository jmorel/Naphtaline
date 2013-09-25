# Naphtaline

*Naphtaline* is an issue tracking platform with a strong focus on usability for non tech users.

It was built in 2008, before the industry as a whole realized that productivity apps (not yet called apps at the time) could benefit from well thought interfaces and could also be used by everyday people. At the time the main issue tracking tools were [Bugzilla](http://www.bugzilla.org/) and [trac](http://trac.edgewall.org/): powerful but also tedious as hell. And clearly out of reach for people not interested in code development. With *Naphtaline*, I wanted to bring the power of bug tracking and simple project management to everyday people.

In order to streamline the user experience, *Naphtaline* got back to the basics: two types of tickets, one for issues and the other for feature requests. The interface used a then groundbreaking 3 panel layout to display in one page everything the user might want to know about a specific issue. The information hierarchy is displayed at all times and visual cues make sure that a glance is enough to know exactly what the page is all about while heavy use of AJAX allowed for a reactive experience.

This project is no longer actively developed, but there are now excellent alternatives out there. Check [Trello](http://trello.com) out!

*Naphtaline* was built from scratch with [CherryPy](http://www.cherrypy.org), a minimalist Python web framework.

## DB structure

### Codes meaning

status:

    code    bug                             feature
    -----------------------------------------------------------
    1       corrected                       implemented
    2       being taken care of             being taken care of
    3       unknown                         unknown
    4       (undefined - feature only)      rejected

severity/urgency (urgency is for features)

    code    bug                             feature
    -----------------------------------------------------------
    1       light                           weak
    2       serious                         strong
    3       critical                        critical
    
user level:

    code    level
    --------------
    1       normal
    2       admin
