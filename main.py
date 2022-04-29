"""
TODO:
✔️ Creating Events
✔️ Create Events using step-by-step commands
✔️ Listing Events
✔️ Modify Events using step-by-step commands
✔️ Deleting Events using step-by-step commands
✔️ Getting notifications from events (need further verification on bug fixes but so far it seems to work lol)
⏰ Add garbage collection
✔️ Runtime command (for the fun of it lol)
"""

from lib2to3.pytree import convert
from tokenize import String
import discord
from discord.ext import tasks, commands
import calendarAPI, datetime, asyncio, time, calendar, event, pytz
from datetime import timedelta
import dataBase

token = open("token.txt", "r").readline()

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = ".", intents=intents)

botStarted = datetime.datetime.utcnow()
allowed_mentions = discord.AllowedMentions(everyone = True)

#startUp
startUp = False


class AllNum(Exception):
    """Exception raised for string not containing all numbers"""
    def __init__(self, message="Dates must be all numbers"):
        self.message = message
        super().__init__(self.message)

class DateLength(Exception):
    """Exception raised for date string not being 12 characters long"""
    def __init__(self, message="Dates must be in this format: yyyymmddhhmm. If it is a full day event, set both starting and ending hhmm to 0."):
        self.message = message
        super().__init__(self.message)


@client.event
async def on_ready():
    #initalizes calendar API
    global startUp
    try:
        calendarAPI.main()
    except:
        print("Error with calendarAPI.py. Stopping bot...")
        exit()
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="your calendar!"))
    print(f"{client.user} has connected to Discord!")
    startUp = True


"""
.newevent takes arguments title (String), desc (String), startTime (String: yyyymmddhhmm), endTime(String: yyyymmddhhmm), 
location (String default=""), reminder (int: default=0), frequency (String: weekly, daily, default=""),
recurrenceInterval (int: default=0), , byday (String: MO,TU,WE,TH,FR,SA,SU default=""),
recurrenceCount (int: default=0), recurrenceEnd (String: yyyymmddhhmm default="")

title sets the title of the event to given string.
desc sets the description of the event to the given string; 
startTime sets the start time (date and time) of event (time is in EST). Format: yyyymmddhhmm
endTime sets the end time (date and time) of event (time is in EST). Format: yyyymmddhhmm
location sets the location of the event to the given string. if no string is provided, no location would be set.
reminder sets when to remind the event is about to start (in minutes). Default is 30 minutes.
frequency sets how often the event should repeat. WEEKLY repeats the event every week. DAILY repeats the event every day. Default is none (no repetition).
recurrenceInterval sets how much skip between events. Default is 0.
byday sets which day of the week to repeat on. If multiple, separate by comma. Default is no specification (""). Options: MO,TU,WE,TH,FR,SA,SU
recurrenceCount sets how much the event should repeat. If recurrenceEnd has input, recurrenceCount will be ignored. Default is 0.
recurrenceEnd sets the last day the event will stop repeating. Default is never (""). Format: yyyymmdd
"""
@client.command(name = "new", help = "Creates a new event using the given parameters.")
async def newEvent(message: discord.Member, title: str, desc: str, startTime: str, 
endTime: str, location: str="", reminder: int=30, frequency: str="", 
recurrenceInterval: str=0, byday: str="", recurrenceCount: str=0,
recurrenceEnd: str = "00000000"):
    try:
        if (not startTime.isnumeric()):
            raise AllNum
        if (len(startTime) != 12 or len(endTime) != 12 or len(recurrenceEnd) != 8):
            raise DateLength
        else:
            frequency = frequency.upper()
            byday = byday.upper()
            #check if we are in DST (i hate dst ahh)
            utc = "05"
            if (time.localtime().tm_isdst):
                utc = "04"
            startTime = startTime[0:4 : ] + "-" + startTime[4: 6 : ] + "-" + startTime[6: 8:] + "T" + startTime[8:10:]+":"+startTime[10: 12:]+":00-"+utc+":00"
            endTime = endTime[0:4 : ] + "-" + endTime[4: 6 : ] + "-" + endTime[6: 8:] + "T" + endTime[8:10:]+":"+endTime[10: 12:]+":00-"+utc+":00"
            #no repetition
            if frequency == "":
                newEvent = event.noFreq(title, desc, startTime, endTime, location, reminder)
            else:
                #has repetition end date
                if recurrenceEnd != "00000000":
                    #if there are specified days of the week
                    if byday != "":
                        newEvent = event.hasFreqEndDate(title, desc, startTime, endTime, location, reminder, frequency, recurrenceEnd, recurrenceInterval, byday)
                    else:
                        newEvent = event.hasFreqEndDateNoByDay(title, desc, startTime, endTime, location, reminder, frequency, recurrenceEnd, recurrenceInterval)
                #if repetition end date not inputted
                else:
                    #if count given
                    if recurrenceCount != 0:
                        #if there are specified days of the week
                        if byday != "":
                            newEvent = event.onlyCount(title, desc, startTime, endTime, location, reminder, frequency, recurrenceCount, recurrenceInterval, byday)
                        else:
                            newEvent = event.onlyCountnoByDay(title, desc, startTime, endTime, location, reminder, frequency, recurrenceCount, recurrenceInterval)
                    #if count is not given
                    else:
                        #if there are specified days of the week
                        if byday != "":
                            newEvent = event.repeatForever(title, desc, startTime, endTime, location, reminder, frequency, recurrenceInterval, byday)
                        else:
                            newEvent = event.repeatForevernoByDay(title, desc, startTime, endTime, location, reminder, frequency, recurrenceInterval)
            link = calendarAPI.createEvent(newEvent)
            embed = discord.Embed(
                title = title, 
                url = link,
                description = "Event Created Successfully!",
                timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                color = discord.Color.blue())
            embed.set_author(name = message.author.display_name, icon_url = message.author.avatar_url)
            embed.add_field(name = "Description", value = desc, inline=False)
            embed.add_field(name = "Location", value = location, inline=False)
            embed.add_field(name = "Start Date", value = startTime, inline=False)
            embed.add_field(name = "End Date", value = endTime, inline=False)
            if frequency!="":
                embed.add_field(name = "Recurring", value = frequency, inline=False)
                if recurrenceEnd !="00000000":
                    embed.add_field(name = "Until", value = recurrenceEnd, inline=False)
                elif recurrenceCount != 0:
                    embed.add_field(name = "Repeating Amount", value = recurrenceCount, inline=False)
                else:
                    embed.add_field(name = "Recurring", value = "Forever", inline=False)
                embed.add_field(name = "Recurrence Interval", value = recurrenceInterval, inline=False)
                if byday != "":
                    embed.add_field(name = "Every", value = byday, inline=False)
            await message.channel.send(embed=embed)
    except AllNum:
        print("Incorrect Date/Time Input")
        embed = discord.Embed(
            title = "Error", 
            description = "Event Has Not Been Created.",
            color = discord.Color.red())
        embed.add_field(name = "AllNum Exception", value = "Please ensure all date inputs are numerical.", inline=False)
        await message.channel.send(embed=embed)
    except DateLength:
        print("Incorrect Date Length Input")
        embed = discord.Embed(
            title = "Error", 
            description = "Event Has Not Been Created.",
            color = discord.Color.red())
        embed.add_field(name = "DateLength Exception", value = "Dates must be in this format: yyyymmddhhmm. If it is a full day event, set both starting and ending hhmm to 0.", inline=False)
        await message.channel.send(embed=embed)
    except:
        embed = discord.Embed(
            title = "Error", 
            description = "Event Has Not Been Created.",
            color = discord.Color.red())
        embed.add_field(name = "Uncaught Exception", value = "Please ensure your inputs are correct and try again.", inline=False)
        await message.channel.send(embed=embed)

