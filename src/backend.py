# TODO: this file returns dummy data: everything should be replaced by calls to your logic
# Feel free to implement your logic within this process, or make calls to an external service

import streamlit as st

from models import ChargerState, DemoAdminState, CombinedState
from datetime import datetime, timedelta


# State management variables
charge_end_time = None  # Tracks when Boost Mode should end (if active). Based on calculation and therefore better to hold on backend, as Streamlit does not automatically track time-based updates


def get_future_states(demo_state: DemoAdminState) -> list[CombinedState]:
    """Return a list of future states for the system. This is used for plotting the charge trajectory."""
    # TODO: replace this with your logic

    global charge_end_time
    future_states = []
    
     # Fixed start and end times for 24-hour static window
    start_time = datetime.now().replace(hour=5, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=24)  
    simulated_now = datetime.combine(datetime.today(), demo_state.current_time)
    charge_end_time =  simulated_now + timedelta(minutes=60)  

    
    # Ensure session state variables exist (these booleans update dynamically based on user input (they do not updated based on calculations), therfore can be a streamlit session_state)
    if "car_is_charging" not in st.session_state:
        st.session_state.car_is_charging = False
    if "charge_is_boost" not in st.session_state:
        st.session_state.charge_is_boost = False
    if "sched_canceled_today" not in st.session_state:
        st.session_state.sched_canceled_today = False

    
    time_slot = start_time
    while time_slot <= end_time:
        # Determine charging behavior
        if st.session_state.charge_is_boost and simulated_now <= time_slot < charge_end_time:
            charger_state = ChargerState(car_is_charging=True, charge_is_boost=True, sched_canceled_today=st.session_state.sched_canceled_today)

        elif st.session_state.sched_canceled_today:
            charger_state = ChargerState(car_is_charging=False, charge_is_boost=False, sched_canceled_today=True)

        else:
            is_scheduled_time = 2 <= time_slot.hour < 5
            should_charge = is_scheduled_time and demo_state.car_is_home
            charger_state = ChargerState(car_is_charging=should_charge, charge_is_boost=False, sched_canceled_today=st.session_state.sched_canceled_today)

        future_states.append(CombinedState(time=time_slot, charger_state=charger_state))
        time_slot += timedelta(minutes=30)  # Increment by 30 minutes

    return future_states


def get_car_state(demo_state: DemoAdminState) -> ChargerState:
     

    now = demo_state.current_time
    is_scheduled_time = 2 <= now.hour < 5  # Scheduled window

    # Initialize session state if not already set
    if "car_is_charging" not in st.session_state:
        st.session_state.car_is_charging = False
    if "charge_is_boost" not in st.session_state:
        st.session_state.charge_is_boost = False
    if "sched_canceled_today" not in st.session_state:
        st.session_state.sched_canceled_today = False

    # Reset `sched_canceled_today` at midnight
    if now.hour == 0 and now.minute == 0:
        st.session_state.sched_canceled_today = False

    # If scheduled charging was manually stopped, DO NOT restart until tomorrow
    if st.session_state.sched_canceled_today:
        st.session_state.car_is_charging = False
        st.session_state.charge_is_boost = False

    # Auto-start scheduled charging at 2 AM if the car is home and plugged in
    elif demo_state.car_is_home and demo_state.car_is_plugged_in and is_scheduled_time:
        if not st.session_state.car_is_charging:  # Prevent restarting if already charging
            st.session_state.car_is_charging = True
            st.session_state.charge_is_boost = False
            st.toast("✅ Scheduled charging started (2 AM - 5 AM).", icon="🔋")

    return ChargerState(
        car_is_charging=st.session_state.car_is_charging,
        charge_is_boost=st.session_state.charge_is_boost,
        sched_canceled_today=st.session_state.sched_canceled_today
    )


def handle_start_charge(override_schedule: bool, boost_mode: bool, demo_state: DemoAdminState):
    """
    Handles the logic for starting a charge session.
    - If boost_mode is True, charge immediately for 60 minutes, then revert to schedule.
    - If override_schedule is False, follow the regular charging schedule.
    - If the car is away, charge without overriding schedule.
    """
    

    global charge_end_time
    
   
    if st.session_state.car_is_charging:
        st.warning("⚡ Car is already charging.")
        return

    st.session_state.car_is_charging = True
    st.session_state.charge_is_boost = boost_mode

    if boost_mode:
        charge_end_time = datetime.combine(datetime.today(), demo_state.current_time) + timedelta(minutes=60)
        st.toast("🚀 Boost Mode: Charging started for 60 minutes!", icon="⚡")
    elif override_schedule:
        st.toast("✅ Scheduled charging active.", icon="🔋")


def handle_stop_charge():
    """
    Handles stopping the charge session.
    - If Boost Mode is active, stop it early and revert to schedule.
    - If scheduled charging is active, disable it until morning.
    """
    
          

    if not st.session_state.car_is_charging:
        st.warning("⛔ Car is not currently charging.")
        return

    if st.session_state.charge_is_boost:
        st.session_state.charge_is_boost = False
        st.toast("⚡ Boost Mode stopped early, reverting to schedule.", icon="🔄")
    else:        
        st.session_state.sched_canceled_today = True
        st.toast("⛔ Scheduled charging stopped until tomorrow.", icon="🕒")

    st.session_state.car_is_charging = False
