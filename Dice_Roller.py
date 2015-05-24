"""
Created on Tue Aug 26 23:40:11 2014
@author: Samuel
"""
from random import randint
from array import array

def parse(l):
    try:
        dice = l.split('d', 1)
        second_param = " "
        if ' ' in dice[1]:
            second_param = dice[1].split(' ')[1][:-2]
            dice[1] = "{0}\r\n".format(dice[1].split(' ')[0])
        message = roll(long(dice[0]), long(dice[1][:-2])) if 'shadowrun' not in second_param.lower() else shadowrun_roll(long(dice[0]), long(dice[1][:-2]))
        return "Invalid syntax. Correct syntax is: .roll #d#" if len(dice) > 2 or long(dice[0]) < 1 else message
    except ValueError:
        print "Value Error"
        return "Invalid syntax. Correct syntax is: .roll #d#"

def roll(times, sides):
    rolled = array('i', (randint(1, sides) for i in range(0, times))).tolist()
    x, y = sum(rolled), rolled
    return "Rolled {0}. {1}".format(x, y)
    
def shadowrun_roll(times, needed):
    rolled = array('i', (randint(1, 6) for i in range(0, times))).tolist()
    hits, ones = 0, 0
    message = ""
    for i in rolled:
        if i > 4: hits += 1
        elif i == 1: ones += 1
    if ones >= times / 2 and hits == 0:
        message += "Critical glitch. "
    elif ones >= times / 2 and hits > 0:
        message += "Glitch. "
    elif hits >= needed + 4 and needed > 0:
        message += "Critical Success! "
    message += "Rolled {0} hits. {1}".format(hits, rolled) 
    return message