@client.command(name = "newevent", help="Creates a new event via a step-by-step guide.")
async def create(message: discord.Member):
    """
    newCheck() will check user input and the bot will only respond if the conditions are met 
    """
    now = datetime.datetime.now()
    def checkDay(year:int, month: int, day: int):
        lastDayOfMonths = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if calendar.isleap(year):
            lastDayOfMonths[2] = 29
        return (day <= lastDayOfMonths[month])
    def checkText(msg):
        return msg.author == message.author and msg.channel == message.channel
    def checkDate(msg):
        #check if date is valid
        if (msg.author == message.author and msg.channel == message.channel):
            date = msg.content
            if date.isnumeric():
                if len(date) == 8 and int(date [0:4:]) >= now.year and int(date[4:6:])>=now.month and int(date[4:6:])<13:
                    if checkDay(int(date[0:4]),int(date[4:6:]), int(date[6:8:])):
                        return True
        return False
    def checkEndDate(msg):
        #check if date is valid
        if (msg.author == message.author and msg.channel == message.channel):
            if (checkDate(msg)):
                #check if end date is the same date as the start date or happening after the start date
                if int(startTime) <= int(msg.content):
                    return True
        return False
    def checkTime(msg):
        #check if time is valid
        if (msg.author == message.author and msg.channel == message.channel):
            time = msg.content
            #24 hour
            if (len(time) == 4 and time.isnumeric()):
                #check if time given is between 0000 (inclusive) and 2400 (exclusive) and the minutes are between 00 and 59.
                if (int(time)>=0 and int(time)<2400 and int(time[0:2:])<=59):
                    return True
            #12 hour
            elif (len(time) == 8): #03:59 am
                if(time[0:2:].isnumeric() and time[3:4:].isnumeric()):
                    #check if hours are between 0 and 12 (inclusive) and minutes are between 0 and 59 (inclusive)
                    if (int(time[0:2:]) >=0 and int(time[0:2:]) <=12 and int(time[3:5:]) >=0 and int(time[3:5:])<= 59):
                        #check if msg[6:8:] is am or pm
                        if (time[6:8:].lower() == "am" or time[6:8:].lower() =="pm"):
                            return True
        return False
    def convertToMilTime(time):
        if len(time) == 8:
            if (time[6:8:].lower() == "pm"):
                time = time.replace(" pm", "")
                if int(time[0:2:]) <12:
                    time = str(int(time[0:2:])+12)+time[2:]
                time = time.replace(":", "")
            else:
                time = time.replace(" am", "")
                time = time.replace(":", "") 
        return time
    def checkNum(msg):
        if (checkText(msg) and msg.content.isnumeric()):
            return int(msg.content) <= 180
    def checkEndTime(msg):
        if (msg.author == message.author and msg.channel == message.channel):
            #check if time is valid
            if (checkTime(msg)):
                #if on same day
                if (startDate == endDate):
                    endTime = msg.content
                    #convert endTime to 24 hour
                    endTime = convertToMilTime(endTime)
                    #check if the start time is BEFORE end time
                    if (int(startTime) < int(endTime)):
                        return True
                else:
                    return True
        return False
    def checkFreq(msg):
        return (checkText(msg) and msg.content.upper() == "DAILY" or 
        msg.content.upper() == "WEEKLY" or msg.content.upper() == "NONE")
    def checkRecEnd(msg):
        if checkText(msg):
            #if entered date
            if len(msg.content) == 8:
                if (checkDate(msg)):
                    return int(msg.content) > int(endDate)
            #if entered count (arbitrary limit of 100 inclusive)
            else:
                return (int(msg.content)<=100)
        return False
    def checkInterval(msg):
        if checkText(msg) and checkNum(msg):
            return int(msg.content) <= 10
        return False
    def checkByDay(msg):
        byDayCheck = ["MO", "TU", "WE", "TH", "FR", "SA", "SU", "NO"]
        if checkText(msg) and len(msg.content) == 2:
            return msg.content.upper() in byDayCheck
        else:
            return False

    try:
        #title
        embed = discord.Embed(
            title = "Creating an Event", 
            timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
            color = discord.Color.orange())
        embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
        embed.add_field(name= "Title", value = "Please enter the name of the event", inline=False)
        await message.channel.send(embed=embed)
        title = await client.wait_for("message", check=checkText, timeout = 60)
        title = title.content

        #Description
        embed = discord.Embed(
            title = "Creating an Event", 
            timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
            color = discord.Color.orange())
        embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
        embed.add_field(name= "Description", value = "Please enter the description of the event", inline=False)
        await message.channel.send(embed=embed)
        desc = await client.wait_for("message", check=checkText, timeout = 60)
        desc = desc.content

        #Start Date
        embed = discord.Embed(
            title = "Creating an Event", 
            timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
            color = discord.Color.orange())
        embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
        embed.add_field(name= "Start Date", value = "Please enter the start date of the event", inline=False)
        embed.add_field(name= "Format", value = "Input date as yyyymmdd", inline=False)
        await message.channel.send(embed=embed)
        startDate = await client.wait_for("message", check=checkDate, timeout = 60)
        startDate = startDate.content
     
        #Start Time
        embed = discord.Embed(
            title = "Creating an Event", 
            timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
            color = discord.Color.orange())
        embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
        embed.add_field(name= "Start Time", value = "Please enter the start time of the event", inline=False)
        embed.add_field(name= "Format", value = "Input time as hhmm (24 hour) or hh:mm <am/pm>", inline=False)
        await message.channel.send(embed=embed)
        startTime = await client.wait_for("message", check=checkTime, timeout = 60)
        startTime = startTime.content

        #format time to be hhmm (24 hour) if it isn't already
        startTime = convertToMilTime(startTime)

        #End Date
        embed = discord.Embed(
            title = "Creating an Event", 
            timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
            color = discord.Color.orange())
        embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
        embed.add_field(name= "End Date", value = "Please enter the end date of the event", inline=False)
        embed.add_field(name= "Format", value = "Input date as yyyymmdd", inline=False)
        await message.channel.send(embed=embed)
        endDate = await client.wait_for("message", check=checkEndDate, timeout = 60)
        endDate = endDate.content


        #End Time
        embed = discord.Embed(
            title = "Creating an Event", 
            timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
            color = discord.Color.orange())
        embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
        embed.add_field(name= "End Time", value = "Please enter the end time of the event", inline=False)
        embed.add_field(name= "Format", value = "Input time as hhmm (24 hour) or hh:mm <am/pm>", inline=False)
        await message.channel.send(embed=embed)
        endTime = await client.wait_for("message", check=checkEndTime, timeout = 60)
        endTime = endTime.content

        #format time to be hhmm (24 hour) if it isn't already
        endTime = convertToMilTime(endTime) 


        #check if we are in DST (i hate dst ahh)
        utc = "05"
        if (time.localtime().tm_isdst):
            utc = "04"
        startTime = startDate[0:4 : ] + "-" + startDate[4: 6 : ] + "-" + startDate[6: 8:] + "T" + startTime[0:2:]+":"+startTime[2:4:]+":00-"+utc+":00"
        endTime = endDate[0:4 : ] + "-" + endDate[4: 6 : ] + "-" + endDate[6: 8:] + "T" + endTime[0:2:]+":"+endTime[2:4:]+":00-"+utc+":00"


        #Location
        embed = discord.Embed(
            title = "Creating an Event", 
            timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
            color = discord.Color.orange())
        embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
        embed.add_field(name= "Location", value = "Please enter the location of the event", inline=False)
        await message.channel.send(embed=embed)
        location = await client.wait_for("message", check=checkText, timeout = 60)
        location = location.content

        #Reminder
        embed = discord.Embed(
            title = "Creating an Event", 
            timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
            color = discord.Color.orange())
        embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
        embed.add_field(name= "Reminder", value = "Please enter when you want a reminder before the event starts (in minutes)? Max 180 minutes.", inline=False)
        await message.channel.send(embed=embed)
        reminder = await client.wait_for("message", check=checkNum, timeout = 60)
        reminder = reminder.content

        freqBool = True
        #Frequency
        embed = discord.Embed(
            title = "Creating an Event", 
            timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
            color = discord.Color.orange())
        embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
        embed.add_field(name= "Frequency", value = "Please enter DAILY/WEEKLY/NONE if you wish to have the event repeat daily, repeat weekly, or to not repeat.", inline=False)
        await message.channel.send(embed=embed)
        frequency = await client.wait_for("message", check=checkFreq, timeout = 60)
        frequency = frequency.content.upper()

        if (frequency == "NONE"):
            freqBool = False
        if (freqBool):
            unlimited = False
            recurrenceCount = -1
            recurrenceEnd = -1
            #recurrenceEnd or Count
            embed = discord.Embed(
                title = "Creating an Event", 
                timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                color = discord.Color.orange())
            embed.add_field(name= "Recurrence End", value = "Please enter a date (yyyymmdd) you want the repetition to end on or enter a number of times (<=100) you wish the event to repeat.", inline=False)
            embed.add_field(name= "Infinite Repeat", value = "Please enter 0 to have the event infinitely repeat.", inline=False)
            embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
            recEnd = await client.wait_for("message", check=checkRecEnd, timeout = 60)
            recEnd = recEnd.content
            if (int(recEnd) == 0):
                unlimited = True
            elif (int(recEnd) <=100):
                recurrenceCount = recEnd  
            else:
                recurrenceEnd = recEnd
            
            #recurrenceInterval
            embed = discord.Embed(
            title = "Creating an Event", 
            timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
            color = discord.Color.orange())
            embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
            embed.add_field(name= "Recurrence Interval", value = "Please enter how often you want the event to repeat (Max 10).", inline=False)
            await message.channel.send(embed=embed)
            recurrenceInterval = await client.wait_for("message", check=checkInterval, timeout = 60)
            recurrenceInterval = recurrenceInterval.content

            #recurrence By Day
            embed = discord.Embed(
            title = "Creating an Event", 
            timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
            color = discord.Color.orange())
            embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
            embed.add_field(name= "Recurrence By Day", value = "Please enter the day of the week you want the event to repeat (MO,TU,WE,TH,FR,SA, or SU).", inline=False)
            embed.add_field(name= "Skip Recurrence By Day", value = "Please enter \"NO\" to skip.", inline=False)
            await message.channel.send(embed=embed)
            byday = await client.wait_for("message", check=checkByDay, timeout = 60)
            byday = byday.content
        
            #infinite repeat
            if (unlimited):
                #No ByDay
                if (byday.upper() == "NO"):
                    newEvent = event.repeatForevernoByDay(title, desc, startTime, endTime, location, reminder, frequency, recurrenceInterval)
                else:
                    newEvent = event.repeatForever(title, desc, startTime, endTime, location, reminder, frequency, recurrenceInterval, byday) 
            #finite repeat
            else:
                #recurrence end date set
                if recurrenceCount == -1:
                    #no byday
                    if (byday.upper() != "NO"):
                        newEvent = event.hasFreqEndDate(title, desc, startTime, endTime, location, reminder, frequency, recurrenceEnd, recurrenceInterval, byday)
                    else:
                        newEvent = event.hasFreqEndDateNoByDay(title, desc, startTime, endTime, location, reminder, frequency, recurrenceEnd, recurrenceInterval)   
                #recurrence count set
                else:
                    #no byday
                    if (byday.upper() != "NO"):
                        newEvent = event.onlyCount(title, desc, startTime, endTime, location, reminder, frequency, recurrenceCount, recurrenceInterval, byday)
                    else:
                        newEvent = event.onlyCountnoByDay(title, desc, startTime, endTime, location, reminder, frequency, recurrenceCount, recurrenceInterval)
        #one time event
        else:
            newEvent = event.noFreq(title, desc, startTime, endTime, location, reminder)

        link = calendarAPI.createEvent(newEvent)
        embed = discord.Embed(
            title = title, 
            url = link,
            description = "Event Created Successfully!",
            timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
            color = discord.Color.blue())
        embed.set_author(name = message.author.display_name, icon_url = message.author.avatar_url)
        embed.add_field(name = "Description", value = desc, inline=False)
        embed.add_field(name = "Location", value = location, inline=False)
        embed.add_field(name = "Start Date", value = startTime, inline=False)
        embed.add_field(name = "End Date", value = endTime, inline=False)
        if freqBool:
            embed.add_field(name = "Recurring", value = frequency, inline=False)
            if recurrenceEnd != -1:
                embed.add_field(name = "Until", value = recurrenceEnd, inline=False)
            elif recurrenceCount != -1:
                embed.add_field(name = "Repeating Amount", value = recurrenceCount, inline=False)
            else:
                embed.add_field(name = "Recurring", value = "Forever", inline=False)
            embed.add_field(name = "Recurrence Interval", value = recurrenceInterval, inline=False)
            if byday.upper() != "NO":
                embed.add_field(name = "Every", value = byday, inline=False)
        
        embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
        await message.channel.send(embed=embed)

    except asyncio.TimeoutError:
            print("Timed out; received no valid user inputs")
            embed = discord.Embed(
                title = "Error", 
                description = "Event Has Not Been Created.",
                color = discord.Color.red())
            embed.add_field(name = "Timed Out", value = "Process cancelled. Please invoke .newevent if you wish to create an event.", inline=False)
            await message.channel.send(embed=embed)
    
    except:
        embed = discord.Embed(
            title = "Error", 
            description = "Event Has Not Been Created.",
            color = discord.Color.red())
        embed.add_field(name = "Uncaught Exception", value = "Please ensure your inputs are correct and try again.", inline=False)
        await message.channel.send(embed=embed)

