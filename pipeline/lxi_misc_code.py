import logging
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")

# Check if the log folder exists. If not, create it
Path("../log").mkdir(parents=True, exist_ok=True)

file_handler = logging.FileHandler("../log/lxi_misc_codes.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def PinPullerTemp_func(vpc, hk_value, lxi_unit):
    PinPullerTemp = (hk_value * vpc - 2.73) * 100
    return PinPullerTemp


def OpticsTemp_func(vpc, hk_value, lxi_unit):
    OpticsTemp = (hk_value * vpc - 2.73) * 100
    return OpticsTemp


def LEXIbaseTemp_func(vpc, hk_value, lxi_unit):
    LEXIbaseTemp = (hk_value * vpc - 2.73) * 100
    return LEXIbaseTemp


def HVsupplyTemp_func(vpc, hk_value, lxi_unit):
    HVsupplyTemp = (hk_value * vpc - 2.73) * 100
    return HVsupplyTemp


def V_Imon_5_2_func(vpc, hk_value, lxi_unit):
    if lxi_unit == 1:
        V_Imon_5_2 = (hk_value * vpc) * 1e3 / 18
    elif lxi_unit == 2:
        V_Imon_5_2 = (hk_value * vpc - 1.129) * 1e3 / 21.456
    else:
        V_Imon_5_2 = (hk_value * vpc) * 1e3 / 18
    return V_Imon_5_2


def V_Imon_10_func(vpc, hk_value, lxi_unit):
    V_Imon_10 = hk_value * vpc
    return V_Imon_10


def V_Imon_3_3_func(vpc, hk_value, lxi_unit):
    if lxi_unit == 1:
        V_Imon_3_3 = (hk_value * vpc + 0.0178) * 1e3 / 9.131
    elif lxi_unit == 2:
        V_Imon_3_3 = (hk_value * vpc - 0.029) * 1e3 / 18
    else:
        V_Imon_3_3 = (hk_value * vpc + 0.0178) * 1e3 / 9.131
    return V_Imon_3_3


def AnodeVoltMon_func(vpc, hk_value, lxi_unit):
    AnodeVoltMon = hk_value * vpc
    return AnodeVoltMon


def V_Imon_28_func(vpc, hk_value, lxi_unit):
    if lxi_unit == 1:
        V_Imon_28 = (hk_value * vpc + 0.00747) * 1e3 / 17.94
    elif lxi_unit == 2:
        V_Imon_28 = (hk_value * vpc + 0.00747) * 1e3 / 17.94
    else:
        V_Imon_28 = (hk_value * vpc + 0.00747) * 1e3 / 17.94
    return V_Imon_28


def ADC_Ground_func(vpc, hk_value, ADC_Ground):
    ADC_Ground = hk_value * vpc
    return ADC_Ground


def Cmd_count_func(vpc, hk_value, lxi_unit):
    Cmd_count = hk_value
    return Cmd_count


def Pinpuller_Armed_func(vpc, hk_value, lxi_unit):
    Pinpuller_Armed = hk_value
    return Pinpuller_Armed


def Unused1_func(vpc, hk_value, lxi_unit):
    Unused1 = hk_value
    return Unused1


def Unused2_func(vpc, hk_value, lxi_unit):
    Unused2 = hk_value
    return Unused2


def HVmcpAuto_func(vpc, hk_value, lxi_unit):
    HVmcpAuto = hk_value * vpc
    return HVmcpAuto


def HVmcpMan_func(vpc, hk_value, lxi_unit):
    HVmcpMan = hk_value * vpc
    return HVmcpMan


def hk_value_comp(ii=None, vpc=None, hk_value=None, hk_id=None, lxi_unit=None):
    ops = {
        "0": PinPullerTemp_func,
        "1": OpticsTemp_func,
        "2": LEXIbaseTemp_func,
        "3": HVsupplyTemp_func,
        "4": V_Imon_5_2_func,
        "5": V_Imon_10_func,
        "6": V_Imon_3_3_func,
        "7": AnodeVoltMon_func,
        "8": V_Imon_28_func,
        "9": ADC_Ground_func,
        "10": Cmd_count_func,
        "11": Pinpuller_Armed_func,
        "12": Unused1_func,
        "13": Unused2_func,
        "14": HVmcpAuto_func,
        "15": HVmcpMan_func,
    }
    chosen_func = ops.get(str(hk_id))
    if chosen_func is None:
        raise ValueError(f"No function found for hk_id {hk_id}")
    return chosen_func(vpc, hk_value, lxi_unit)
