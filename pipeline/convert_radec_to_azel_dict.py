import datetime
import glob
from functools import lru_cache

import numpy as np
import pandas as pd
import pytz
from dateutil import parser
from matplotlib import pyplot as plt


def quaternion_to_rotation_matrix(q: np.ndarray) -> np.ndarray:
    """Single quaternion [q0,q1,q2,q3] -> 3x3 rotation matrix."""
    q0, q1, q2, q3 = q
    R = np.empty((3, 3), dtype=float)
    R[0, 0] = q0 * q0 + q1 * q1 - q2 * q2 - q3 * q3
    R[0, 1] = 2 * (q1 * q2 + q0 * q3)
    R[0, 2] = 2 * (q1 * q3 - q0 * q2)
    R[1, 0] = 2 * (q1 * q2 - q0 * q3)
    R[1, 1] = q0 * q0 - q1 * q1 + q2 * q2 - q3 * q3
    R[1, 2] = 2 * (q2 * q3 + q0 * q1)
    R[2, 0] = 2 * (q1 * q3 + q0 * q2)
    R[2, 1] = 2 * (q2 * q3 - q0 * q1)
    R[2, 2] = q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3
    return R


@lru_cache(maxsize=2)
def _load_quaternion_df(quaternion_type: str) -> pd.DataFrame:
    folder = "../data/quaternions/"
    all_files = sorted(glob.glob(folder + "*.csv"))
    if quaternion_type not in {"actual", "nominal"}:
        raise ValueError("quaternion_type must be 'actual' or 'nominal'")
    picks = [
        f for f in all_files if ("Actual" in f if quaternion_type == "actual" else "Nominal" in f)
    ]
    if not picks:
        raise FileNotFoundError(f"No CSV found for quaternion_type='{quaternion_type}' in {folder}")
    df = pd.read_csv(picks[0], index_col=None)
    if "Epoch_MJD" in df.columns:
        df = df.drop(columns=["Epoch_MJD"])
    # Ensure UTC, strip sub-ms if present
    dt = pd.to_datetime(df["Epoch_UTC"].astype(str).str.slice(0, -3), format="mixed", utc=True)
    df = df.drop(columns=["Epoch_UTC"]).set_index(dt).sort_index()
    # Ensure columns are in [q0,q1,q2,q3] order
    cols = [c for c in df.columns if c.lower().startswith("q")]
    if len(cols) != 4:
        raise ValueError("Quaternion CSV must have 4 quaternion columns (q0..q3).")
    return df[cols].astype(float)


def _normalize_epoch(epoch_value):
    if isinstance(epoch_value, str):
        ts = parser.parse(epoch_value)
        ts = ts if ts.tzinfo is not None else ts.replace(tzinfo=pytz.UTC)
        return pd.Timestamp(ts).tz_convert("UTC")
    if isinstance(epoch_value, datetime.datetime):
        ts = epoch_value if epoch_value.tzinfo is not None else epoch_value.replace(tzinfo=pytz.UTC)
        return pd.Timestamp(ts).tz_convert("UTC")
    if isinstance(epoch_value, np.datetime64):
        return pd.to_datetime(epoch_value, utc=True)
    if isinstance(epoch_value, pd.Timestamp):
        return (
            epoch_value.tz_localize("UTC")
            if epoch_value.tzinfo is None
            else epoch_value.tz_convert("UTC")
        )
    if isinstance(epoch_value, pd.DatetimeIndex):
        t0 = epoch_value[0]
        t0 = t0.tz_localize("UTC") if t0.tzinfo is None else t0.tz_convert("UTC")
        return t0
    raise TypeError(f"Unsupported epoch_value type: {type(epoch_value)!r}")


def rotation_matrices_from_epoch(epoch_value, quaternion_type="nominal") -> np.ndarray:
    """Return (R_b_nominal_J2000, R_J2000_b_nominal) at closest time within ±5 min."""
    df = _load_quaternion_df(quaternion_type)
    if epoch_value is None:
        q = df.iloc[0].values
    else:
        t = _normalize_epoch(epoch_value)
        idx = df.index.get_indexer([t], method="nearest", tolerance=pd.Timedelta("5min"))[0]
        if idx == -1:
            raise ValueError(f"No quaternion within 5 minutes of {t.isoformat()}")
        q = df.iloc[idx].values
    R_b_nominal_J2000 = quaternion_to_rotation_matrix(q)
    return R_b_nominal_J2000


def radec_to_azel_grid(
    ra_grid: np.ndarray, dec_grid: np.ndarray, epoch, quaternion_type: str = "nominal", R_b_nominal_J2000: np.ndarray = None
) -> tuple[np.ndarray, np.ndarray]:
    """Vectorized RA/Dec→Az/El for entire grid; also returns inverse result."""
    if R_b_nominal_J2000 is None:
        R_b_nominal_J2000 = rotation_matrices_from_epoch(epoch, quaternion_type)

    ra = np.deg2rad(ra_grid)
    dec = np.deg2rad(dec_grid)

    cosd = np.cos(dec)
    X = np.stack([np.cos(ra) * cosd, np.sin(ra) * cosd, np.sin(dec)], axis=0)  # (3, M, N)

    M, N = ra_grid.shape
    Xf = X.reshape(3, -1)

    Xb = (R_b_nominal_J2000 @ Xf).reshape(3, M, N)

    y, z = Xb[1], Xb[2]
    x = Xb[0]
    theta1 = np.degrees(np.arctan2(-y, z))
    theta2 = np.degrees(np.arcsin(x))
    az = (270.0 - theta1) % 360.0
    el = theta2

    return az, el


def radec_to_azel_grid_dict(
    data_dict: dict, epoch, quaternion_type: str = "nominal"
) -> dict:
    
    