@client.command(name = "listevents", help="Lists next 5 upcoming events.")
async def create(message: discord.Member):
    try:
        listEvents = calendarAPI.listEvents()
        #print (listEvents)

        if listEvents is None:
            embed = discord.Embed(
                title = "There are no upcoming events",
                description = "Do .newevent to add events to the calendar!", 
                color = discord.Color.red(),
                timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern"))
                )
            
        else:
            embed = discord.Embed(
                title = "Next 6 upcoming events", 
                color = discord.Color.green(),
                timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern"))
                )
            for currEvent in listEvents:
                embed.add_field(name=currEvent['summary'], value="["+currEvent['description']+"]("+currEvent['htmlLink']+")\n"+ currEvent['start']['dateTime'][0:10]+ " "+currEvent['start']['dateTime'][11:16]+" to "+currEvent['end']['dateTime'][0:10]+ " "+currEvent['end']['dateTime'][11:16]+"\nLocation: "+currEvent['location'], inline=True)
        embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
        await message.channel.send(embed=embed)
    
    except:
        embed = discord.Embed(
            title = "Error", 
            description = "An Error Has Occured. Please try again.",
            color = discord.Color.red())
        await message.channel.send(embed=embed)

@client.command(name="runtime", help="See how long the bot has been up for!")
async def runTime(message):
    now = datetime.datetime.utcnow()
    elapsed = now - botStarted
    seconds = elapsed.seconds
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    print("Running for {}d {}h {}m {}s".format(elapsed.days, hours, minutes, seconds))
    await message.channel.send("Running for {}d {}h {}m {}s".format(elapsed.days, hours, minutes, seconds))

