#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import glob
import sys
import json
from pathlib import Path
import textwrap

import pandas as pd

from math import factorial
    
"""



"""

__version_info__ = ('0', '1', '0')
__version__ = '.'.join(__version_info__)

version_history = \
"""
0.1.0 - initial version  
"""
    
SampleData = 'SampleData'

class ImpulsivityProcess:
    
    def __init__(self, **kwargs):
        
        # load self.config
        self.config = {}
        for key, value in kwargs.items():
            self.config[key] = value

    def test(self, cmd=''):
        
        if cmd == "GoStop":
            filename = os.path.join(SampleData,"GoStop.json")
            # read sample data
            with open(filename, 'r') as file:
                task_data = json.load(file)   
            result = self.gostop_score(task_data)     
            pass
        elif cmd == "IST":
            filename = os.path.join(SampleData,"IST.json")
            # read sample data
            with open(filename, 'r') as file:
                task_data = json.load(file)   
            result = self.ist_score(task_data)
            pass
        elif cmd == "DelayDiscounting":
            filename = os.path.join(SampleData,"DelayDiscounting.json")
            with open(filename, 'r') as file:
                task_data = json.load(file)   
            result = self.delaydiscounting_score(task_data)
            pass


    def ist_score(self,ddict):
        """
        Analyze the IST task

        Two conditions:
        1. DecreasingWin
        2. FixedWin
        
        rt - total time to make choice
        Args:
            ddict  - dictionary of IST task
        """
        total_entries = len(ddict)
        
        results = {}
        for condition in ['DecreasingWin','FixedWin']:
            results[condition] = {}
            results[condition]['opens'] = []  # len of pressed
            results[condition]['incorrect'] = []  # correct
            results[condition]['choicetime'] = []  # rt
            results[condition]['latency'] = []  # latency
                        
        for index in range(total_entries):
            entry = ddict[index]
            # check if pressed is a key
            if 'pressed' in entry:
                # data to use
                opens = len(entry['pressed'])
                # check if response is correct
                if entry['correct'] == True:
                    incorrect = 0
                else:
                    incorrect = 1
            
                choicetime = entry['rt']
                
                if entry['decreasing'] == True:
                    condition = 'DecreasingWin'
                else:
                    condition = 'FixedWin'
                    
                results[condition]['opens'].append(opens)
                results[condition]['incorrect'].append(incorrect)
                results[condition]['choicetime'].append(choicetime)
                # calculate metrics
                latency = choicetime/opens 
                results[condition]['latency'].append(latency)
                
                # calculate the number of target color boxes opened
                # by reading the pressed list
        
        pass
    
    def test_probability_calculation(self):
        
        # Example usage:
        num_boxes_opened = 3
        num_boxes_chosen_color = 5
        probability = self.probability_of_at_least_one_correct(num_boxes_opened, num_boxes_chosen_color)
        print(f"Probability of finding at least one box of the chosen color: {probability}")
        pass

    def probability_of_at_least_one_correct(self, z, a):
        """
        Calculates the probability of finding at least one box of the chosen color 
        when opening 'z' boxes out of a total where 'a' boxes are of that color,
        using the original formula adapted for this problem.

        Args:
            z: The number of boxes opened.
            a: The number of boxes of the chosen color.

        Returns:
            The probability of finding at least one box of the chosen color.
        """
        if z <= 0 or a <= 0:
            return 0  # Handle invalid input

        total_combinations = factorial(a) // (factorial(z) * factorial(a - z))
        favorable_combinations = 0

        for k in range(1, z + 1):
            binomial_coeff = factorial(a) // (factorial(k) * factorial(a - k))
            favorable_combinations += binomial_coeff

        probability = favorable_combinations / total_combinations
        return probability




    def probability_of_at_least_one_correct_mod(z, a):
        """
        Calculates the probability of finding at least one box of the chosen color 
        when opening 'z' boxes out of a total where 'a' boxes are of that color.

        Args:
            z: The number of boxes opened.
            a: The number of boxes of the chosen color.

        Returns:
            The probability of finding at least one box of the chosen color.
        """
        if z <= 0 or a <= 0:
            return 0  # Handle invalid input

        total_combinations = factorial(a) // (factorial(z) * factorial(a - z))
        unfavorable_combinations = 1  # Only one combination where none are the chosen color

        probability = 1 - (unfavorable_combinations / total_combinations) 
        return probability

    def get_hours_for_delay_discounting(self, index):
        """
        return the hours for the delay discounting task times from the 
        Koffarnus and Bickel paper 2014 
        
        """
        # conversion factor to hours
        day2hours = 24
        week2hours = 7 * day2hours
        month2hours = 30 * day2hours
        year2hours = 365 * day2hours
        
        # index used is one index so first entry of list is zero
        
        hours = [
            0, # 
            1, # 1 hour
            2, # 2 hours
            3, # 3 hours
            4, # 4 hours
            6, # 6 hours
            9, # 9 hours
            12, # 12 hours
            1*day2hours, # 1 day
            1.5*day2hours, # 1.5 days
            2*day2hours, # 2 days
            3*day2hours, # 3 days
            4*day2hours, # 4 days
            1*week2hours, # 1 week
            1.5*week2hours, # 1.5 weeks
            2*week2hours, # 2 weeks
            3*week2hours, # 3 weeks
            1*month2hours, # 1 month
            2*month2hours, # 2 months
            3*month2hours, # 3 months
            4*month2hours, # 4 months
            6*month2hours, # 6 months
            8*month2hours, # 8 months
            1*year2hours, # 1 year
            2*year2hours, # 2 years
            3*year2hours, # 3 years
            4*year2hours, # 4 years
            5*year2hours, # 5 years
            8*year2hours, # 8 years
            12*year2hours, # 12 years
            18*year2hours, # 18 years
            25*year2hours, # 25 years
        ]
        
        if index < len(hours):
            return hours[index]
        else:
            # error
            return None
        
    def delaydiscounting_score(self,ddict):
        """
        Analyze the delay discounting task

        Args:
            ddict  - dictionary of IST task
            
        Results:
            ED50 - the effective delay at which the subjective value of the
            reward is 50% of the immediate reward, we return the log transform of the time
        """
        total_entries = len(ddict)
        # determine the ED50 value
        # iterate starting with last entry and identifying when entry['delay] == True
        for index in range(total_entries-1,0,-1):
            entry = ddict[index]
            if entry['delay'] == True:
                # get the index number
                time_index = entry['index'][0]
                break
        
        # get the hours for the time_index
        hours = self.get_hours_for_delay_discounting(time_index)
        
        pass    
    
    def gostop_score(self,ddict):
        """
        Analyze each GoStop entry

        how many correct and incorrect responses on novel/target
        how many correct and incorrect responses on stop signal
        
        Args:
            ddict (_type_): _description_
        """
        novel_total = 0
        novel_correct = 0
        novel_incorrect = 0
        target_total = 0
        target_correct = 0
        target_late = 0
        target_incorrect = 0
        stop_total = 0
        stop_correct = 0
        stop_incorrect = 0
        target_reaction_times = []
    
        
        total_entries = len(ddict)
        # initialize skip to False
        skip = False
        for index in range(total_entries):
            if skip == True:
                skip = False
                continue
            entry = ddict[index]
            # don't read past the end of the list
            
            if index < total_entries - 1:
                next1_entry = ddict[index+1]
            if index < total_entries - 2:
                next2_entry = ddict[index+2]
            if index < total_entries - 3:
                next3_entry = ddict[index+2]
            
            if entry.get('type',None) == 'novel':
                novel_total += 1
                if entry.get('correct',None) == True:
                    # now check next fixation response to see if 
                    # it was correct or incorrect
                    if next1_entry.get('correct',None) == False:
                        novel_incorrect += 1
                    else:
                        novel_correct += 1
                elif entry.get('correct',None) == False:
                    novel_incorrect += 1
            elif entry.get('type',None) == 'target':
                target_total += 1
                if entry.get('correct',None) == True:
                    # now check next fixation response to see if 
                    # it was late or not
                    # get the reaction time for this entry
                    rt = entry.get('rt',None)
                    target_reaction_times.append(rt)
                    target_correct += 1
                else:
                    # check if pressed during fixation entry
                    if next1_entry.get('correct',None) == False:
                        # responded but it was late
                        target_late += 1
                    
                        # calculate the reaction time
                        # add 500 ms for the stimulus presentation time
                        rt = next1_entry.get('rt',None) + 500
                        target_reaction_times.append(rt)
                    else:
                        target_incorrect += 1
                
            elif entry.get('type',None) == 'stop':
                """
                Stop requires two entries, so we need to check next2 
                """
                # set to skip next entry which will be a stop 
                skip = True
                stop_total += 1
                if entry.get('correct',None) == False:
                    # pressed during blue
                    stop_incorrect += 1
                elif next1_entry.get('correct',None) == False:
                    # pressed during yellow stop
                    stop_incorrect += 1
                else:
                    # check if responded late during fixation entry
                    if next2_entry.get('correct',None) == False:
                        # responded but it was late
                        stop_incorrect += 1
                    else:
                        stop_correct += 1
                pass
             
            pass
        # calculate the mean reaction time
        if len(target_reaction_times) == 0:
            info = {}
        else:
            mean_reaction_time = sum(target_reaction_times) / len(target_reaction_times)
            stop_incorrect_ratio = stop_incorrect / stop_total
            
            info = {
                'gs_novel_total': novel_total,
                'gs_novel_correct': novel_correct,
                'gs_novel_incorrect': novel_incorrect,
                'gs_target_total': target_total,
                'gs_target_correct': target_correct,
                'gs_target_late': target_late,
                'gs_target_incorrect': target_incorrect,
                'gs_stop_total': stop_total,
                'gs_stop_correct': stop_correct,
                'gs_stop_incorrect': stop_incorrect,
                'gs_mean_reaction_time': mean_reaction_time,
                'gs_stop_incorrect_ratio': stop_incorrect_ratio
            }
        
        return info
    
    def read_csv(self):
        with open(self.config['csvfile'], 'r') as file:
            self.data = pd.read_csv(file)
        pass
    
    def retrieve_row_column(self, row, column_name):
        return self.data.loc[row,column_name]
        
