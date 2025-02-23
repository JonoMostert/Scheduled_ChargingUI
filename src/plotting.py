from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
from plotly.graph_objs import Figure
import plotly.graph_objects as go

from models import CombinedState
from utils import get_current_time_to_nearest_30_minutes

# These set the resampling period for graphing
PERIOD = timedelta(minutes=30)
PERIOD_STR = "30min"


def _convert_states_to_dataframe(states: list[CombinedState]) -> pd.DataFrame:
    """Convert to dataframe for ease of plotting with Plotly, and resample to 30mins"""    

    data = {
        "Time": [],
        "State of Charge": [],
        "Car is Charging": [],
        "Charge is Boost": [],
    }

    soc = soc_init = 60  # Initial State of Charge
    
    for idx, state in enumerate(states):
        data["Time"].append(state.time) # Instead of static time intervals, we can now use the real schedule from backemd
        data["Car is Charging"].append(state.charger_state.car_is_charging)
        data["Charge is Boost"].append(state.charger_state.charge_is_boost)

        # Simulated SOC Increase (assumption: 5% increase per charging interval)
        if idx == 0:
            data["State of Charge"].append(soc_init)
        else:
            if states[idx - 1].charger_state.car_is_charging:                
                soc = min(100, soc + 5)  # Max SOC is 100%
            data["State of Charge"].append(soc)

    df = pd.DataFrame(data)
   

    return df.reset_index() 


def plot_upcoming_charges(
    states: list[CombinedState], selected_time: datetime
) -> Figure:
    """Plot the upcoming charges for the car"""
    df = _convert_states_to_dataframe(states)    

    fig = px.line(df, x="Time", y="State of Charge")
    # Ensure the x-axis always shows 5 AM to 5 AM (fixed range)
    start_time = datetime.now().replace(hour=5, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=24)
    fig.update_xaxes(range=[start_time, end_time])

    if selected_time.hour < 5:
        selected_datetime = datetime.combine(datetime.today() + timedelta(days=1), selected_time) 
    else:
        selected_datetime = datetime.combine(datetime.today(), selected_time)

    # Add a vertical line at the current time
    fig.add_vline(
        x=selected_datetime, #rounded_time, #current_time,
        line_dash="dash",
        line_color="grey",
        label=dict(text="Now", textposition="top center"),
    )

    # Add vertical rectangles for charging periods
    for i, row in df.iterrows():
        if not row["Car is Charging"]:
            continue
        fig.add_vrect(
            x0=row["Time"],
            x1=row["Time"] + PERIOD,
            fillcolor="red" if row["Charge is Boost"] else "green",
            opacity=0.1,
            layer="below",
            # label=dict(
            #     text="Boost" if row["Charge is Boost"] else "Scheduled",
            #     font=dict(
            #         color="red" if row["Charge is Boost"] else "green",
            #     ),
            #     textposition="top center",
            # ),
        )

    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(size=14, color="rgba(0, 128, 0, 0.2)", symbol="square"),  
        name="Scheduled Charging"
    ))

    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(size=14, color="rgba(255, 0, 0, 0.2)", symbol="square"), 
        name="Boost Charging"
    ))

    fig.update_layout(
        yaxis_title="State of Charge",
        xaxis_title="Time",
        xaxis=dict(showgrid=False),
        yaxis=dict(range=[50, 100]), 
        legend=dict(
            title="Charging Legend",
            x=0.02, y=0.98,  
            xanchor="left", yanchor="top",
            bgcolor="rgba(255, 255, 255, 0.7)",  
            bordercolor="black",
            borderwidth=1
        ),
    )

    fig.update_traces(mode="markers+lines")
   
    return fig