@client.command(name="modifyevent", help="Modifies an existing event.")
async def modifyEvent(message):

    selection = "NEXT"
    listEvents = []
    now = datetime.datetime.now()

    def getDate(date):
        date = datetime.datetime.fromisoformat(date)
        month = date.month
        day = date.day
        if len(str(month)) == 1:
            month = "0"+str(month)
        if len(str(day)) == 1:
            day = "0"+str(day)
        return str(date.year)+"-"+str(date.month)+"-"+str(date.day)

    def getTime(time):
        time = datetime.datetime.fromisoformat(time)
        hour = time.hour
        min = time.minute

        if len(str(hour)) == 1:
            hour = "0"+str(hour)
        if len(str(min)) == 1:
            min = "0"+str(min)

        return str(hour)+":"+str(min)

    def checkFromAuthor(msg):
        return msg.author == message.author and msg.channel == message.channel
    def selectionCheck(msg):
        selectChoices = ['1', '2', '3', '4', '5', '6', 'NEXT', 'CANCEL']
        if checkFromAuthor(msg):
            return msg.content.upper() in selectChoices
        return False    

    def select(timeMin):
        #get next 6 events from given time (utc)
        nextEvents = calendarAPI.listEventsFromDate(timeMin)
        return nextEvents

    def checkDay(year:int, month: int, day: int):
        lastDayOfMonths = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if calendar.isleap(year):
            lastDayOfMonths[2] = 29
        return (day <= lastDayOfMonths[month])
    def checkDate(msg):
        #check if date is valid
        if (msg.author == message.author and msg.channel == message.channel):
            if msg.content.upper() == "SKIP":
                return True
            date = msg.content
            if date.isnumeric():
                if len(date) == 8 and int(date [0:4:]) >= now.year and int(date[4:6:])>=now.month and int(date[4:6:])<13:
                    if checkDay(int(date[0:4]),int(date[4:6:]), int(date[6:8:])):
                        return True
        return False
    def checkEndDate(msg):
        if (msg.author == message.author and msg.channel == message.channel):
            if msg.content.upper() == "SKIP":
                return True
            #get starttime from event
            startTime = selectedEvent['start']['dateTime'][0:10].replace("-","")
            #check if date is valid
            if (checkDate(msg)):
                #check if end date is the same date as the start date or happening after the start date
                if int(startTime) <= int(msg.content):
                    return True
        return False

    def checkTime(msg):
        #check if time is valid
        if (msg.author == message.author and msg.channel == message.channel):
            time = msg.content
            if msg.content.upper() == "SKIP":
                return True
            #24 hour
            if (len(time) == 4 and time.isnumeric()):
                #check if time given is between 0000 (inclusive) and 2400 (exclusive) and the minutes are between 00 and 59.
                if (int(time)>=0 and int(time)<2400 and int(time[0:2:])<=59):
                    return True
            #12 hour
            elif (len(time) == 8): #03:59 am
                if(time[0:2:].isnumeric() and time[3:4:].isnumeric()):
                    #check if hours are between 0 and 12 (inclusive) and minutes are between 0 and 59 (inclusive)
                    if (int(time[0:2:]) >=0 and int(time[0:2:]) <=12 and int(time[3:5:]) >=0 and int(time[3:5:])<= 59):
                        #check if msg[6:8:] is am or pm
                        if (time[6:8:].lower() == "am" or time[6:8:].lower() =="pm"):
                            return True
        return False

    def convertToMilTime(time):
        if len(time) == 8:
            if (time[6:8:].lower() == "pm"):
                time = time.replace(" pm", "")
                time = str(int(time[0:2:])+12)+time[2:]
            else:
                time = time.replace(" am", "")
            return time
        else:
            return time[0:2]+":"+time[2:4]

    def checkEndTime(msg):
        if (msg.author == message.author and msg.channel == message.channel):
            #get startTime
            startTime = selectedEvent['start']['dateTime'][11:16].replace(":", "")
            #check if time is valid
            if (checkTime(msg)):
                #if on same day
                if (startDate == endDate):
                    endTime = msg.content
                    #convert endTime to 24 hour
                    endTime = convertToMilTime(endTime)
                    #check if the start time is BEFORE end time
                    if (int(startTime) < int(endTime)):
                        return True
                else:
                    return True
            elif msg.content.upper() == "SKIP":
                return True
        return False

    try:
        listEvents = calendarAPI.listEvents()
        first = True
        while selection.upper() == "NEXT":
            if listEvents is None:
                embed = discord.Embed(
                    title = "There are no upcoming events to modify!",
                    description = "Do .newevent to add events to the calendar!", 
                    color = discord.Color.red(),
                    timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern"))
                    )
                await message.channel.send(embed=embed)
                break
            if (first):
                #first page
                embed = discord.Embed(
                    title = "Modifying Events",
                    description = "Listing the 6 Upcoming Events",
                    timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                    color = discord.Color.orange()
                )
                embed.add_field(name="Select", value="Enter 1-6 to select the event you wish to modify, enter \"NEXT\" to get the next upcoming 6 events, or enter \"CANCEL\" to exit.", inline=False)
                for currEvent in listEvents:
                    embed.add_field(name=currEvent['summary'], value="["+currEvent['description']+"]("+currEvent['htmlLink']+")\n"+ currEvent['start']['dateTime'][0:10]+ " "+currEvent['start']['dateTime'][11:16]+" to "+currEvent['end']['dateTime'][0:10]+ " "+currEvent['end']['dateTime'][11:16]+"\nLocation: "+currEvent['location'], inline=True)
                embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                selection = await client.wait_for("message", check = selectionCheck, timeout=60)
                selection = selection.content
                first = False
            #if user wants to see more events
            else:
                #next page
                #convert endTime of the last event to utc for timeMin. using timeMin to search for the next events using google API
                listEvents = select(datetime.datetime.fromisoformat(listEvents[5]['end']['dateTime']).astimezone(pytz.utc).isoformat())
                embed = discord.Embed(
                    title = "Modifying Events",
                    description = "Listing the next 6 Upcoming Events",
                    timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                    color = discord.Color.orange()
                    )
                embed.add_field(name="Select", value="Enter 1-6 to select the event you wish to modify, enter \"NEXT\" to get the next upcoming 6 events, or enter \"CANCEL\" to exit.", inline=False)
                for currEvent in listEvents:
                    embed.add_field(name=currEvent['summary'], value="["+currEvent['description']+"]("+currEvent['htmlLink']+")\n"+ currEvent['start']['dateTime'][0:10]+ " "+currEvent['start']['dateTime'][11:16]+" to "+currEvent['end']['dateTime'][0:10]+ " "+currEvent['end']['dateTime'][11:16]+"\nLocation: "+currEvent['location'], inline=True)
                embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                selection = await client.wait_for("message", check = selectionCheck, timeout=60)
                selection = selection.content
        
            if selection.upper() == "CANCEL":
                embed = discord.Embed(
                title = "Modifying Events",
                description = "Cancelled Action",
                timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                color = discord.Color.red()
                )
                await message.channel.send(embed=embed)
                break
            elif selection.isnumeric():
                #select the event user chosen and then modify it
                selectedEvent = listEvents[int(selection)-1]
                utc = "05"
                if (time.localtime().tm_isdst):
                    utc = "04"

                #title
                embed = discord.Embed(
                    title = "Modifying Events",
                    description = "Please enter a new title. Enter \"SKIP\" to keep existing title.",
                    timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                    color = discord.Color.orange()
                )
                embed.add_field(name = "Current Title", value = selectedEvent['summary'])
                await message.channel.send(embed=embed)
                title = await client.wait_for("message", check=checkFromAuthor, timeout = 60)
                title = title.content
                if title.upper() != "SKIP":
                    selectedEvent['summary'] = title
                
                #desc
                embed = discord.Embed(
                    title = "Modifying Events",
                    description = "Please enter a new description. Enter \"SKIP\" to keep existing description.",
                    timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                    color = discord.Color.orange()
                )
                embed.add_field(name = "Current Description", value = selectedEvent['description'])
                await message.channel.send(embed=embed)
                desc = await client.wait_for("message", check=checkFromAuthor, timeout = 60)
                desc = desc.content
                if desc.upper() != "SKIP":
                    selectedEvent['description'] = desc

                #location
                embed = discord.Embed(
                    title = "Modifying Events",
                    description = "Please enter a new location. Enter \"SKIP\" to keep existing location.",
                    timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                    color = discord.Color.orange()
                )
                embed.add_field(name = "Current Location", value = selectedEvent['location'])
                await message.channel.send(embed=embed)
                location = await client.wait_for("message", check=checkFromAuthor, timeout = 60)
                location = location.content
                if location.upper() != "SKIP":
                    selectedEvent['location'] = location
                
                #Start Date
                embed = discord.Embed(
                    title = "Modifying Events",
                    description = "Please enter a new start date. Enter \"SKIP\" to keep existing start date.",
                    timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                    color = discord.Color.orange()
                )
                embed.add_field(name = "Current Start Date (format yyyymmdd)", value = getDate(selectedEvent['start']['dateTime']))
                await message.channel.send(embed=embed)
                startDate = await client.wait_for("message", check=checkDate, timeout = 60)
                startDate = startDate.content
                if startDate.upper() != "SKIP":
                    #Start Time
                    embed = discord.Embed(
                        title = "Modifying Events",
                        description = "Please enter a new start time. Enter \"SKIP\" to keep existing start time.",
                        timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                        color = discord.Color.orange()
                    )
                    embed.add_field(name = "Current Start Time (format hhmm for 24 hour or hh:mm <am/pm>)", value = getTime(selectedEvent['start']['dateTime']))
                    await message.channel.send(embed=embed)
                    startTime = await client.wait_for("message", check=checkTime, timeout = 60)
                    startTime = startTime.content
                    startTime = convertToMilTime(startTime)
                    if startTime.upper() != "SKIP":
                        selectedEvent['start']['dateTime'] =  startDate[0:4]+"-"+startDate[4:6]+"-"+startDate[6:8]+"T"+startTime+":00-"+utc+":00"
                    else:
                        selectedEvent['start']['dateTime'] = selectedEvent['start']['dateTime'][0:10]+"T"+startTime+":00-"+utc+":00"

                #End Date
                embed = discord.Embed(
                    title = "Modifying Events",
                    description = "Please enter a new end date. Enter \"SKIP\" to keep existing end date.",
                    timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                    color = discord.Color.orange()
                )
                embed.add_field(name = "Current End Date (format yyyymmdd)", value = getDate(selectedEvent['end']['dateTime']))
                await message.channel.send(embed=embed)
                endDate = await client.wait_for("message", check=checkEndDate, timeout = 60)
                endDate = endDate.content
                if endDate.upper() != "SKIP":
                
                    #End Time
                    embed = discord.Embed(
                        title = "Modifying Events",
                        description = "Please enter a new end time. Enter \"SKIP\" to keep existing end time.",
                        timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                        color = discord.Color.orange()
                    )
                    embed.add_field(name = "Current End Time (format hhmm for 24 hour or hh:mm <am/pm>)", value = getTime(selectedEvent['end']['dateTime']))
                    await message.channel.send(embed=embed)
                    endTime = await client.wait_for("message", check=checkEndTime, timeout = 60)
                    endTime = endTime.content
                    endTime = convertToMilTime(endTime)
                    if endTime.upper() != "SKIP":
                        selectedEvent['end']['dateTime'] =  endDate[0:4]+"-"+endDate[4:6]+"-"+endDate[6:8]+"T"+endTime+":00-"+utc+":00"
                    else:
                        selectedEvent['end']['dateTime'] = selectedEvent['end']['dateTime'][0:10]+"T"+endTime+":00-"+utc+":00"

                #check if event is recurring
                if "recurringEventId" in selectedEvent:
                    print("Recurring Event")
                    embed = discord.Embed(
                        title = "Modifying Events",
                        description = "Warning! This will change all events! Enter \"CONFIRM\" to continue or \"CANCEL\" to quit without changes.",
                        timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                        color = discord.Color.orange()
                    )
                    await message.channel.send(embed=embed)
                    result = await client.wait_for("message", check=checkFromAuthor, timeout = 60)
                    if result.ceonten.upper == "CANCEL":
                        embed = discord.Embed(
                            title = "Modifying Events",
                            description = "Cancelled without changes.",
                            timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                            color = discord.Color.red()
                        )
                        await message.channel.send(embed=embed)
                        break
                if (title.upper() == "SKIP" and desc.upper() == "SKIP" and location.upper() == "SKIP" and startDate.upper() == "SKIP" and endDate.upper() == "SKIP"):
                    embed = discord.Embed(
                            title = "Modifying Events",
                            description = "Cancelled without changes.",
                            timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                            color = discord.Color.red()
                        )
                    await message.channel.send(embed=embed)
                else:
                    link = calendarAPI.modifyEvent(selectedEvent)
                    embed = discord.Embed(
                        title = title, 
                        url = link,
                        description = "Event Modified Successfully!",
                        timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                        color = discord.Color.blue())
                    embed.set_author(name = message.author.display_name, icon_url = message.author.avatar_url)
                    embed.add_field(name = "Description", value = desc, inline=False)
                    embed.add_field(name = "Location", value = location, inline=False)
                    embed.add_field(name = "Start Date", value = str(selectedEvent['start']['dateTime']), inline=False)
                    embed.add_field(name = "End Date", value = str(selectedEvent['end']['dateTime']), inline=False)
                    embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)

    except asyncio.TimeoutError:
            print("Timed out; received no valid user inputs")
            embed = discord.Embed(
                title = "Error", 
                description = "Event Has Not Been Modified.",
                color = discord.Color.red())
            embed.add_field(name = "Timed Out", value = "Process cancelled. Please invoke .modifyevent if you wish to modify an event.", inline=False)
            await message.channel.send(embed=embed)
    
    except:
        embed = discord.Embed(
            title = "Error", 
            description = "An Error Has Occured. Please try again.",
            color = discord.Color.red())
        await message.channel.send(embed=embed)

