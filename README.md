# To-Do-Discord-Bot

A Discord bot that will allow an user to view, modify, and add events to a google calendar.
The bot will then send out reminders to the server based on the event.

This bot uses both the Discord and Google REST APIs and will require both the discord token and a google OAuth credentials from Google Cloud Platform. On first time use, you will be prompted to log in (for google to generate a token).

Events will be created based on the calID in the calID.txt. To get the calID, go to your google calendar, select on the specific calendar you wish to use > Settings and sharing > Integrate Calendar > Calendar ID. Copy and paste the ID into a txt file named "calID".

# Creating an Event #

To start the process of creating an event, type ".newevent" into the channel. You will be prompted to enter an title for the event.
![Invoke .newevent](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/newevent.png)

The bot will then prompt the following:
![New Description](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/newdesc.png)
![Start Date of the Event](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/newstartdate.png)
![Start Time of the Event](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/newstarttime.png)
![End Date of the Event](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/newenddate.png)
![End Time of the Event](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/newendtime.png)
![Location of the Event](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/newlocation.png)
![When to Send Reminder](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/newreminder.png)
![Setting Frequency](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/newfrequency.png)

If you select none:

![Created New Event With No Frequency](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/neweventNoFreq.png)

If you select either "DAILY" or "WEEKLY":

![Setting Recurrence End/Count](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/newEventRecurr.png)

Setting Recurrence Interval is optional.

![Setting Recurrence Interval](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/newEventRecurrInterval.png)

Setting By Day is optional.
![Setting By Day](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/newEventByDay.png)

![Created New Event with Frequency](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/neweventFreq.png)

## Listing Events ##

Lists the next 6 upcoming events

![Invoke .listevents](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/listEvents.png)

## Modifiying an Event ##
![Invoke .modifyevent](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/modifyEvent.png)
![Modify Title](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/modifyTitle.png)
![Modify Description](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/modifyDesc.png)
![Modify Start Date](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/modifyStartDate.png)
![Modify Start Time](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/modifyStartTime.png)
![Modify End Date](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/modifyEndDate.png)
![Modify End Time](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/modifyEndTime.png)

Note: .modifyevent does not allow a user to change the recurrence rules.

End Result:

![Modified Event](https://github.com/superkor/To-Do-Discord-Bot/blob/main/images/modifiedEvent.png)


## Deleting an Event ##

