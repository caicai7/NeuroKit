# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

from ..signal import signal_phase
from .ecg_peaks import ecg_peaks
from .ecg_delineate import ecg_delineate



def ecg_phase(ecg_cleaned, rpeaks=None, delineate_info=None, method='peak', sampling_rate=None):
    """Compute cardiac phase (for both atrial and ventricular).

    Finds the cardiac phase, labelled as 1 for systole and 0 for diastole.
    Parameters
    ----------
    rpeaks : list, array, DataFrame, Series or dict
        The samples at which the different ECG peaks occur. If a dict or a
        DataFrame is passed, it is assumed that these containers were obtained
        with `ecg_findpeaks()` or `ecg_peaks()`.
    delineate_info : dict
        A dictionary containing additional information of ecg delineation and
        can be obtained with `ecg_delineate()`.

    Returns
    -------
    signals : DataFrame
        A DataFrame of same length as `ecg_signal` containing the following
        columns:

        - *"ECG_Phase_Atrial"*: cardiac phase, marked by "1" for systole
          and "0" for diastole.
        - *"ECG_Phase_Atrial_Completion"*: cardiac phase (atrial) completion,
          expressed in percentage (from 0 to 1), representing the stage of the
          current cardiac phase.
        - *"ECG_Phase_Ventricular"*: cardiac phase, marked by "1" for systole
          and "0" for diastole.
        - *"ECG_Phase_Ventricular_Completion"*: cardiac phase (ventricular)
          completion, expressed in percentage (from 0 to 1), representing the
          stage of the current cardiac phase.

    See Also
    --------
    ecg_clean, ecg_peaks, ecg_process, ecg_plot

    Examples
    --------
    >>> import neurokit2 as nk
    >>>
    >>> ecg = nk.ecg_simulate(duration=10, sampling_rate=1000)
    >>> cleaned = nk.ecg_clean(ecg, sampling_rate=1000)
    >>> _, rpeaks = nk.ecg_peaks(cleaned)
    >>> signals, waves = nk.ecg_delineate(cleaned, rpeaks, sampling_rate=1000)
    >>>
    >>> cardiac_phase = nk.ecg_phase(ecg_cleaned=cleaned,
    >>>                              rpeaks=rpeaks,
    >>>                              delineate_info=waves,
    >>>                              sampling_rate=1000)
    >>> nk.signal_plot([cleaned, cardiac_phase], standardize=True)
    """
    # Sanitize inputs
    if rpeaks is None:
        if sampling_rate is not None:
            _, rpeaks = ecg_peaks(ecg_cleaned, sampling_rate=sampling_rate)
        else:
            raise ValueError("rpeaks will be obtained using `nk.ecg_peaks`. "
                             "Please provide the sampling_rate of "
                             "ecg_signal.")
    # Try retrieving right column
    if isinstance(rpeaks, dict):
        rpeaks = rpeaks["ECG_R_Peaks"]

    if delineate_info is None:
        signals, delineate_info = ecg_delineate(ecg_cleaned, sampling_rate=sampling_rate, method=method)

    # Try retrieving right column
    if isinstance(delineate_info, dict):
        toffsets = delineate_info['ECG_T_Offsets']
        toffsets = [int(x) for x in toffsets if ~np.isnan(x)]
        toffsets = np.array(toffsets)

        ppeaks = delineate_info['ECG_P_Peaks']
        ppeaks = [int(x) for x in ppeaks if ~np.isnan(x)]
        ppeaks = np.array(ppeaks)




    # Atrial Phase
    atrial = np.full(len(ecg_cleaned), np.nan)
    atrial[rpeaks] = 0.0
    atrial[ppeaks] = 1.0

    last_element = np.where(~np.isnan(atrial))[0][-1]  # Avoid filling beyond the last peak/trough
    atrial[0:last_element] = pd.Series(atrial).fillna(method="ffill").values[0:last_element]

    # Atrial Phase Completion
    atrial_completion = signal_phase(atrial, method="percent")




    # Ventricular Phase
    ventricular = np.full(len(ecg_cleaned), np.nan)
    ventricular[toffsets] = 0.0
    ventricular[rpeaks] = 1.0

    last_element = np.where(~np.isnan(ventricular))[0][-1]  # Avoid filling beyond the last peak/trough
    ventricular[0:last_element] = pd.Series(ventricular).fillna(method="ffill").values[0:last_element]

    # Ventricular Phase Completion
    ventricular_comletion = signal_phase(ventricular, method="percent")



    out = pd.DataFrame({"ECG_Phase_Atrial": atrial,
                        "ECG_Phase_Atrial_Completion": atrial_completion,
                        "ECG_Phase_Ventricular": ventricular,
                        "ECG_Phase_Ventricular_Completion": ventricular_comletion})

    return out