@client.command(name = "delevent", help="Deletes an existing event.")
async def deleteEvent(message):
    selection = "NEXT"
    listEvents = []
    now = datetime.datetime.now()

    def checkFromAuthor(msg):
        return msg.author == message.author and msg.channel == message.channel
    def selectionCheck(msg):
        selectChoices = ['1', '2', '3', '4', '5', '6', 'NEXT', 'CANCEL']
        if checkFromAuthor(msg):
            return msg.content.upper() in selectChoices
        return False 
    def select(timeMin):
        #get next 6 events from given time (utc)
        nextEvents = calendarAPI.listEventsFromDate(timeMin)
        return nextEvents
    def checkResponse(msg):
        return checkFromAuthor(msg) and (msg.content == selectedEvent['summary'] or msg.content.upper() == "CANCEL") 

    try:
        listEvents = calendarAPI.listEvents()
        first = True
        while selection.upper() == "NEXT":
            if listEvents is None:
                embed = discord.Embed(
                    title = "There are no upcoming events to delete!",
                    description = "Do .newevent to add events to the calendar!", 
                    color = discord.Color.red(),
                    timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern"))
                    )
                await message.channel.send(embed=embed)
                break
            if (first):
                #first page
                embed = discord.Embed(
                    title = "Delete Event",
                    description = "Listing the 6 Upcoming Events",
                    timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                    color = discord.Color.orange()
                )
                embed.add_field(name="Select", value="Enter 1-6 to select the event you wish to delete, enter \"NEXT\" to get the next upcoming 6 events, or enter \"CANCEL\" to exit.", inline=False)
                for currEvent in listEvents:
                    embed.add_field(name=currEvent['summary'], value="["+currEvent['description']+"]("+currEvent['htmlLink']+")\n"+ currEvent['start']['dateTime'][0:10]+ " "+currEvent['start']['dateTime'][11:16]+" to "+currEvent['end']['dateTime'][0:10]+ " "+currEvent['end']['dateTime'][11:16]+"\nLocation: "+currEvent['location'], inline=True)
                embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                selection = await client.wait_for("message", check = selectionCheck, timeout=60)
                selection = selection.content
                first = False
            #if user wants to see more events
            else:
                #next page
                #convert endTime of the last event to utc for timeMin. using timeMin to search for the next events using google API
                listEvents = select(datetime.datetime.fromisoformat(listEvents[5]['end']['dateTime']).astimezone(pytz.utc).isoformat())
                embed = discord.Embed(
                    title = "Delete Event",
                    description = "Listing the next 6 Upcoming Events",
                    timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                    color = discord.Color.orange()
                    )
                embed.add_field(name="Select", value="Enter 1-6 to select the event you wish to modify, enter \"NEXT\" to get the next upcoming 6 events, or enter \"CANCEL\" to exit.", inline=False)
                for currEvent in listEvents:
                    embed.add_field(name=currEvent['summary'], value="["+currEvent['description']+"]("+currEvent['htmlLink']+")\n"+ currEvent['start']['dateTime'][0:10]+ " "+currEvent['start']['dateTime'][11:16]+" to "+currEvent['end']['dateTime'][0:10]+ " "+currEvent['end']['dateTime'][11:16]+"\nLocation: "+currEvent['location'], inline=True)
                embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                selection = await client.wait_for("message", check = selectionCheck, timeout=60)
                selection = selection.content
        
            if selection.upper() == "CANCEL":
                embed = discord.Embed(
                title = "Delete Event",
                description = "Cancelled Action",
                timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                color = discord.Color.red()
                )
                await message.channel.send(embed=embed)
                break
            elif selection.isnumeric():
                #select the event user chosen and then delete it
                selectedEvent = listEvents[int(selection)-1]
                embed = discord.Embed(
                    title = "Delete Event",
                    description = "Please review the event's details.",
                    url=selectedEvent['htmlLink'],
                    timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                    color = discord.Color.orange()
                    )
                embed.add_field(name = "Title", value = selectedEvent['summary'])
                embed.add_field(name = "Description", value = selectedEvent['description'])
                embed.add_field(name = "Start", value = selectedEvent['start']['dateTime'])
                embed.add_field(name = "End", value = selectedEvent['end']['dateTime'])
                embed.add_field(name = "Location", value = selectedEvent['location'])
                await message.channel.send(embed=embed)

                embed = discord.Embed(
                    title = "Delete Event",
                    description = "To delete the event, please enter the title of the event. To cancel, type \"CANCEL\"",
                    timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                    color = discord.Color.orange()
                    )
                await message.channel.send(embed=embed)
                response = await client.wait_for("message", check=checkResponse, timeout=60)
                if response.content.upper() == "CANCEL":
                    embed = discord.Embed(
                    title = "Delete Event",
                    description = "Cancelled Action",
                    timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                    color = discord.Color.red()
                    )
                    await message.channel.send(embed=embed)
                    break
                elif response.content == selectedEvent['summary']:
                    calendarAPI.deleteEvent(selectedEvent)
                    embed = discord.Embed(
                        title = "Deleted Event",
                        description = "Event Deleted Successfully!",
                        timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")),
                        color = discord.Color.blue())
                    await message.channel.send(embed=embed)
                    break                

    except asyncio.TimeoutError:
        print("Timed out; received no valid user inputs")
        embed = discord.Embed(
            title = "Error", 
            description = "Event Has Not Been Deleted.",
            color = discord.Color.red())
        embed.add_field(name = "Timed Out", value = "Process cancelled. Please invoke .delevent if you wish to delete an event.", inline=False)
        await message.channel.send(embed=embed)
    
    """ except:
        embed = discord.Embed(
            title = "Error", 
            description = "An Error Has Occured. Please try again.",
            color = discord.Color.red())
        await message.channel.send(embed=embed) """

