import requests
import json
from random import random as rand
from random import shuffle
from datetime import date
import os
import glob
import textwrap
import re
from html import unescape
import codecs

def glean():
    #set difficulty paramaters
    EASY_PROB = .6
    MED_PROB = .3
    HARD_PROB = .1
    
    #words to exlcude, mostly useful for eggregious examples multiple choice 
    #causing problems
    EXCLUDED = ['following', 'except']
    
    #set which this will be
    r = rand()
    diff = 'easy' if r < EASY_PROB else ('medium' if r < EASY_PROB + MED_PROB else 'hard')    
    
    #gets a single run of as many questions as possible
    _url = 'https://opentdb.com/api.php?amount=50&difficulty=' + diff + '&type=multiple'
    _json = json.loads(requests.get(_url).text)
    res = {}
    for question in _json['results']:
        if all(not e in question['question'].lower() for e in EXCLUDED):
            res[str(question)] = (question['question'], question['correct_answer'])
    return res

def get(num_qs = 1200, max_iter = 1000):
    res = {}
    _iter = 0
    while len(res) < num_qs and _iter < max_iter:
        res.update(glean())
        _iter += 1
    res = [(k, v) for (k, v) in res.items()]
    res = res if len(res) <= num_qs else res[:num_qs]
    shuffle(res)
    res = dict(res)
    return _iter < max_iter, res

def generate(num_games, qs_per_game):
    tot_qs = num_games * qs_per_game
    success, qs = get(num_qs = tot_qs, max_iter = 1000)
    qpg = qs_per_game if success else (len(qs)//num_games)
    questions = list(qs.values())
    shuffle(questions)
    games = [questions[ind:ind+qpg] for ind in range(0, len(questions), qpg)]
    return games

def write(num_games, qs_per_game):
    #A constant important to the formatting
    LINE_LENGTH = 60
    
    #writes to a subfolder of this folder named for distro and date
    dir_name = str(num_games) + '_GAMES-' + str(qs_per_game) + '_QUESTIONS'
    dir_name += '-' + date.today().strftime("%m_%d_%Y")
    #if the folder exists, clear it out
    if os.path.isdir(dir_name):
        for f in glob.glob(dir_name + '/*'):
            os.remove(f)
    else:
        #otherwise, create it
        os.mkdir(dir_name)
        
    #Now actually get the games
    games = generate(num_games, qs_per_game)
    for (ind, game) in enumerate(games):
        #make and write a file with the game contents
        filename = 'game-' + str(ind+1) + '.txt'
        game_str = ''
        for (q, a) in game:
            #construct and add in the question string
            qstr = '\n' + '-' * LINE_LENGTH + '\n'
            qstr += 'Q: '
            q_lines = textwrap.fill(q, width = LINE_LENGTH - 3)
            q_lines = re.sub('\n', '\n   ',  q_lines)
            qstr += q_lines
            qstr += '\n' + '-' * LINE_LENGTH + '\n'
            qstr += 'A: '
            a_lines = textwrap.fill(a, width = LINE_LENGTH - 3)
            a_lines = re.sub('\n', '\n   ',  a_lines)
            qstr += a_lines
            qstr += '\n' + '-' * LINE_LENGTH + '\n'
            game_str += qstr
        #fix the unicode problems and write it.
        game_str = unescape(game_str)
        with codecs.open(dir_name + '/' + filename, 'w', 'utf-8') as f:
            f.write(game_str)
    print('Success!')
        

write(25, 60)

    