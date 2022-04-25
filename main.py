import discord
from discord.ext import commands
import calendarAPI
import time

token = open("token.txt", "r").readline()

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = ".", intents=intents)

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
.newevent takes arguments title (String), location (String), startTime (String: yyyymmddhhmm), endTime(String: yyyymmddhhmm), desc (String: default=""), reminder (int: default=0), frequency (String: weekly, daily, default=""), recurrenceCount (int: default=0), recurrenceInterval (int: default=0), recurrenceEnd (String: yyyymmddhhmm default="")
title sets the title of the event to given string.
location sets the location of the event to the given string.
startTime sets the start time (date and time) of event (time is in EST). Format: yyyymmddhhmm
endTime sets the end time (date and time) of event (time is in EST). Format: yyyymmddhhmm
desc sets the description of the event to the given string; if no string is provided, no description would be set.
reminder sets when to remind the event is about to start (in minutes). Default is 30 minutes.
frequency sets how often the event should repeat. WEEKLY repeats the event every week. DAILY repeats the event every day. Default is none (no repetition).
recurrenceCount sets how much the event should repeat. Default is 0.
recurrenceInterval sets how much skip between events. Default is 0.
recurrenceEnd sets the last day the event will stop repeating. Default is never (""). Format: yyyymmdd
"""
@client.command(name = "newevent", help = "Assigns the message author the role organizers")
async def newEvent(message, title, location, startTime, endTime, desc="", reminder=30, frequency="", recurrenceCount=0, recurrenceInterval=0, recurrenceEnd = "00000000"):
    creator = message.author
    if (len(startTime) != 12 or len(endTime) != 12 or len(recurrenceEnd) != 8):
        embed = discord.Embed(
                title = "Error", 
                description = "Invalid Date/time.",
                color = discord.Color.red())
        embed.add_field(name = "They must be in this format: yyyymmddhhmm.", value = "If it is a full day event, set both starting and ending hhmm to 0.", inline= False)
        await message.channel.send(embed=embed)
        print("Incorrect Date/Time Input")
    else:
        #check if we are in DST (i hate dst ahh)
        utc = "05"
        if (time.localtime().tm_isdst):
            utc = "04"
        startTime = startTime[0:4 : ] + "-" + startTime[4: 6 : ] + "-" + startTime[6: 8:] + "T" + startTime[8:10:]+":"+startTime[10: 12:]+":00-"+utc+":00"
        endTime = endTime[0:4 : ] + "-" + endTime[4: 6 : ] + "-" + endTime[6: 8:] + "T" + endTime[8:10:]+":"+endTime[10: 12:]+":00-"+utc+":00"
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
            if recurrenceInterval != "00000000":
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
                        "RRULE:FREQ="+str(frequency)+";"+"COUNT="+str(recurrenceCount)+";INTERVAL="+str(recurrenceInterval)+";UNTIL="+recurrenceEnd+"0000T000000Z"
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
        if (link != "0"):
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
            await message.channel.send(embed=embed)
        else:
            embed = discord.Embed(
                title = "Error",
                description = "Event Failed to be Created.",
                color = discord.Color.red())
            embed.add_field(name = link, value = "Please Try Again!", inline= False)
            await message.channel.send(embed=embed)

   


client.run(token)