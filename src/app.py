import streamlit as st
from datetime import datetime, timedelta
import backend
from models import DemoAdminState
from plotting import plot_upcoming_charges
from utils import get_current_time_to_nearest_30_minutes


def get_demo_state() -> DemoAdminState:
    rounded_time = get_current_time_to_nearest_30_minutes()

    # Generate dropdown options in 30-minute intervals
    time_options = [datetime.strptime(f"{h:02d}:{m:02d}", "%H:%M").time() for h in range(24) for m in [0, 30]]

    with st.sidebar:
        st.subheader("Demo Admin Controls")
        st.write("Use these controls to simulate the car and charger state.")
       
        selected_time = st.selectbox("Current Time", time_options, index=time_options.index(rounded_time.time()))

        if selected_time.hour < 5:
            selected_datetime = datetime.combine(datetime.today() + timedelta(days=1), selected_time)
        else:
            selected_datetime = datetime.combine(datetime.today(), selected_time)

        car_is_plugged_in = st.toggle("Plugged in", value=True)
        car_is_home = st.toggle("Car is at Home", value=True)  # New toggle

    return DemoAdminState(car_is_plugged_in=car_is_plugged_in, current_time=selected_datetime.time(), car_is_home=car_is_home)


def controls(car_is_plugged_in: bool, car_is_home: bool, car_is_charging: bool, charge_is_boost: bool):
    st.subheader("Controls")
    c1, c2 = st.columns([1, 1])

    if not car_is_plugged_in:
        # Case: Car is not plugged in
        start_disabled = True
        stop_disabled = True
        start_label = "Start Charge (Car not plugged in)"
        stop_label = "Stop Charge (Car not plugged in)"
    elif car_is_home:
        if car_is_charging and charge_is_boost:
            # Case: Boost Mode is active
            start_disabled = True
            stop_disabled = False
            start_label = "Start Charge: Boost"
            stop_label = "Stop Charge (Boost Mode)"
        elif car_is_charging and not charge_is_boost:
            # Case: Charging is scheduled (rare edge case)
            start_disabled = True
            stop_disabled = False
            start_label = "Scheduled Charging Active"
            stop_label = "Stop Charging"
        else:
            # Case: Scheduled charging is default, allow Boost Mode
            start_disabled = False
            stop_disabled = True
            start_label = "Start Charge: Boost"
            stop_label = "Stop Charge"
    else:
        # Case: Car is not at home, only Boost Mode is available
        start_disabled = car_is_charging  # Disable Start if already charging
        stop_disabled = not car_is_charging  # Disable Stop if not charging
        start_label = "Start Charge: Boost (Away)"
        stop_label = "Stop Charge"

    start_button = c1.button(start_label, disabled=start_disabled)
    stop_button = c2.button(stop_label, disabled=stop_disabled)
    
    return start_button, stop_button

if __name__ == "__main__":
    demo_state = get_demo_state()
    car_state = backend.get_car_state(demo_state)
    
    if demo_state.car_is_home and car_state.sched_canceled_today:
        st.success("🚗 Car is at home, but scheduled charging will resume tomorrow")
    elif demo_state.car_is_home:
        st.success("🚗 Car is at home - charging schedule active (2am to 5am)")
    else:
        st.warning("🏠 Car is away - charging schedule disabled")

    
    st.subheader("Charging Schedule")

    st.plotly_chart(
        plot_upcoming_charges(
            backend.get_future_states(demo_state),
            selected_time=demo_state.current_time,
        )
    ) #demo_state.current_time
    start_charging, stop_charging = controls(
        demo_state.car_is_plugged_in,
        demo_state.car_is_home,
        car_state.car_is_charging,
        car_state.charge_is_boost,
    )

    if start_charging:
        if demo_state.car_is_home:
            if not car_state.car_is_charging:
                backend.handle_start_charge(override_schedule=True, boost_mode=True, demo_state=demo_state)  # Start Boost Mode at home
        else:
            backend.handle_start_charge(override_schedule=False, boost_mode=True, demo_state=demo_state)  # Start Boost Mode away from home

    if stop_charging:
        if car_state.charge_is_boost:
            backend.handle_stop_charge()  # Stop Boost Mode and revert to schedule if at home
        else:
            backend.handle_stop_charge()  # Stop charging without reverting schedule (away from home)
