import numpy as np
import pandas as pd

EPS = 1e-9

def intermediates(p1, p2, d1, d2):
    """Return a list of equally spaced points between p1 and p2 with the range of d2 to d1 (days)"""
    # between p1 and p2
    nb_days = d2 - d1
    price_spacing = (p2 - p1) / nb_days

    return [(p1 + i * price_spacing) for i in range(nb_days)]


def intermediates_signal(price, marks):
    """Return a signal created from list of marks index on the certain price"""
    if isinstance(marks, list):
        marks = np.asarray(marks)
    signal = np.empty(price.shape[0])
    signal[:] = np.nan
    for i in range(marks.shape[0]-1):
        signal[marks[i]:marks[i+1]] = intermediates(price[marks[i]], price[marks[i+1]], marks[i], marks[i+1])

    signal[marks[-1]] = price[marks[-1]]
    return signal


def almost_between(value, target, tol=0.05):
    return (target - tol <= value <= target + tol)


def horizental_line(price, idx, ratio = -1, param = 75):

    signal = np.empty(price.shape[0])
    signal[:] = np.nan
    nxt = price.shape[0]-idx if (idx + param > price.shape[0]) else param
    prv = idx if (idx - param < 0) else param
    value = price[idx] if (ratio == -1) else ratio
    signal[idx-prv:idx+nxt] = np.ones(prv+nxt)*value

    signal_ratio = np.empty(price.shape[0])
    signal_ratio[:] = np.nan
    if (idx + param + 1 < price.shape[0]):
        signal_ratio[idx+nxt] = np.ones(1)*value
    else:
        signal_ratio[idx-prv-1] = np.ones(1)*value

    return [signal, signal_ratio]


def df_empty(columns, dtypes, index=None):
    assert len(columns)==len(dtypes)
    df = pd.DataFrame(index=index)
    for c,d in zip(columns, dtypes):
        df[c] = pd.Series(dtype=d)
    return df


def intersection(x1,y1,x2,y2,x3,y3,x4,y4):
    """two lines given by (x1,y1)->(x2,y2), (x3,y3)->(x4,y4) (xr, yr) is the intersection point return (None,None) if two lines are parallel"""
    d = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
    if abs(d) < EPS: return None,None
    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / d
    xr = x1 + (x2 - x1) * ua
    yr = y1 + (y2 - y1) * ua
    return xr, yr


def check_subitem_in_list(list_items:list, sub_item) -> bool:
    if len([item for item in list_items if sub_item in item]) == 0:
        return False
    return True


def remove_subitem_in_list(list_items:list, sub_item) -> list:
    new_list = [j for j in list_items if sub_item not in j]
    return new_list


def df2list(df_mw:pd.DataFrame) -> list:
    return [df_mw.iloc[i] for i in range(len(df_mw))]