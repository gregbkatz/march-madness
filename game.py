from scipy.special import erfinv, erf
from random import uniform
import pdb

class Game:
    def __init__(self, data, favorite=False):
        self.team0 = data['team0']
        self.team1 = data['team1']
        self.round = data['round']
        self.favorite = favorite
        self.p_win = self.calc_win_prob()
        self.error = []
        self.check_fit()

    def check_fit(self):
        # @TODO: This only makes sense for first round
        # Should add code for actual fit check across Monte Carlo
        diff = self.team0.rating - self.team1.rating
        p_win538 = self.team0.rd_win[self.round - 1]

        # nsigma = 2**0.5*erfinv(2*p_win538-1)
        # sigma = diff/nsigma
        error = self.p_win - p_win538 

        self.error = error

    def calc_win_prob(self):
        diff = self.team0.rating - self.team1.rating
        return 0.5*(1+erf(diff/10/2**0.5))

    def resolve_game_result(self, sample):
        # returns index of winning team
        # sample must be between 0 and 1
        # For monte carlo, sample should be uniformly distributed
        # For favorite to win use 1
        # For higher rated to win use 0.5
        
        # Get final round truth values
        t1_frnd = self.team0.final_round
        t2_frnd = self.team1.final_round

        # No truth value for this game
        if t1_frnd == -1 and t2_frnd == -1:
            return sample >= self.p_win

        # Check for conflict in final round truth value
        assert(t1_frnd != t2_frnd)

        rnd = self.round    

        # t1 advanced
        if t1_frnd > rnd:
            assert(t2_frnd == rnd or t2_frnd == -1)
            return 0

        # t1 lost
        elif t1_frnd != -1:
            assert(t1_frnd == rnd)
            assert(t2_frnd > rnd or t2_frnd == -1)
            return 1

        # t2 advanced
        elif t2_frnd > rnd:
            return 1
        # t2 lost
        else:
            assert(t2_frnd == rnd)
            return 0

    def resolve(self):
        sample = 0.5 if self.favorite else uniform(0,1)
        self.result = self.resolve_game_result(sample)
        if self.result:
            self.win_id = self.team1.id
            self.seed_diff = self.team1.seed - self.team0.seed
        else:
            self.win_id = self.team0.id
            self.seed_diff = self.team0.seed - self.team1.seed