if __name__ == "__main__":
    
    # provide a description of the program with format control
    description = textwrap.dedent('''\
        Code to process impulsivity tasks.
        
    ''')
    
    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawTextHelpFormatter)

    
    parser.add_argument("--env", type = str,
                     help="name of env file in the current directory, default .env",
                      default=".env") 

    parser.add_argument("--config", type = str,
                     help="name of yaml config file in the current directory, default config.yaml",
                      default="config.yaml") 
        
    parser.add_argument("--cmd", type = str,
                    help="cmd - [list, summarize], default list",
                    default = 'list')

    parser.add_argument("--format", type = str,
                    help="format to use, default json",
                    default = 'json')
    
    parser.add_argument("-H", "--history", action="store_true", help="Show program history")
     
    # parser.add_argument("--quiet", help="Don't output results to console, default false",
    #                     default=False, action = "store_true")  
    
    parser.add_argument("--verbose", type=int, help="verbose level default 2",
                         default=2) 
        
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {__version__}')

    args = parser.parse_args()

    if args.history:
        print(f"{os.path.basename(__file__) } Version: {__version__}")
        print(version_history)
        exit(0)

    obj = ImpulsivityProcess( #cmd=args.cmd, 
                        # env=args.env, 
                        verbose=args.verbose, 
                        #config=args.config,
                        #format=args.format,
                        #csvfile=args.csvfile
                    )
    
    obj.test(cmd=args.cmd)