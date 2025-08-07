import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

pointing_folder = "../data/pointing/"
pointing_file = (
    "lexi_look_direction_data_uninterpolated_2025-03-02_00-00-00_to_2025-03-16_23-59-59_v0.0.csv"
)

df_lexi_pointing = pd.read_csv(pointing_folder + pointing_file)
# Set epoch as index
df_lexi_pointing.set_index("Epoch", inplace=True, drop=True)

# Make subplots for RA and Dec
fig = make_subplots(
    rows=2, cols=1, shared_xaxes=True, subplot_titles=["Right Ascension", "Declination"]
)

keys = ["dec_lexi", "ra_lexi"]
colors = ["cyan", "magenta"]
min_time = "2025-03-06T14:30:00Z"
max_time = "2025-03-06T17:05:00Z"
# Convert it to datetime
min_time = pd.to_datetime(min_time)
max_time = pd.to_datetime(max_time)

# Select the data within the specified time range
df_lexi_pointing.index = pd.to_datetime(df_lexi_pointing.index, utc=True)
df_lexi_pointing = df_lexi_pointing.loc[min_time:max_time]

for i, key in enumerate(keys):
    fig.add_trace(
        go.Scattergl(
            x=df_lexi_pointing.index,
            y=df_lexi_pointing[key],
            mode="markers",
            marker=dict(size=5, symbol="circle", color=colors[i], opacity=1),
            name=key,
        ),
        row=i + 1,
        col=1,
    )

    fig.update_yaxes(title_text=key, row=i + 1, col=1)

fig.update_layout(
    height=800,
    width=1200,
    title_text="LEXI Right Ascension and Declination",
    template="plotly_dark",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

fig.update_xaxes(title_text="Time (UTC)", row=2, col=1)
# Set x-axis range
fig.update_xaxes(range=[min_time, max_time], row=2, col=1)

# Save as HTML
fig.write_html("../data/pointing/LEXI_pointing_ra_dec.html")


pointing_file_interpolated = "lexi_look_direction_data_resampled_interpolated_2025-03-02_00-00-00_to_2025-03-16_23-59-59_v0.0.csv"

df_lexi_pointing_interpolated = pd.read_csv(pointing_folder + pointing_file_interpolated)
# Set epoch as index
df_lexi_pointing_interpolated.set_index("Epoch", inplace=True, drop=True)

# Select the data within the specified time range
df_lexi_pointing_interpolated.index = pd.to_datetime(df_lexi_pointing_interpolated.index, utc=True)
df_lexi_pointing_interpolated = df_lexi_pointing_interpolated.loc[min_time:max_time]
# Make subplots for RA and Dec
fig = make_subplots(
    rows=2, cols=1, shared_xaxes=True, subplot_titles=["Right Ascension", "Declination"]
)

keys = ["dec_lexi", "ra_lexi"]
colors = ["cyan", "magenta"]
for i, key in enumerate(keys):
    fig.add_trace(
        go.Scattergl(
            x=df_lexi_pointing_interpolated.index,
            y=df_lexi_pointing_interpolated[key],
            mode="markers",
            marker=dict(size=5, symbol="circle", color=colors[i], opacity=1),
            name=key,
        ),
        row=i + 1,
        col=1,
    )

    fig.update_yaxes(title_text=key, row=i + 1, col=1)

fig.update_layout(
    height=800,
    width=1200,
    title_text="LEXI Right Ascension and Declination (Interpolated)",
    template="plotly_dark",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

fig.update_xaxes(title_text="Time (UTC)", row=2, col=1)
# Set x-axis range
fig.update_xaxes(range=[min_time, max_time], row=2, col=1)
# Save as HTML
fig.write_html("../data/pointing/LEXI_pointing_ra_dec_interpolated.html")
