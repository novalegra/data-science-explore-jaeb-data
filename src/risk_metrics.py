import numpy as np

def get_bgri(bg_df):
    # Calculate LBGI and HBGI using equation from
    # Clarke, W., & Kovatchev, B. (2009)
    bgs = bg_df.copy()
    bgs[bgs < 1] = 1  # this is added to take care of edge case BG <= 0
    transformed_bg = 1.509 * ((np.log(bgs) ** 1.084) - 5.381)
    risk_power = 10 * (transformed_bg) ** 2
    low_risk_bool = transformed_bg < 0
    high_risk_bool = transformed_bg > 0
    rlBG = risk_power * low_risk_bool
    rhBG = risk_power * high_risk_bool
    LBGI = np.mean(rlBG)
    HBGI = np.mean(rhBG)
    BGRI = LBGI + HBGI

    return LBGI, HBGI, BGRI


def lbgi_risk_score(lbgi):
    if lbgi > 10:
        risk = 4
    elif lbgi > 5:
        risk = 3
    elif lbgi > 2.5:
        risk = 2
    elif lbgi > 0:
        risk = 1
    else:
        risk = 0
    return risk


def hbgi_risk_score(hbgi):
    if hbgi > 18:
        risk = 4
    elif hbgi > 9:
        risk = 3
    elif hbgi > 4.5:
        risk = 2
    elif hbgi > 0:
        risk = 1
    else:
        risk = 0
    return risk


def get_steady_state_iob_from_sbr(sbr):
    return sbr * 2.111517


def get_dka_risk_hours(iob_array, sbr):
    steady_state_iob = get_steady_state_iob_from_sbr(sbr)

    fifty_percent_steady_state_iob = steady_state_iob / 2

    indices_with_less_50percent_sbr_iob = iob_array < fifty_percent_steady_state_iob

    hours_with_less_50percent_sbr_iob = np.sum(indices_with_less_50percent_sbr_iob) * 5 / 60

    return hours_with_less_50percent_sbr_iob


def dka_risk_score(hours_with_less_50percent_sbr_iob):
    if hours_with_less_50percent_sbr_iob >= 21:
        risk = 4
    elif hours_with_less_50percent_sbr_iob >= 14:
        risk = 3
    elif hours_with_less_50percent_sbr_iob >= 8:
        risk = 2
    elif hours_with_less_50percent_sbr_iob >= 2:
        risk = 1
    else:
        risk = 0
    return risk
