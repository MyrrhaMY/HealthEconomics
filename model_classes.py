import numpy as np

import deampy.econ_eval as econ
import deampy.statistics as stat
from deampy.markov import MarkovJumpProcess
from deampy.plots.sample_paths import PrevalencePathBatchUpdate
from input_data import HealthStates


class Patient:
    def __init__(self, id, parameters):
        """ initiates a patient
        :param id: ID of the patient
        :param parameters: an instance of the parameters class
        """
        self.id = id
        self.params = parameters
        self.stateMonitor = PatientStateMonitor(parameters=parameters)

    def simulate(self, n_time_steps):
        """ simulate the patient over the specified simulation length """

        # random number generator
        rng = np.random.RandomState(seed=self.id)
        # Markov jump process
        markov_jump = MarkovJumpProcess(transition_prob_matrix=self.params.probMatrix)

        k = 0  # simulation time step

        # while the patient is alive and simulation length is not yet reached
        while k < n_time_steps:
            # sample from the Markov jump process to get a new state
            # (returns an integer from {0, 1, 2, ...})
            new_state_index = markov_jump.get_next_state(
                current_state_index=self.stateMonitor.currentState.value,
                rng=rng)

            # update health state
            self.stateMonitor.update(time_step=k, new_state=HealthStates(new_state_index))

            # increment time
            k += 1


class PatientStateMonitor:
    """ to update patient outcomes (years survived, cost, etc.) throughout the simulation """
    def __init__(self, parameters):

        self.currentState = parameters.initialHealthState   # initial health state
        self.survivalTime = None      # survival time
        self.timeToDIAB = None        # time to develop DIAB
        # patient's cost and utility monitor
        self.costUtilityMonitor = PatientCostUtilityMonitor(parameters=parameters)

    def update(self, time_step, new_state):
        """
        update the current health state to the new health state
        :param time_step: current time step
        :param new_state: new state
        """

        # update survival time
        # if new_state == HealthStates.HIV_DEATH:
        #     self.survivalTime = time_step + 0.5  # corrected for the half-cycle effect

        # update time until DIAB
        if self.currentState != HealthStates.DIAB and new_state == HealthStates.DIAB:
            self.timeToDIAB = time_step + 0.5  # corrected for the half-cycle effect

        # update cost and utility
        self.costUtilityMonitor.update(k=time_step,
                                       current_state=self.currentState,
                                       next_state=new_state)

        # update current health state
        self.currentState = new_state


class PatientCostUtilityMonitor:

    def __init__(self, parameters):

        # model parameters for this patient
        self.params = parameters

        # total cost and utility
        self.totalDiscountedCost = 0
        self.totalDiscountedUtility = 0

    def update(self, k, current_state, next_state):
        """ updates the discounted total cost and health utility
        :param k: simulation time step
        :param current_state: current health state
        :param next_state: next health state
        """

        # update cost
        cost = 0.5 * (self.params.annualStateCosts[current_state.value] +
                      self.params.annualStateCosts[next_state.value])
        # update utility
        utility = 0.5 * (self.params.annualStateUtilities[current_state.value] +
                         self.params.annualStateUtilities[next_state.value])

        # add the cost of treatment
        # if HIV death will occur, add the cost for half-year of treatment
        if next_state == HealthStates.DIAB:
            cost += 0.5 * self.params.annualTreatmentCost
        else:
            cost += 1 * self.params.annualTreatmentCost

        # update total discounted cost and utility (corrected for the half-cycle effect)
        self.totalDiscountedCost += econ.pv_single_payment(payment=cost,
                                                           discount_rate=self.params.discountRate / 2,
                                                           discount_period=2 * k + 1)
        self.totalDiscountedUtility += econ.pv_single_payment(payment=utility,
                                                              discount_rate=self.params.discountRate / 2,
                                                              discount_period=2 * k + 1)


class Cohort:
    def __init__(self, id, pop_size, parameters):
        """ create a cohort of patients
        :param id: cohort ID
        :param pop_size: population size of this cohort
        :param parameters: parameters
        """
        self.id = id
        self.popSize = pop_size
        self.params = parameters
        self.cohortOutcomes = CohortOutcomes()  # outcomes of this simulated cohort

    def simulate(self, n_time_steps):
        """ simulate the cohort of patients over the specified number of time-steps
        :param n_time_steps: number of time steps to simulate the cohort
        """

        # populate and simulate the cohort
        for i in range(self.popSize):
            # create a new patient (use id * pop_size + n as patient id)
            patient = Patient(id=self.id * self.popSize + i,
                              parameters=self.params)
            # simulate
            patient.simulate(n_time_steps)

            # store outputs of this simulation
            self.cohortOutcomes.extract_outcome(simulated_patient=patient)

        # calculate cohort outcomes
        self.cohortOutcomes.calculate_cohort_outcomes(initial_pop_size=self.popSize)


class CohortOutcomes:
    def __init__(self):

        self.survivalTimes = []         # patients' survival times
        self.timesToDIAB = []           # patients' times to DIAB
        self.costs = []                 # patients' discounted costs
        self.utilities = []              # patients' discounted utilities
        self.nLivingPatients = None  # survival curve (sample path of number of alive patients over time)

        self.statSurvivalTime = None    # summary statistics for survival time
        self.statTimeToDIAB = None      # summary statistics for time to DIAB
        self.statCost = None            # summary statistics for discounted cost
        self.statUtility = None         # summary statistics for discounted utility

    def extract_outcome(self, simulated_patient):
        """ extracts outcome of a simulated patient
        :param simulated_patient: a simulated patients"""

        # record patient outcomes
        # survival time
        if simulated_patient.stateMonitor.survivalTime is not None:
            self.survivalTimes.append(simulated_patient.stateMonitor.survivalTime)
        # time until DIAB
        if simulated_patient.stateMonitor.timeToDIAB is not None:
            self.timesToDIAB.append(simulated_patient.stateMonitor.timeToDIAB)
        # discounted cost and discounted utility
        self.costs.append(simulated_patient.stateMonitor.costUtilityMonitor.totalDiscountedCost)
        self.utilities.append(simulated_patient.stateMonitor.costUtilityMonitor.totalDiscountedUtility)

    def calculate_cohort_outcomes(self, initial_pop_size):
        """ calculates the cohort outcomes
        :param initial_pop_size: initial population size
        """

        # summary statistics
        # self.statSurvivalTime = stat.SummaryStat(
        #     name='Survival time', data=self.survivalTimes)
        # self.statTimeToDIAB = stat.SummaryStat(
        #     name='Time until Diabetes', data=self.timesToDIAB)
        self.statCost = stat.SummaryStat(
            name='Discounted cost', data=self.costs)
        self.statUtility = stat.SummaryStat(
            name='Discounted utility', data=self.utilities)
