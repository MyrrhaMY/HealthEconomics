from enum import Enum

import numpy as np

import input_data as data


class Therapies(Enum):
    """ mono vs. combination therapy """
    SEMA = 0
    TIRZ = 1


class Parameters:
    def __init__(self, therapy):

        # selected therapy
        self.therapy = therapy

        # initial health state
        self.initialHealthState = data.HealthStates.WELL

        # annual treatment cost
        if self.therapy == Therapies.SEMA:
            self.annualTreatmentCost = data.Semaglutide_COST
        else:
            self.annualTreatmentCost = data.Tirzepatide_COST

        # transition probability matrix of the selected therapy
        self.probMatrix = []

        # calculate transition probabilities between diabetes states
        if self.therapy == Therapies.SEMA:
            # calculate transition probability matrix for the semaglutide therapy
            self.probMatrix = data.TRANS_PROB_MATRIX

        elif self.therapy == Therapies.TIRZ:
            # calculate transition probability matrix for the tirzepatide therapy
            self.probMatrix = data.TRANS_PROB_MATRIX

        # annual state costs and utilities
        self.annualStateCosts = data.ANNUAL_STATE_COST
        if self.therapy == Therapies.SEMA:
            self.annualStateUtilities = data.ANNUAL_STATE_UTILITY_SEMA
        elif self.therapy == Therapies.TIRZ:
            self.annualStateUtilities = data.ANNUAL_STATE_UTILITY_TIRZ

        # discount rate
        self.discountRate = data.DISCOUNT

print("Transition probability matrix:", data.TRANS_PROB_MATRIX)
