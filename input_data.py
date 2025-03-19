from enum import Enum

# simulation settings
POP_SIZE = 2000         # cohort population size
SIM_TIME_STEPS = 50    # length of simulation (years)
ALPHA = 0.05        # significance level for calculating confidence intervals
DISCOUNT = 0.03     # annual discount rate


class HealthStates(Enum):
    """ health states of patients with HIV """
    WELL = 0
    PRE_DIAB = 1
    DIAB = 2


# transition matrix
TRANS_PROB_MATRIX = [
    [0.837, 0.163, 0],   # WELL
    [0.162, 0.775, 0.063],   # PRE_DIAB
    [0, 0.005, 0.995]   # DIAB
    ]

# annual cost of each health state
ANNUAL_STATE_COST = [
    0,     # WELL
    1500,     # PRE-DIAB
    5000,     # DIAB
    ]

tirz_utility = 0.75

# annual health utility of each health state
ANNUAL_STATE_UTILITY_SEMA = [
    1,     # WELL
    0.9,   # PRE-DIAB
    0.68,  # DIAB
    ]


ANNUAL_STATE_UTILITY_TIRZ = [
    1,     # WELL
    0.9,   # PRE-DIAB
    tirz_utility,  # DIAB
    ]


# annual drug costs
Semaglutide_COST = 11597 #status quo
Tirzepatide_COST = 12666
