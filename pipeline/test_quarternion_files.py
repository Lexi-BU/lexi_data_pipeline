import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

quaternion_folder = "../data/quaternions/"

sunset_file_act = "LEXI_q_LandActual_ITRF.csv"
full_mission_file_act = "LEXI_q_LandAct_ITRF_1min.csv"

# Load CSVs
df_sunset_act = pd.read_csv(quaternion_folder + sunset_file_act)
df_full_mission_act = pd.read_csv(quaternion_folder + full_mission_file_act)

# Drop Epoch_MJD column if it exists
df_sunset_act.drop(columns=["Epoch_MJD"], errors="ignore", inplace=True)
df_full_mission_act.drop(columns=["Epoch_MJD"], errors="ignore", inplace=True)

# Convert time to datetime and set as index
df_sunset_act["Epoch_UTC"] = pd.to_datetime(
    df_sunset_act["Epoch_UTC"].str.slice(0, -3), format="mixed", utc=True
)
df_full_mission_act["Epoch_UTC"] = pd.to_datetime(
    df_full_mission_act["Epoch_UTC"].str.slice(0, -3), format="mixed", utc=True
)

df_sunset_act.set_index("Epoch_UTC", inplace=True)
df_full_mission_act.set_index("Epoch_UTC", inplace=True)

df_sunset_act.sort_index(inplace=True)
df_full_mission_act.sort_index(inplace=True)

# Time range for x-axis
min_sunset_time = df_sunset_act.index.min()
max_sunset_time = df_sunset_act.index.max()

min_full_mission_time = df_full_mission_act.index.min()
max_full_mission_time = df_full_mission_act.index.max()

# Create subplots (4 rows, 1 column)
fig = make_subplots(rows=4, cols=1, shared_xaxes=True, subplot_titles=["q0", "q1", "q2", "q3"])

keys = ["q0", "q1", "q2", "q3"]

for i, key in enumerate(keys):
    fig.add_trace(
        go.Scattergl(
            x=df_sunset_act.index,
            y=df_sunset_act[key],
            mode="markers",
            marker=dict(
                size=10,
                symbol="diamond",
                color="white",
                opacity=1,
            ),
            name="Sunset",
            legendgroup="Sunset",
            showlegend=(i == 0),
        ),
        row=i + 1,
        col=1,
    )

    fig.add_trace(
        go.Scattergl(
            x=df_full_mission_act.index,
            y=df_full_mission_act[key],
            mode="markers",
            marker=dict(size=5, symbol="circle", color="red", opacity=1),
            name="Full Mission",
            legendgroup="Full Mission",
            showlegend=(i == 0),
        ),
        row=i + 1,
        col=1,
    )

    fig.update_yaxes(title_text=key, row=i + 1, col=1)

# Update layout
fig.update_layout(
    height=1200,
    width=1200,
    title_text="LEXI Quaternion Comparison (Sunset vs Full Mission)",
    template="plotly_dark",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

# Restrict to sunset time range

min_time = "2025-03-06T14:30:00Z"
max_time = "2025-03-06T17:05:00Z"
# Convert it to datetime
min_time = pd.to_datetime(min_time)
max_time = pd.to_datetime(max_time)
fig.update_xaxes(range=[min_time, max_time])
fig.update_xaxes(title_text="Time (UTC)", row=4, col=1)

# Save as HTML
fig.write_html("../data/quaternions/LEXI_quaternion_comparison.html")
