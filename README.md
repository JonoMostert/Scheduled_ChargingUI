# The Challenge
In this task, we’re building a whitelabel app which our customers can put in the hands of their own end users to manage their electricity usage.
Your challenge is to implement a single screen for this app, namely the charge control panel: a screen the user can use to see what charging we have planned for their electric vehicle, and override it if necessary.

This panel is a little complex, because it needs to:
1. Show the user when the charge is scheduled to happen
Axle Tech Exercise: Engineering 2
2. Allow them to overrule the charge schedule and charge immediately if they
need to (e.g. they get home and want to go out again in an hour, so they
need to boost the charging)
3. Allow them to stop charging
4. Keep track of whether the current charge is the scheduled one, or the result
of an override, in order to determine the behaviour of the stop charging
button (see AC’s below)

## Acceptance Criteria
- User should be able to see what the scheduled charge is, and what their battery % (State of Charge, or SOC) will be at the end of it.
this obviously depends upon the starting battery %, which in reality we forecast; you can hardcode it to something like 60%

- Users should be able to hit a button to charge the car immediately
    - When they do so, the car should charge for a set period of time (e.g. 60
        minutes)
    - At the end of that time, the car should revert to the schedule
    - During this time, if the user hits “Stop Charge”, the car should revert to
        the schedule
- When scheduled charging is occurring, if the user hits “Stop Charge”, the
schedule should be disabled until the next morning
The charge schedule should only be applied when the user’s car is at home.
you should include a UI element that highlights whether the car is home or
not, and makes it clear how this relates to the charging (e.g. if you hit “Start
Charge” and you’re not at home, you’re not overriding the schedule: the
schedule only applies at home)

## Base assumptions
1. Scheduled charging is only active when the user is away. This was a requirement, but I went further to ensure that the user would not see the prediction of the scheduled charge if the car is away from home. The only ability in this state is for the user to do a boost charge for 60 minutes.
2. Boost charging will only last for 60 minutes and will not restart unless triggered again. If the user is at home or away, the scheduled charging session will not be overriden. The user will still be able to charge through the night as long as the car is at home.
3. The only way to stop a scheduled charge is during scheduled charging (ideally this would be an optional field as the user does not want to wait until 2am to stop the scheduled charge). This is more of an edge case as a user typically wants to have the car fully charged by morning.
4. Inidication of the car being at home is currently done with a toggle. In real life, this would be replaced with either geo-location, or EVSE (charging station) recognition. 
5. Car plugged in is currently a toggle. In real life, the BMS or Charging Controller will indicate if the plug is inserted by monitoring the Proximity Pilot pin resistance.
6. State of charge is currently hardcoded to 60% initially and charges at 10% every hour - this would be dynamically updated from the BMS and is reliant on charging rates from the battery, as well as AC charging power from the OBC and station.
7. The charging schedule will not resume if charging was stopped during a scheduled charging session until the next day.
8. The user has no way of determining the state of charging without this UI.
9. When the user selects a current time from the drop down menu (only to be used by the reviewer), that any time selected after midnight will refelct for the next day and not the current day.

## Functionailty that needs improvement
1. Currently if I stop a scheduled charge and attempt a boost charge, it does not work. My logic needs to be reworked to account for this. I chose not to spend too much time on this as it is considered an edge case.
2. The user should be able to deactivate schduled charge by toggle. As mentioned, this is an edge case so I did not spend much time on it as the user typically want's the car to be fully charged by morning.
3. At the moment, the buttons need to be pressed twice before they get updated. This would be a good change to spend time on, but for the purpose of handing this task in on time I moved on.
4. Allow the user to select the time to perform a scheduled charge.
