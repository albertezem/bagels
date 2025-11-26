import gymnasium as gym
from gym.spaces import Dict, Discrete
import random
import numpy as np

def initializePossibleAnswers(n=10):
    possible = []

    for i in range(0, n):
        for j in range(0, n):
            for k in range(0, n):
                if i != j and j != k and i != k:
                    possible.append(str(i) + str(j) + str(k))

    return possible

def index_to_answer_map():
    answers = initializePossibleAnswers()
    mp = {}
    
    for i in range(720):
        mp[i] = answers[i]
        
    return mp

class PFBEnv(gym.Env):
    def __init__(self):
        self.answer = random.choice(initializePossibleAnswers())
        self._map = index_to_answer_map()
        self.responses = []
        self.observation_space = gym.spaces.MultiBinary(720)
        self.action_space = gym.spaces.Discrete(720)

    def _get_obs(self):
        possible_i = np.where(self.observation_space == 1)[0]
        
        possible_ans = [self._map[x] for x in possible_i]
        
        return possible_ans

    def _get_info(self):
        return self.responses, self.answer

    def reset(self, seed=None, options=None):
        self.answer = random.choice(initializePossibleAnswers())

        self.observation_space = np.ones(self.observation_space.shape)
        
    def step(self, action):
        action = self._map[action]
        
        # update responses with response code
        
        # check if guess is correct
        
        # update possible answers according to response code
        
        # reward is always -1
