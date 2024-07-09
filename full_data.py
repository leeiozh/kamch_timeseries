from lib import *
from glob import glob

filenames = glob("*.txt")
filenames.sort()
filenames = filenames[4:]

for name in filenames:
    print(name)
    time, level = read_txt_file(name)
    level = ave_outliers(level, 0.5)
    level[level > 2 * np.median(level)] = np.NAN

    time_str = [dt.fromtimestamp(tt) for tt in time]
    plt.plot(time_str, level)
    plt.show()
    tim_spl, lev_spl = split_holes(time, level, 24 * 3600)
    print(len(tim_spl))
    i = 0
    for s in range(len(tim_spl)):
        if len(tim_spl[s]) > 30 * 24 * 60:
            try:
                plt.plot(tim_spl[s], lev_spl[s])
                plt.show()
                analyze(tim_spl[s], lev_spl[s], name[:-5], True, False, i)
            except ValueError:
                continue
            i += 1

    # plt.plot(time, level)
    # plt.show()
