# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd



def _hrv_sanitize_input(peaks=None, sampling_rate=None, ecg_rate=None):

    if isinstance(peaks, tuple):
        peaks = _hrv_sanitize_tuple(peaks)
    elif isinstance(peaks, (dict, pd.DataFrame)):
        peaks = _hrv_sanitize_dict_or_df(peaks)
    else:
        peaks = _hrv_sanitize_peaks(peaks)

    return peaks









# =============================================================================
# Internals
# =============================================================================
def _hrv_sanitize_tuple(peaks):

    if isinstance(peaks[0], (dict, pd.DataFrame)):
        try:
            peaks = _hrv_sanitize_dict_or_df(peaks[0])
        except NameError:
            if isinstance(peaks[1], (dict, pd.DataFrame)):
                try:
                    peaks = _hrv_sanitize_dict_or_df(peaks[1])
                except NameError:
                    peaks = _hrv_sanitize_peaks(peaks[1])
            else:
                peaks = _hrv_sanitize_peaks(peaks[0])
    return peaks


def _hrv_sanitize_dict_or_df(peaks):

    # Get columns
    if isinstance(peaks, dict):
        cols = np.array(list(peaks.keys()))
    elif isinstance(peaks, pd.DataFrame):
        cols = peaks.columns.values

    cols = cols[["Peak" in s for s in cols]]

    if len(cols) > 1:
        cols = cols[[("ECG" in s) or ("PPG" in s) for s in cols]]

    if len(cols) == 0:
        raise NameError("NeuroKit error: hrv(): Wrong input, ",
                        "we couldn't extract R-peak indices. ",
                        "You need to provide a list of R-peak indices.")

    peaks = _hrv_sanitize_peaks(peaks[cols[0]])

    return peaks



def _hrv_sanitize_peaks(peaks):

    if isinstance(peaks, pd.Series):
        peaks = peaks.values

    if len(np.unique(peaks)) == 2:
        if np.all(np.unique(peaks) == np.array([0, 1])):
            peaks = np.where(peaks == 1)[0]

    if isinstance(peaks, list):
        peaks = np.array(peaks)

    return peaks