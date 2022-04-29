import sqlite3


connection = sqlite3.connect("info.db")
cursor = connection.cursor()

""" cursor.execute("CREATE TABLE info (title TEXT, startDate TEXT, reminder TEXT, htmlLink TEXT, id TEXT)") """

"""
addEvent adds an event to the database.
Parameters:
title (title of the event): str
startDate (when the event starts): str
reminderTime (when to send a notification; startDate + reminder in minutes): str
htmlLink (link to the event): str
id (id of the event): str

No return value.
"""
def addEvent(title, startDate, reminderTime, htmlLink, id):
    cursor.execute("INSERT INTO info VALUES(?,?,?,?,?);", (title, startDate, reminderTime, htmlLink,id)) 
    connection.commit()
    print("ID: "+ id + " SAVED TO DATABASE!")

"""
getEvents returns the entire list of events in the database
No parameters

Returns a list of events from database
"""
def getEvents():
    return cursor.execute("SELECT title, startDate, reminder, htmlLink, id FROM info").fetchall()

"""
deleteEvent deletes an event in the database
Parameters:
id (id of the event): str

Returns:
No return value
"""
def deleteEvent(id):
    print("DELETING "+ id)
    cursor.execute("DELETE FROM info WHERE id = ?", (id,))
    connection.commit()

"""
isAdded checks if an event has been added to the database
Parameters:
id (id of the event): str

Returns:
False if the event has not been added 
True if the event has been added
"""
def isAdded(id):
    rows = cursor.execute(
    "SELECT title, startDate, reminder, htmlLink, id FROM info WHERE id = ?",
    (id,),
    ).fetchone()

    if rows is None:
        return False
    else:
        print("ID: "+ id+ " ALREADY ADDED!!")
        return True
