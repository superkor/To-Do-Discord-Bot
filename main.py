"""
TODO:
✔️ Creating Events
✔️ Create Events using step-by-step commands
⏰ Listing Events
⏰ Modify Events
⏰ Modify Events using step-by-step commands
⏰ Deleting Events
⏰ Getting notifications from events
⏰ Add garbage collection
"""

from distutils.log import error
from tokenize import String
import discord
from discord.ext import commands
import calendarAPI
import datetime
import asyncio
import time
import calendar
import event 

token = open("token.txt", "r").readline()

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = ".", intents=intents)

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
    try:
        calendarAPI.main()
    except:
        print("Error with calendarAPI.py. Stopping bot...")
        exit()
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="your calendar!"))
    print(f"{client.user} has connected to Discord!")

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
@client.command(name = "new", help = "Creates a new event using the given parameters")
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

@client.command(name = "newevent", help="Creates a new event via a step-by-step guide")
async def create(message: discord.Member):
    """
    newCheck() will check user input and the bot will only respond if the conditions are met 
    """
    now = datetime.datetime.now()
    def checkDay(year:int, month: int, day: int):
        lastDayOfMonths = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if calendar.isleap(year):
            lastDayOfMonths[2] = 29
        return (now.day <= day <= lastDayOfMonths[month])
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
                    if (int(time[0:2:]) >=0 and int(time[0:2:]) <=12 and int(time[3:4:]) >=0 and int(time[3:5:])<= 59):
                        #check if msg[6:8:] is am or pm
                        if (time[6:8:].lower() == "am" or time[6:8:].lower() =="pm"):
                            return True
        return False
    def convertToMilTime(time):
        if len(time) == 8:
            if (time[6:8:].lower() == "pm"):
                time = time.replace(" pm", "")
                time = str(int(time[0:2:])+12)+time[2:]
                time = time.replace(":", "")
            else:
                time = time.replace(" am", "")
                time = time.replace(":", "") 
        return time
    def checkNum(msg):
        return (checkText(msg) and msg.content.isnumeric())
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
        if checkText(msg) and checkNum(msg):
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
        if checkText(msg) and len(msg.content) == 2:
            byDayCheck = ["MO", "TU", "WE", "TH", "FR", "SA", "SU", "NO"]
            return msg.content.upper() in byDayCheck
        return False

    try:
        #title
        embed = discord.Embed(
            title = "Creating an Event", 
            color = discord.Color.orange())
        embed.add_field(name= "Title", value = "Please enter the name of the event", inline=False)
        await message.channel.send(embed=embed)
        title = await client.wait_for("message", check=checkText, timeout = 60)
        title = title.content
        print(title)

        #Description
        embed = discord.Embed(
            title = "Creating an Event", 
            color = discord.Color.orange())
        embed.add_field(name= "Description", value = "Please enter the description of the event", inline=False)
        await message.channel.send(embed=embed)
        desc = await client.wait_for("message", check=checkText, timeout = 60)
        desc = desc.content
        print(desc)

        #Start Date
        embed = discord.Embed(
            title = "Creating an Event", 
            color = discord.Color.orange())
        embed.add_field(name= "Start Date", value = "Please enter the start Date of the event", inline=False)
        embed.add_field(name= "Format", value = "Input time as yyyymmdd", inline=False)
        await message.channel.send(embed=embed)
        startDate = await client.wait_for("message", check=checkDate, timeout = 60)
        startDate = startDate.content
        print(startDate)

        #Start Time
        embed = discord.Embed(
            title = "Creating an Event", 
            color = discord.Color.orange())
        embed.add_field(name= "Start Time", value = "Please enter the start time of the event", inline=False)
        embed.add_field(name= "Format", value = "Input time as hhmm (24 hour) or hh:mm <am/pm>", inline=False)
        await message.channel.send(embed=embed)
        startTime = await client.wait_for("message", check=checkTime, timeout = 60)
        startTime = startTime.content

        #format time to be hhmm (24 hour) if it isn't already
        startTime = convertToMilTime(startTime)
        print(startTime)

        #End Date
        embed = discord.Embed(
            title = "Creating an Event", 
            color = discord.Color.orange())
        embed.add_field(name= "End Date", value = "Please enter the end date of the event", inline=False)
        embed.add_field(name= "Format", value = "Input time as yyyymmdd", inline=False)
        await message.channel.send(embed=embed)
        endDate = await client.wait_for("message", check=checkEndDate, timeout = 60)
        endDate = endDate.content
        print(endDate)


        #End Time
        embed = discord.Embed(
            title = "Creating an Event", 
            color = discord.Color.orange())
        embed.add_field(name= "End Time", value = "Please enter the end time of the event", inline=False)
        embed.add_field(name= "Format", value = "Input time as hhmm (24 hour) or hh:mm <am/pm>", inline=False)
        await message.channel.send(embed=embed)
        endTime = await client.wait_for("message", check=checkEndTime, timeout = 60)
        endTime = endTime.content
        print(endTime)

        #format time to be hhmm (24 hour) if it isn't already
        endTime = convertToMilTime(endTime) 
        print(endTime)


        #check if we are in DST (i hate dst ahh)
        utc = "05"
        if (time.localtime().tm_isdst):
            utc = "04"
        startTime = startDate[0:4 : ] + "-" + startDate[4: 6 : ] + "-" + startDate[6: 8:] + "T" + startTime[0:2:]+":"+startTime[2:4:]+":00-"+utc+":00"
        endTime = endDate[0:4 : ] + "-" + endDate[4: 6 : ] + "-" + endDate[6: 8:] + "T" + endTime[0:2:]+":"+endTime[2:4:]+":00-"+utc+":00"


        #Location
        embed = discord.Embed(
            title = "Creating an Event", 
            color = discord.Color.orange())
        embed.add_field(name= "Location", value = "Please enter the location of the event", inline=False)
        await message.channel.send(embed=embed)
        location = await client.wait_for("message", check=checkText, timeout = 60)
        location = location.content
        print(location)

        #Reminder
        embed = discord.Embed(
            title = "Creating an Event", 
            color = discord.Color.orange())
        embed.add_field(name= "Reminder", value = "Please enter when you want a reminder before the event starts (in minutes)?", inline=False)
        await message.channel.send(embed=embed)
        reminder = await client.wait_for("message", check=checkNum, timeout = 60)
        reminder = reminder.content
        print(reminder)

        freqBool = True
        #Frequency
        embed = discord.Embed(
            title = "Creating an Event", 
            color = discord.Color.orange())
        embed.add_field(name= "Frequency", value = "Please enter DAILY/WEEKLY/NONE if you wish to have the event repeat daily, repeat weekly, or to not repeat.", inline=False)
        await message.channel.send(embed=embed)
        frequency = await client.wait_for("message", check=checkFreq, timeout = 60)
        frequency = frequency.content.upper()
        print(frequency)

        if (frequency == "NONE"):
            freqBool = False
        if (freqBool):
            unlimited = False
            recurrenceCount = -1
            recurrenceEnd = -1
            #recurrenceEnd or Count
            embed = discord.Embed(
                title = "Creating an Event", 
                color = discord.Color.orange())
            embed.add_field(name= "Recurrence End", value = "Please enter a date (yyyymmdd) you want the repetition to end on or enter a number of times (<=100) you wish the event to repeat.", inline=False)
            embed.add_field(name= "Infinite Repeat", value = "Please enter 0 to have the event infinitely repeat.", inline=False)
            await message.channel.send(embed=embed)
            recEnd = await client.wait_for("message", check=checkRecEnd, timeout = 60)
            recEnd = recEnd.content
            print(recEnd)
            if (int(recEnd) == 0):
                unlimited = True
            elif (int(recEnd) <=100):
                recurrenceCount = recEnd  
            else:
                recurrenceEnd = recEnd
            
            #recurrenceInterval
            embed = discord.Embed(
                title = "Creating an Event", 
                color = discord.Color.orange())
            embed.add_field(name= "Recurrence Interval", value = "Please enter how often you want the event to repeat (Max 10).", inline=False)
            await message.channel.send(embed=embed)
            recurrenceInterval = await client.wait_for("message", check=checkInterval, timeout = 60)
            recurrenceInterval = recurrenceInterval.content
            print(recurrenceInterval)

            #recurrenceInterval
            embed = discord.Embed(
                title = "Creating an Event", 
                color = discord.Color.orange())
            embed.add_field(name= "Recurrence ByDay", value = "Please enter the day of the week you want the event to repeat (MO,TU,WE,TH,FR,SA,SU).", inline=False)
            embed.add_field(name= "Skip Recurrence ByDay", value = "Please enter \"NO\" to skip.", inline=False)
            await message.channel.send(embed=embed)
            byday = await client.wait_for("message", check=checkByDay, timeout = 60)
            byday = byday.content
            print(byday)
        
            #infinite repeat
            if (unlimited):
                #No ByDay
                if (byday.content.upper() == "NO"):
                    newEvent = event.repeatForevernoByDay(title, desc, startTime, endTime, location, reminder, frequency, recurrenceInterval)
                else:
                    newEvent = event.repeatForever(title, desc, startTime, endTime, location, reminder, frequency, recurrenceInterval, byday) 
            #finite repeat
            else:
                #recurrence end date set
                if recurrenceCount == -1:
                    #no byday
                    if (byday.content.upper() == "NO"):
                        newEvent = event.hasFreqEndDate(title, desc, startTime, endTime, location, reminder, frequency, recurrenceEnd, recurrenceInterval, byday)
                    else:
                        newEvent = event.hasFreqEndDateNoByDay(title, desc, startTime, endTime, location, reminder, frequency, recurrenceEnd, recurrenceInterval)   
                #recurrence count set
                else:
                    #no byday
                    if (byday.content.upper() == "NO"):
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
            if byday != "NO":
                embed.add_field(name = "Every", value = byday, inline=False)
        await message.channel.send(embed=embed)



    except asyncio.TimeoutError:
            print("Timed out; received no valid user inputs")
            embed = discord.Embed(
                title = "Error", 
                description = "Event Has Not Been Created.",
                color = discord.Color.red())
            embed.add_field(name = "Timed Out", value = "Process cancelled. Please invoke .newevent if you wish to create an event.", inline=False)
            await message.channel.send(embed=embed)
    
    """ except:
        embed = discord.Embed(
            title = "Error", 
            description = "Event Has Not Been Created.",
            color = discord.Color.red())
        embed.add_field(name = "Uncaught Exception", value = "Please ensure your inputs are correct and try again.", inline=False)
        await message.channel.send(embed=embed) """

@client.command(name = "listevents", help="Lists next 5 upcoming events")
async def create(message: discord.Member):
    listEvents = calendarAPI.listEvents()
    print (listEvents)
    embed = discord.Embed(
            title = "Next 10 upcoming events", 
            color = discord.Color.green())
    embed.add_field(name="Title", value="[Desc](https://google.ca)")
    await message.channel.send(embed=embed)
   


client.run(token)