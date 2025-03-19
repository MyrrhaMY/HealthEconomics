import math

import deampy.random_variates as rvgs
import numpy as np
import scipy.stats as stat

import input_data as data
from param_classes import Therapies


class Parameters:
    """ class to include parameter information to simulate the model """

    def __init__(self, therapy):

        self.therapy = therapy              # selected therapy
        self.initialHealthState = data.HealthStates.WELL     # initial health state
        self.annualTreatmentCost = 0        # annual treatment cost
        self.probMatrix = []                # transition probability matrix of the selected therapy
        self.annualStateCosts = []          # annual state costs
        self.annualStateUtilities = []      # annual state utilities
        self.discountRate = data.DISCOUNT   # discount rate


class ParameterGenerator:
    """ class to generate parameter values from the selected probability distributions """

    def __init__(self, therapy):

        self.therapy = therapy
        self.probMatrixRVG = []     # list of dirichlet distributions for transition probabilities
        #self.lnRelativeRiskRVG = None  # normal distribution for the natural log of the treatment relative risk
        self.annualStateCostRVGs = []  # list of gamma distributions for the annual cost of states
        self.annualStateUtilityRVGs = []  # list of beta distributions for the annual utility of states
        self.annualSemaglutideCostRVG = None   # gamma distribution for the cost of Semaglutide
        self.annualTirzepatideCostRVG = None   # gamma distribution for the cost of lamivudine

        # create Dirichlet distributions for transition probabilities
        for row in data.TRANS_PROB_MATRIX:
            # note:  for a Dirichlet distribution all values of the argument 'a' should be non-zero.
            # setting if_ignore_0s to True allows the Dirichlet distribution to take 'a' with zero values.
            self.probMatrixRVG.append(
                rvgs.Dirichlet(a=row, if_ignore_0s=True))

        # treatment relative risk
        #rr_ci = [0.365, 0.71]  # confidence interval of the treatment relative risk

        # find the mean and st_dev of the normal distribution assumed for ln(RR)
        # sample mean ln(RR)
        #mean_ln_rr = math.log(data.TREATMENT_RR)
        # sample standard deviation of ln(RR)
        #std_ln_rr = \
        #    (math.log(rr_ci[1]) - math.log(rr_ci[0])) / (2 * stat.norm.ppf(1 - 0.05 / 2))
        # create a normal distribution for ln(RR)
        #self.lnRelativeRiskRVG = rvgs.Normal(loc=mean_ln_rr, scale=std_ln_rr)

        # create gamma distributions for annual state cost
        for cost in data.ANNUAL_STATE_COST:

            # if cost is zero, add a constant 0, otherwise add a gamma distribution
            if cost == 0:
                self.annualStateCostRVGs.append(rvgs.Constant(value=0))
            else:
                # find shape and scale of the assumed gamma distribution
                # no data available to estimate the standard deviation, so we assumed st_dev=cost / 5
                fit_output = rvgs.Gamma.fit_mm(mean=cost, st_dev=cost / 5)
                # append the distribution
                self.annualStateCostRVGs.append(
                    rvgs.Gamma(shape=fit_output["shape"], loc=0, scale=fit_output["scale"]))

        # create a gamma distribution for annual treatment cost with each drug
        # first fit the gamma distribution to the cost of each drug
        fit_output_sema = rvgs.Gamma.fit_mm(mean=data.Semaglutide_COST, st_dev=data.Semaglutide_COST / 5)
        fit_output_tirz = rvgs.Gamma.fit_mm(mean=data.Tirzepatide_COST, st_dev=data.Tirzepatide_COST / 5)

        # then create the gamma distribution for the cost of each drug
        self.annualSemaglutideCostRVG = rvgs.Gamma(shape=fit_output_sema["shape"], loc=0, scale=fit_output_sema["scale"])
        self.annualTirzepatideCostRVG = rvgs.Gamma(shape=fit_output_tirz["shape"], loc=0, scale=fit_output_tirz["scale"])

        # create beta distributions for annual state utility
        if self.therapy == Therapies.SEMA:
            for utility in data.ANNUAL_STATE_UTILITY_SEMA:
                # if utility is zero, add a constant 0, otherwise add a beta distribution
                if utility <= 0 or utility >= 1:
                    self.annualStateUtilityRVGs.append(rvgs.Constant(value=0))
                else:
                    # find alpha and beta of the assumed beta distribution
                    # no data available to estimate the standard deviation, so we assumed st_dev=cost / 4
                    fit_output = rvgs.Beta.fit_mm(mean=utility, st_dev=utility /4)     # changed /4 to *0.1
                    # append the distribution
                    self.annualStateUtilityRVGs.append(
                        rvgs.Beta(a=fit_output["a"], b=fit_output["b"]))

        if self.therapy == Therapies.TIRZ:
            for utility in data.ANNUAL_STATE_UTILITY_TIRZ:
                # if utility is zero, add a constant 0, otherwise add a beta distribution
                if utility == 0 or utility >= 1:
                    self.annualStateUtilityRVGs.append(rvgs.Constant(value=0))
                else:
                    # find alpha and beta of the assumed beta distribution
                    # no data available to estimate the standard deviation, so we assumed st_dev=cost / 4
                    fit_output = rvgs.Beta.fit_mm(mean=utility, st_dev=utility /4)       # changed /4 to *0.1
                    # append the distribution

                    self.annualStateUtilityRVGs.append(
                        rvgs.Beta(a=fit_output["a"], b=fit_output["b"]))

    def get_new_parameters(self, seed):
        """
        :param seed: seed for the random number generator used to a sample of parameter values
        :return: a new parameter set
        """

        rng = np.random.RandomState(seed=seed)

        # create a parameter set
        param = Parameters(therapy=self.therapy)

        # calculate transition probabilities
        #prob_matrix = []    # probability matrix without background mortality added
        # for all health states
        # for s in data.HealthStates:
        #     # if this state is not diabetes
        #     if s != data.HealthStates.DIAB:
        #         # sample from the dirichlet distribution to find the transition probabilities between states
        #         # fill in the transition probabilities out of this state
        #         prob_matrix.append(self.probMatrixRVG[s.value].sample(rng))

        # sampled relative risk
        #rr = math.exp(self.lnRelativeRiskRVG.sample(rng))

        # calculate transition probabilities between states
        if self.therapy == Therapies.SEMA:
            # calculate transition probability matrix for the semaglutide therapy
            param.probMatrix = data.TRANS_PROB_MATRIX

        elif self.therapy == Therapies.TIRZ:
            # calculate transition probability matrix for the tirzepatide therapy
            param.probMatrix = data.TRANS_PROB_MATRIX

        # sample from gamma distributions that are assumed for annual state costs
        for dist in self.annualStateCostRVGs:
            param.annualStateCosts.append(dist.sample(rng))

        # sample from gamma distributions that are assumed for annual treatment costs
        sema_cost = self.annualSemaglutideCostRVG.sample(rng)
        tirz_cost = self.annualTirzepatideCostRVG.sample(rng)

        # calculate the annual treatment cost
        if self.therapy == Therapies.SEMA:
            param.annualTreatmentCost = sema_cost
        elif self.therapy == Therapies.TIRZ:
            param.annualTreatmentCost = sema_cost + tirz_cost

        # sample from beta distributions that are assumed for annual state utilities
        for dist in self.annualStateUtilityRVGs:
            param.annualStateUtilities.append(dist.sample(rng))

        # return the parameter set
        return param