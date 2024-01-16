# Bone Crushers
# Experiment Engine

PI = 3.1415926535

import copy
import secrets

from bonecrushers.library import wav

# Speaker Positions:
#  0 - Left Front
#  1 - Left Back
#  2 - Right Front
#  3 - Right Back
#  4 - Left Top
#  5 - Left Bottom
#  6 - Right Top
#  7 - Right Bottom

# Protocol:
#  6 positions (U, D, L, R, F, B)
#  2 distances (N, F)
#  3 random trials per pair in a block
#  2 blocks, one w/bkg noise, one without

# Position Delay Matrices
UP = [0, 0, 0, 0, -48, 48, -48, 48]
DOWN = [0, 0, 0, 0, 48, -48, 48, -48]
LEFT = [0, 0, 0, 0, 60, 60, 60, 60]
RIGHT = [60, 60, 60, 60, 0, 0, 0, 0]
FORWARD = [-36, 36, 0, 0, -36, 36, 0, 0]
BACKWARD = [36, -36, 0, 0, 36, -36, 0, 0]

# For far, multiply matrices by 3

class BCTrial():
    DelayMatrix = []
    BkgNoise = False
    Far = False

    def __init__(self, delay_matrix=[0,0,0,0,0,0,0,0], bkg=False, far=False):
        self.DelayMatrix=delay_matrix
        self.BkgNoise=bkg
        self.Far=far

        if far:
            self.DelayMatrix *= 3
        
    def __repr__(self) -> str:
        return f"BoneCrushers Experiment Trial: (delay_matrix={self.DelayMatrix}, {('ambient' if self.BkgNoise else 'silent')}, {('far' if self.Far else 'near')})"

class BCTrial_Adv():
    ZAxis = 0
    Theta = 0
    BkgNoise = False
    Far = False

    def __init__(self, t=0, z=0, bkg=False, far=False):
        self.ZAxis=z
        self.Theta=t
        self.BkgNoise=bkg
        self.Far=far

    def __repr__(self) -> str:
        return f"BoneCrushers Experiment Trial: (t={self.Theta}, z={self.ZAxis}, {('ambient' if self.BkgNoise else 'silent')}, {('far' if self.Far else 'near')})"

class BCExperiment():

    def setup(self, ambient=False):
        """Generates a random set of trials for the experiment"""

        # experiments
        exp_base = [

            BCTrial(bkg=ambient, delay_matrix=FORWARD),    #forward
            BCTrial(bkg=ambient, delay_matrix=RIGHT),      #right
            BCTrial(bkg=ambient, delay_matrix=BACKWARD),   #backward
            BCTrial(bkg=ambient, delay_matrix=LEFT),       #left
            BCTrial(bkg=ambient, delay_matrix=UP),         #up
            BCTrial(bkg=ambient, delay_matrix=DOWN),       #down

            BCTrial(bkg=ambient, far=True, delay_matrix=FORWARD),
            BCTrial(bkg=ambient, far=True, delay_matrix=RIGHT),
            BCTrial(bkg=ambient, far=True, delay_matrix=BACKWARD),
            BCTrial(bkg=ambient, far=True, delay_matrix=LEFT),
            BCTrial(bkg=ambient, far=True, delay_matrix=UP),
            BCTrial(bkg=ambient, far=True, delay_matrix=DOWN),

            # BCTrial(bkg=ambient),    #forward
            # BCTrial(bkg=ambient, t=-(PI/2)),    #right
            # BCTrial(bkg=ambient, t=PI),   #backward
            # BCTrial(bkg=ambient, t=(PI/2)),   #left
            # BCTrial(bkg=ambient, z=1),    #up
            # BCTrial(bkg=ambient, z=-1),   #down

            # BCTrial(bkg=ambient, far=True),
            # BCTrial(bkg=ambient, far=True, t=-(PI/2)),
            # BCTrial(bkg=ambient, far=True, t=PI),
            # BCTrial(bkg=ambient, far=True, t=(PI/2)),
            # BCTrial(bkg=ambient, far=True, z=1),
            # BCTrial(bkg=ambient, far=True, z=-1),
        ]

        exp_set = copy.deepcopy(exp_base) + copy.deepcopy(exp_base) + copy.deepcopy(exp_base)

        # Cryptographically scramble the test cases
        exp_final_set = []
        while len(exp_set) > 0:
            picked_item = secrets.choice(exp_set)
            exp_final_set.append(picked_item)
            exp_set.remove(picked_item)
        
        self.exp_set = exp_final_set

        print(self.exp_set)
        
def main():
    exp = BCExperiment()
    exp.setup()

    # Experiment selection complete
    
    # TODO: Actually... do the proper math (look at student submitted code)

    
    