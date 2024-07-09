import numpy as np
from datetime import datetime as dt
import ttide as tt
import matplotlib.pyplot as plt
import pandas as pd


def ave_outliers(arr, ttrr=0.5):
    """
    averaging outliers
    :param arr: input 1D array
    :param ttrr: allowed emission value in meters
    :return: input array without outliers
    """
    ser = pd.Series(arr)
    rol_med = ser.rolling(window=15, center=True).median()
    outs = (ser - rol_med).abs() > ttrr
    ser[outs] = rol_med[outs]
    ser.fillna(method='bfill', inplace=True)
    ser.fillna(method='ffill', inplace=True)
    return ser.to_numpy()


def split_holes(times, arr, gap):
    """
    splitting input array on a pack of arrays with gaps not more than gap
    :param times: array of times
    :param arr: array of data
    :param gap: allowed gap in seconds
    :return:
    """
    diffs = np.diff(times)
    gap_ind = np.where(diffs > gap)[0] + 1
    spl_times = np.split(times, gap_ind)
    spl_arr = np.split(arr, gap_ind)
    return spl_times, spl_arr


def read_xlsx_file(name):
    data = pd.read_excel(name)
    time = np.zeros(data.shape[0])
    level = np.zeros(data.shape[0])
    for j in range(data.shape[0]):
        time[j] = data["Время"].at[j].timestamp()
        level[j] = data["Уровень"].at[j]
    level[level < 0] = np.NAN
    return time, level


def read_txt_file(name):
    """
    reading input file to two arrays
    :param name: name of file
    :return: array of times and array of sea level according times
    """
    data = np.loadtxt(name, delimiter=",")
    time = np.zeros(data.shape[0])
    level = np.zeros(data.shape[0])
    for j in range(data.shape[0]):
        time[j] = dt(year=int(data[j, 0]), month=int(data[j, 1]), day=int(data[j, 2]), hour=int(data[j, 3]),
                     minute=int(data[j, 4])).timestamp()
        level[j] = data[j, -1]
    return time, level


def analyze(tim, arr, name, plot=True, ret=False, num=0):
    """
    analyzing sea level data
    :param tim: array of times
    :param arr: array of sea level data
    :param name: name of png file for saving
    :param plot: plot or not
    :param ret: return smth or not
    :param num: additional index for file name
    :return: (if flag) array of datetimes since start of meas., sea level excluding tides, high frequency component
    """
    t_start = tim[0]  # start time
    anom = arr - arr.mean()  # exclude mean level
    tim -= tim[0]
    time_i = np.arange(0, (tim[-1] - tim[0]) / 60, 1)  # time in minutes (so 1 element = 1 step of discretization)
    time_str = [dt.fromtimestamp(ttt * 60 + t_start) for ttt in time_i]  # time for ax labeling
    anom_i = np.interp(time_i, (tim - tim[0]) / 60, anom)  # interpolating data on regular grid

    res = tt.t_tide(anom_i, dt=1. / 60, lat=54, stime=dt.fromtimestamp(t_start))  # calculating tides 55.197903
    tides = res["xout"].squeeze()
    anom_ex_tides = anom_i - tides  # excluding tides
    anom_ave = np.convolve(anom_ex_tides, np.ones(180) / 180, mode='same')  # averaging with 3-h window

    if plot:
        fig, ax = plt.subplots(5, 1, figsize=(8, 8))
        ax[0].plot(time_str, anom_i)
        ax[1].plot(time_str, tides)
        ax[2].plot(time_str, anom_ex_tides)
        ax[3].plot(time_str, anom_ave)
        ax[3].plot([time_str[0], time_str[-1]], [0, 0])
        ax[3].plot([time_str[0], time_str[-1]], [0.5, 0.5])
        ax[3].plot([time_str[0], time_str[-1]], [-0.5, -0.5])
        ax[4].plot(time_str, anom_ex_tides - anom_ave)
        plt.savefig("new_f_" + name + "_" + str(num) + "_" + time_str[0].strftime("%y%m%d") + ".png",
                    dpi=300, bbox_inches="tight")
        plt.show()

    if ret:
        return np.array([ttt * 60 + t_start for ttt in time_i]), anom_ex_tides, anom_ex_tides - anom_ave