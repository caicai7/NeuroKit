import neurokit2 as nk
import numpy as np


def test_hrv_time():
    ecg_slow = nk.ecg_simulate(duration=60, sampling_rate=1000, heart_rate=70, random_state=42)
    ecg_fast = nk.ecg_simulate(duration=60, sampling_rate=1000, heart_rate=110, random_state=42)

    _, peaks_slow = nk.ecg_process(ecg_slow, sampling_rate=1000)
    _, peaks_fast = nk.ecg_process(ecg_fast, sampling_rate=1000)

    hrv_slow = nk.hrv_time(peaks_slow, sampling_rate=1000)
    hrv_fast = nk.hrv_time(peaks_fast, sampling_rate=1000)
    
    assert hrv_fast["RMSSD"] < hrv_slow["RMSSD"]
    assert hrv_fast["MeanNN"] < hrv_slow["MeanNN"]
    assert hrv_fast["SDNN"] < hrv_slow["SDNN"]
    assert hrv_fast["CVNN"] < hrv_slow["CVNN"]
    assert hrv_fast["CVSD"] < hrv_slow["CVSD"]
    assert hrv_fast["MedianNN"] < hrv_slow["MedianNN"]
    assert hrv_fast["MadNN"] < hrv_slow["MadNN"]
    assert hrv_fast["MCVNN"] < hrv_slow["MCVNN"]
    assert hrv_fast["pNN50"] == hrv_slow["pNN50"]
    assert hrv_fast["pNN20"] < hrv_slow["pNN20"]
    assert hrv_fast["TINN"] < hrv_slow["TINN"]
    assert hrv_fast["HTI"] > hrv_slow["HTI"]


def test_hrv_frequency():
    # Test frequency domain
    ecg1 = nk.ecg_simulate(duration=60, sampling_rate=2000, heart_rate=70, random_state=42)
    _, peaks1 = nk.ecg_process(ecg1, sampling_rate=2000)
    hrv1 = nk.hrv_frequency(peaks1, sampling_rate=2000)

    ecg2 = nk.signal_resample(ecg1, sampling_rate=2000, desired_sampling_rate=500)
    _, peaks2 = nk.ecg_process(ecg2, sampling_rate=500)
    hrv2 = nk.hrv_frequency(peaks2, sampling_rate=500)

    assert np.allclose(hrv1["HF"] - hrv2["HF"], 0, atol=1.5)
    assert np.allclose(hrv1["LF"] - hrv2["LF"], 0, atol=1)
    assert np.allclose(hrv1["VLF"] - hrv2["VLF"], 0, atol=1)


def test_hrv_summary():
    
    ecg = nk.ecg_simulate(duration=60, sampling_rate=1000, heart_rate=110, random_state=42)

    _, peaks = nk.ecg_process(ecg, sampling_rate=1000)

    ecg_hrv = nk.hrv_summary(peaks, sampling_rate=1000)

    assert all(elem in ['HRV_RMSSD', 'HRV_MeanNN', 'HRV_SDNN', 'HRV_SDSD', 'HRV_CVNN',
                        'HRV_CVSD', 'HRV_MedianNN', 'HRV_MadNN', 'HRV_MCVNN',
                        'HRV_pNN50', 'HRV_pNN20', 'HRV_TINN', 'HRV_HTI', 'HRV_ULF',
                        'HRV_VLF', 'HRV_LF', 'HRV_HF', 'HRV_VHF', 'HRV_LFHF',
                        'HRV_LFn', 'HRV_HFn', 'HRV_LnHF',
                        'HRV_SD1', 'HRV_SD2', 'HRV_SD2SD1', 'HRV_CSI', 'HRV_CVI',
                        'HRV_CSI_Modified', 'HRV_SampEn']
               for elem in np.array(ecg_hrv.columns.values, dtype=str))