"""
Scans through the next 3 events and sends out reminders depending on settings set on that event.
Background task will trigger every 1 minute.
"""
@tasks.loop(seconds=60)
async def background_task():
    if startUp:
        now = datetime.datetime.now().isoformat()
        listEvents = calendarAPI.listThreeEvents()
        #search through the next 3 events
        for x in (listEvents):
            reminder = x['reminders']['overrides'][0]['minutes']
            startTime = x['start']['dateTime']
            startTime = startTime.replace(startTime[19:],"")
            title = x['summary']
            htmlLink = x['htmlLink']
            id = x['id']

            reminderTime = datetime.datetime.fromisoformat(startTime) - timedelta(minutes = int(reminder))
            reminderTime = reminderTime.isoformat()

            #if the reminderTime has not been passed, add the upcoming event to the database
            if (reminderTime > now):
                #check if event has already been added
                if not dataBase.isAdded(id):
                    dataBase.addEvent(title, startTime, reminderTime, htmlLink, id)
                    print("ADDED TO DATABASE!")        
            
        #search through the database and send a reminder when the current time (now) has reached reminderTime of that event
        for y in dataBase.getEvents():
            if datetime.datetime.fromisoformat(y[2]).isoformat() <= now:
                embed = discord.Embed(
                    title = "Reminder",
                    description = y[0] + " is starting at "+ y[1] +"!", 
                    color = discord.Color.blue(),
                    timestamp = datetime.datetime.now().astimezone(pytz.timezone("US/Eastern"))
                    )
                embed.add_field(name="Link: ", value=y[3])
                dataBase.deleteEvent(y[4])
                channel = await client.fetch_channel(885573483814338560)
                await channel.send("@everyone")
                await channel.send(embed=embed)

        

    


background_task.start()
client.run(token)