def noFreq(title, desc, startTime, endTime, location, reminder):
    return( {
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
                })

def hasFreqEndDate(title, desc, startTime, endTime, location, reminder, frequency, recurrenceEnd, recurrenceInterval, byday):
        return({
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
                    })

def hasFreqEndDateNoByDay(title, desc, startTime, endTime, location, reminder, frequency, recurrenceEnd, recurrenceInterval):
    return ({
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
        })

def onlyCount(title, desc, startTime, endTime, location, reminder, frequency, recurrenceCount, recurrenceInterval, byday):
    return({
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
        })

def onlyCountnoByDay(title, desc, startTime, endTime, location, reminder, frequency, recurrenceCount, recurrenceInterval):
    return({
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
        })

def repeatForever(title, desc, startTime, endTime, location, reminder, frequency, recurrenceInterval, byday):
    return({
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
                "RRULE:FREQ="+str(frequency)+";"+"INTERVAL="+str(recurrenceInterval)+";BYDAY="+str(byday)
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
        })

def repeatForevernoByDay(title, desc, startTime, endTime, location, reminder, frequency, recurrenceInterval):
    return({
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
                "RRULE:FREQ="+str(frequency)+";"+"INTERVAL="+str(recurrenceInterval)+";"
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
        })