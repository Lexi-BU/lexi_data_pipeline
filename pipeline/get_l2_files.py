from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from astropy.io import fits
from astropy.wcs import WCS


@dataclass
class InstrumentMeta:
    mission: str | None = "CLPS"
    observatory: str | None = "Moon Surface (LEXI)"
    telescope: str = "LEXI"
    instrument: str = "LEXI Camera"
    detector: str | None = None
    observer: str = "LEXI L1c pipeline"
    filter_name: str | None = None
    obs_mode: str | None = None
    point_id: str | None = None


def df_to_hist2d_fits(
    df: pd.DataFrame,
    *,
    # Which columns to histogram
    x_col: str = "photon_RA",  # or "photon_az"
    y_col: str = "photon_Dec",  # or "photon_el"
    # Time binning
    bin_minutes: int = 5,
    date_beg: datetime | None = None,  # if None -> min Epoch
    date_end: datetime | None = None,  # if None -> max Epoch rounded up
    # Spatial binning
    x_range: tuple[float, float] | None = None,  # if None -> data min/max
    y_range: tuple[float, float] | None = None,
    x_bins: int = 180,  # e.g., 2° RA bins over 360°
    y_bins: int = 90,  # e.g., 2° Dec bins over 180°
    # Output scaling
    as_rate: bool = False,  # True => counts/s
    # Output file
    filename: str = "lexi_l1c_hist2d_5min.fits",
    # Headers
    solarnet_level: float = 1.0,
    meta: InstrumentMeta = InstrumentMeta(),
    bname: str = "Counts 2D hist",
    btype: str = "intensity",
    extra_history: list[str] | None = None,
) -> str:
    """
    Build 5-min time-sliced 2D histograms from an event dataframe and write to a SOLARNET-style FITS.
    df index must be a timezone-aware datetime (UTC recommended).
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("df.index must be a DatetimeIndex (timezone-aware).")
    if df.index.tz is None:
        # treat as UTC if naive
        df = df.tz_localize("UTC")
    else:
        df = df.tz_convert("UTC")

    # Extract event arrays
    x = pd.to_numeric(df[x_col], errors="coerce").to_numpy(dtype=float)
    y = pd.to_numeric(df[y_col], errors="coerce").to_numpy(dtype=float)
    t_unix = df.index.asi8.astype(np.float64) / 1e9  # nanoseconds → seconds

    valid = np.isfinite(x) & np.isfinite(y) & np.isfinite(t_unix)
    if not np.any(valid):
        raise ValueError("No valid rows after filtering finite x/y/time.")
    x, y, t_unix = x[valid], y[valid], t_unix[valid]

    # --- Time bin edges (snap to bin boundaries, guarantee ≥1 bin) ---
    bin_sec = int(bin_minutes) * 60

    t0_data = (
        float(np.nanmin(t_unix))
        if date_beg is None
        else (
            (
                date_beg.replace(tzinfo=timezone.utc) if date0_beg.tzinfo is None else date_beg
            ).timestamp()
        )
    )
    t1_data = (
        float(np.nanmax(t_unix))
        if date_end is None
        else (
            (
                date_end.replace(tzinfo=timezone.utc) if date_end.tzinfo is None else date_end
            ).timestamp()
        )
    )

    # Snap to 5‑min grid
    t0 = np.floor(t0_data / bin_sec) * bin_sec
    t1 = np.ceil(t1_data / bin_sec) * bin_sec

    # If span collapses (e.g., exactly one timestamp or float fuzz), force one bin
    if t1 <= t0:
        t1 = t0 + bin_sec

    time_edges = np.arange(t0, t1 + 1e-9, bin_sec, dtype=float)
    n_t = len(time_edges) - 1
    if n_t <= 0:
        raise ValueError(f"No time bins (t0={t0}, t1={t1}, bin_sec={bin_sec}, edges={time_edges})")

    # Spatial ranges / edges
    if x_range is None:
        x0, x1 = float(np.nanmin(x)), float(np.nanmax(x))
    else:
        x0, x1 = x_range
    if y_range is None:
        y0, y1 = float(np.nanmin(y)), float(np.nanmax(y))
    else:
        y0, y1 = y_range
    if not np.isfinite([x0, x1, y0, y1]).all() or x1 <= x0 or y1 <= y0:
        raise ValueError("Invalid x/y ranges")

    x_edges = np.linspace(x0, x1, x_bins + 1, dtype=float)
    y_edges = np.linspace(y0, y1, y_bins + 1, dtype=float)

    # Vectorized binning (fast):
    it = np.digitize(t_unix, time_edges) - 1
    ix = np.digitize(x, x_edges) - 1
    iy = np.digitize(y, y_edges) - 1
    ok = (it >= 0) & (it < n_t) & (ix >= 0) & (ix < x_bins) & (iy >= 0) & (iy < y_bins)

    cube = np.zeros((n_t, y_bins, x_bins), dtype=np.float32)
    # accumulate counts
    np.add.at(cube, (it[ok], iy[ok], ix[ok]), 1.0)

    if as_rate:
        cube /= float(bin_sec)  # counts/s

    # ---- Build WCS (RA/Dec CAR or generic degrees) + UTC time axis ----
    w = WCS(naxis=3)
    # Choose labels from columns (purely cosmetic; still degrees)
    if x_col.lower().endswith("ra") and y_col.lower().endswith("dec"):
        w.wcs.ctype = ["RA---CAR", "DEC--CAR", "UTC"]
    else:
        # generic degree axes (still compliant); viewers will show units
        w.wcs.ctype = ["GLON-CAR", "GLAT-CAR", "UTC"]  # or custom; FITS allows non-standard CTYPEs
    w.wcs.cunit = ["deg", "deg", "s"]
    w.wcs.cdelt = [
        (x_edges[1] - x_edges[0]),
        (y_edges[1] - y_edges[0]),
        float(bin_sec),
    ]
    w.wcs.crpix = [1.0, 1.0, 1.0]
    w.wcs.crval = [
        0.5 * (x_edges[0] + x_edges[1]),
        0.5 * (y_edges[0] + y_edges[1]),
        0.5 * float(bin_sec),
    ]

    hdr = w.to_header()

    # ---- SOLARNET / Obs-HDU keywords ----
    datebeg_dt = datetime.fromtimestamp(time_edges[0], tz=timezone.utc)
    dateend_dt = datetime.fromtimestamp(time_edges[-1], tz=timezone.utc)
    hdr["EXTNAME"] = ("OBSERVATION", "Obs-HDU for 2D time-binned histograms")
    hdr["SOLARNET"] = (float(solarnet_level), "SOLARNET compliance intent (1=full, 0.5=partial)")
    hdr["OBS_HDU"] = (1, "Marks this HDU as an Obs-HDU")
    hdr["TIMESYS"] = ("UTC", "Time system for DATE-* and DATEREF")
    hdr["DATE-BEG"] = (datebeg_dt.strftime("%Y-%m-%dT%H:%M:%S"), "Acquisition start")
    hdr["DATE-END"] = (dateend_dt.strftime("%Y-%m-%dT%H:%M:%S"), "Acquisition end")
    hdr["DATEREF"] = (datebeg_dt.strftime("%Y-%m-%dT%H:%M:%S"), "WCS time zero point")

    if as_rate:
        hdr["BUNIT"] = ("s-1", "Counts per second per (x,y) bin")
        hdr["BNAME"] = (bname if bname else "Counts rate 2D hist", "Human-readable name")
    else:
        hdr["BUNIT"] = ("count", "Counts per (x,y) bin")
        hdr["BNAME"] = (bname if bname else "Counts 2D hist", "Human-readable name")
    hdr["BTYPE"] = (btype, "Data content type")

    # Instrument / origin
    if meta.mission:
        hdr["MISSION"] = (meta.mission, "Mission")
    if meta.observatory:
        hdr["OBSRVTRY"] = (meta.observatory, "Observatory")
    hdr["TELESCOP"] = (meta.telescope, "Telescope")
    hdr["INSTRUME"] = (meta.instrument, "Instrument")
    if meta.detector:
        hdr["DETECTOR"] = (meta.detector, "Detector")
    if meta.filter_name:
        hdr["FILTER"] = (meta.filter_name, "Filter")
    hdr["OBSERVER"] = (meta.observer, "Operator")
    if meta.obs_mode:
        hdr["OBS_MODE"] = (meta.obs_mode, "Mode string")
    if meta.point_id:
        hdr["POINT_ID"] = (meta.point_id, "Grouping id")

    hdr["COMMENT"] = (
        f"Cube axes: (time,y,x) with bins {bin_minutes} min, y_bins={y_bins}, x_bins={x_bins}"
    )
    hdr["HISTORY"] = f"Binned from event stream using {x_col}/{y_col}."
    if extra_history:
        for line in extra_history:
            hdr["HISTORY"] = line

    # Primary Obs-HDU
    hdu_obs = fits.PrimaryHDU(data=cube, header=hdr)

    # Bin edges table (exact edges = truth source)
    cols = [
        fits.Column(
            name="TIME_EDGES_S", format=f"{len(time_edges)}D", array=time_edges[np.newaxis, :]
        ),
        fits.Column(name="X_EDGES_DEG", format=f"{len(x_edges)}D", array=x_edges[np.newaxis, :]),
        fits.Column(name="Y_EDGES_DEG", format=f"{len(y_edges)}D", array=y_edges[np.newaxis, :]),
    ]
    hdu_bins = fits.BinTableHDU.from_columns(cols, name="BINS")
    hdu_bins.header["COMMENT"] = f"Time step {bin_minutes} min; edges define pixel centers & widths"

    fits.HDUList([hdu_obs, hdu_bins]).writeto(filename, overwrite=True)
    return filename
