"""
TODO:
✔️ Creating Events
⏰ Create Events using step-by-step commands
⏰ Modify Events
⏰ Modify Events using step-by-step commands
⏰ Deleting Events
⏰ Listing Events
⏰ Getting notifications from events
⏰ Add garbage collection
"""

from tokenize import String
import discord
from discord.ext import commands
import calendarAPI
import datetime
import asyncio
import time
import calendar

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
recurrenceCount (int: default=0), recurrenceInterval (int: default=0), 
recurrenceEnd (String: yyyymmddhhmm default=""), byday (String: MO,TU,WE,TH,FR,SA,SU default="")

title sets the title of the event to given string.
desc sets the description of the event to the given string; 
startTime sets the start time (date and time) of event (time is in EST). Format: yyyymmddhhmm
endTime sets the end time (date and time) of event (time is in EST). Format: yyyymmddhhmm
location sets the location of the event to the given string. if no string is provided, no location would be set.
reminder sets when to remind the event is about to start (in minutes). Default is 30 minutes.
frequency sets how often the event should repeat. WEEKLY repeats the event every week. DAILY repeats the event every day. Default is none (no repetition).
recurrenceCount sets how much the event should repeat. If recurrenceEnd has input, recurrenceCount will be ignored. Default is 0.
recurrenceInterval sets how much skip between events. Default is 0.
byday sets which day of the week to repeat on. If multiple, separate by comma. Default is no specification (""). Options: MO,TU,WE,TH,FR,SA,SU
recurrenceEnd sets the last day the event will stop repeating. Default is never (""). Format: yyyymmdd
"""
@client.command(name = "new", help = "Creates a new event using the given parameters")
async def newEvent(message: discord.Member, title: str, desc: str, startTime: str, 
endTime: str, location: str="", reminder: int=30, frequency: str="", 
recurrenceCount: str=0, recurrenceInterval: str=0, byday: str="",
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
                event = {
                    "summary": title,
                    "location": location,
                    "description": desc,
                    "start": {
                        "dateTime": startTime,
                        "timeZone": "America/Toronto",
                    },
                    "end": {
                        "dateTime": endTime,
                        "timeZone": "America/Toronto",
                    },
                    "reminders": {
                        'useDefault': False,
                        "overrides": [
                            {
                                "method": "popup",
                                "minutes": reminder
                            }
                        ]
                    }
                }
            else:
                #has repetition end date
                if recurrenceEnd != "00000000":
                    #if there are specified days of the week
                    if byday != "":
                        event = {
                        "summary": title,
                        "location": location,
                        "description": desc,
                        "start": {
                            "dateTime": startTime,
                            "timeZone": "America/Toronto",
                        },
                        "end": {
                            "dateTime": endTime,
                            "timeZone": "America/Toronto",
                        },
                        "recurrence": [
                            "RRULE:FREQ="+str(frequency)+";"+"UNTIL="+str(recurrenceEnd)+";INTERVAL="+str(recurrenceInterval)+";BYDAY="+str(byday),
                        ],
                        "reminders": {
                            'useDefault': False,
                            "overrides": [
                                {
                                    "method": "popup",
                                    "minutes": reminder
                                }
                            ]
                        }
                    }
                    else:
                        event = {
                            "summary": title,
                            "location": location,
                            "description": desc,
                            "start": {
                                "dateTime": startTime,
                                "timeZone": "America/Toronto",
                            },
                            "end": {
                                "dateTime": endTime,
                                "timeZone": "America/Toronto",
                            },
                            "recurrence": [
                                "RRULE:FREQ="+str(frequency)+";"+"UNTIL="+str(recurrenceEnd)+";INTERVAL="+str(recurrenceInterval),
                            ],
                            "reminders": {
                                'useDefault': False,
                                "overrides": [
                                    {
                                        "method": "popup",
                                        "minutes": reminder
                                    }
                                ]
                            }
                        }
                #if repetition end date not inputted
                else:
                    #if there are specified days of the week
                    if byday != "":
                        event = {
                        "summary": title,
                        "location": location,
                        "description": desc,
                        "start": {
                            "dateTime": startTime,
                            "timeZone": "America/Toronto",
                        },
                        "end": {
                            "dateTime": endTime,
                            "timeZone": "America/Toronto",
                        },
                        "recurrence": [
                            "RRULE:FREQ="+str(frequency)+";"+"COUNT="+str(recurrenceCount)+";INTERVAL="+str(recurrenceInterval)+";BYDAY="+str(byday),
                        ],
                        "reminders": {
                            'useDefault': False,
                            "overrides": [
                                {
                                    "method": "popup",
                                    "minutes": reminder
                                }
                            ]
                        }
                    }
                    else:
                        event = {
                            "summary": title,
                            "location": location,
                            "description": desc,
                            "start": {
                                "dateTime": startTime,
                                "timeZone": "America/Toronto",
                            },
                            "end": {
                                "dateTime": endTime,
                                "timeZone": "America/Toronto",
                            },
                            "recurrence": [
                                "RRULE:FREQ="+str(frequency)+";"+"COUNT="+str(recurrenceCount)+";INTERVAL="+str(recurrenceInterval)+";"
                            ],
                            "reminders": {
                                'useDefault': False,
                                "overrides": [
                                    {
                                        "method": "popup",
                                        "minutes": reminder
                                    }
                                ]
                            }
                        }
            link = calendarAPI.createEvent(event)
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
                else:
                    embed.add_field(name = "Repeating Amount", value = recurrenceCount, inline=False)
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
    def checkTime(msg):
        if (msg.author == message.author and msg.channel == message.channel):
            msg = msg.content
            print(msg[0:4:]+ " "+ msg[4:6:] + " " + msg[6:8: ])
            if msg.isnumeric():
                print("yes")
                if len(msg) == 8 and int(msg [0:4:]) >= now.year and int(msg[4:6:])>=now.month and int(msg[4:6:])<13:
                    print("yes")
                    if checkDay(int(msg[0:4]),int(msg[4:6:]), int(msg[6:8:])):
                        print("yes")
                        return True
        return False
    try:
        embed = discord.Embed(
            title = "Creating an Event", 
            color = discord.Color.orange())
        embed.add_field(name= "Title", value = "Please enter the name of the event", inline=False)
        await message.channel.send(embed=embed)
        title = await client.wait_for("message", check=checkText, timeout = 15)
        title = title.content
        print(title)

        embed = discord.Embed(
            title = "Creating an Event", 
            color = discord.Color.orange())
        embed.add_field(name= "Description", value = "Please enter the description of the event", inline=False)
        await message.channel.send(embed=embed)
        desc = await client.wait_for("message", check=checkText, timeout = 15)
        desc = desc.content
        print(desc)

        embed = discord.Embed(
            title = "Creating an Event", 
            color = discord.Color.orange())
        embed.add_field(name= "Start Time", value = "Please enter the start time of the event", inline=False)
        embed.add_field(name= "Format", value = "Input time as yyyymmdd", inline=False)
        await message.channel.send(embed=embed)
        startTime = await client.wait_for("message", check=checkTime, timeout = 15)
        startTime = startTime.content
        print(startTime)

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



   


client.run(token)