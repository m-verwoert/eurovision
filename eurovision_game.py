"""
This script takes a file with information on the eurovision winners of each year
which can be used to study (practice mode), take a quiz on (quiz mode) or plot
an overview of how many times a country has won (overview mode).

by Maxime Verwoert (last edit 27-05-2021)
"""
#import modules
import csv
import json
import os
from os import path
import time
import random
import seaborn as sns
import matplotlib.pyplot as plt
from simpleimage  import SimpleImage


def main():
    #welcome message
    print("Welcome, Eurovision fan!")
    print("\nHere you can practice and test your knowledge on the Eurovision winners by year, "
          "or see an overview of how many times a country has won. You can return to the "
          "selection menu at any time by typing 'quit'. Enjoy!")
    #load the eurovision winner data
    data = load_data()
    #get desired mode from user and start it
    mode = select_valid_mode()
    end = enter_mode(data, mode)
    #loop to continue playing
    while end == False:
        mode = select_valid_mode()
        end = enter_mode(data, mode)
    #signal the end of the game
    print("\nExiting Eurovision game... Thanks for playing :)")


def load_data():
    """
    Loads a eurovision winners dictionary (json file) or creates one if only the
    original file (csv file) is present in the current directory. 
    """
    fname = "eurovision_winners"
    fpath = path.abspath(os.getcwd()) + "\\"
    if path.exists(fname+".json"):
        with open (fpath + fname + ".json", encoding = 'iso_8859_1') as jsonfile:
            data = json.load(jsonfile)
    elif path.exists(fname+".csv"):
        with open(fpath + fname + ".csv", 'r', newline='', encoding = 'iso_8859_1') as csvfile:
            reader = csv.DictReader(csvfile)
            data = {}
            for row in reader:
                year = row.pop('Year')
                data[year] = row
        with open(path+'eurovision_winners.json', 'w', encoding = 'iso_8859_1') as jsonfile:
            json.dump(data, jsonfile, indent=4, ensure_ascii=False)
    else:
        print("Required files not found, please make sure \'eurovision_winners.json\' "
              "or \'eurovision_winners.csv\' is in the current directory!")
    return data
    
        
def select_valid_mode():
    """
    Asks user to select a valid mode.
    """
    valid_modes = {'practice', 'quiz', 'overview', 'exit'}
    mode = input("Would you like to practice, take a quiz, see an overview or exit the game? ")
    while mode.lower() not in valid_modes:
        if mode.lower() != 'end':
            mode = input("Please type 'practice', 'quiz', 'overview' or 'exit': ")
    return mode.lower()


def enter_mode(data, mode):
    """
    Starts the requested mode or returns to the main function to exit the game.
    """
    if mode == 'practice':
        eurovision_practice(data)   
    elif mode == 'quiz':
        eurovision_quiz(data)
    elif mode == 'overview':
        eurovision_overview(data)
    else:
        return True
    return False
    

def eurovision_practice(data):
    """
    Allows the user to enter a valid eurovision year and displays relevant information
    about the winner of that year. This mode is a continuous loop until the user decides
    to quit.
    """
    print("\nYou have entered practice mode!" 
          "\nChoose a year and you will see relevant information about the winner(s). "
          "Note: you only have to remember the year and (one) winning country for the quiz."
          "\nType 'quit' to return to the main menu.")
    while True:
        year = input("Enter a year (1956-2021): ")
        while year not in data:
            if year != 'quit':
                year = input("Please enter a valid year: ")    
            else:
                print("\nReturning to the menu...")
                return
        print("Winner: " + data[year]['Winner'])
        print("Song: " + "\"" + data[year]['Song'] + "\"")
        print("Performer: " + data[year]['Performer'])
        if year == '1969':
            print("Note: in 1969 it was the first time ever a tie had occurred. "
                  "However, there was no rule at the time to cover such an eventuality, so all four countries were declared joint winners. "
                  "Choose one of these four countries during the quiz.")


def eurovision_quiz(data):
    """ 
    Presents a specified numbers of questions to the user, displays feedback after
    the last question and returns to the main function. 
    """
    numq = 1
    print("\nYou have entered quiz mode!"
          "\nTry to answer all", numq, "questions, you'll get a score at the end."
          "\nType 'quit' to return to the main menu during the quiz."
          "\nGood luck!")
    score = quiz_questions(data, numq)
    if score != 'quit':
        quiz_feedback(score, numq)
    time.sleep(2)
    print("\nReturning to the menu...")


def quiz_questions(data, numq):
    """ 
    Presents the quiz questions with direct feedback, if the user enters 'quit'
    it will return to the main function.
    """
    used = []
    score = 0
    for q in range(numq):
        year = random.choice(list(data.keys()))
        while year in used:
            year = random.choice(list(data.keys()))
        used.append(year)
        answer = input(str(q+1) + ". Which country won in " + str(year) + "? ")
        if year != '1969':
            if answer.lower() == data[year]['Winner'].lower():
                print("Correct!")
                score += 1
            elif answer.lower() == 'quit':
                return answer.lower()
            else:
                print("Incorrect. The correct answer was " + data[year]['Winner'] + ".")
        else: #because multiple countries are correct in 1969
            winners = data[year]['Winner'].split('|')
            winnersl = (data[year]['Winner'].lower()).split('|')                               
            if answer.lower() in winnersl: 
                print("Correct!")
                score += 1
            elif answer.lower() == 'quit':
                return answer.lower()
            else:
                print("Incorrect. Correct answers were: ")  
                print(*winners, sep = ", ")
    return score


def quiz_feedback(score, numq):
    """ 
    Displays feedback based on the number of correct answers to the quiz, then
    returns to the main function.
    """
    if score == numq:         
        print("\nYour score is " + str(score) + "/" + str(numq) + ", you are a true Eurovision fan!! " 
              "\nHere is your well-deserved award!")
        image = SimpleImage("eurovision_trophy.jpg")
        time.sleep(2)
        image.show()
    elif score > int(numq/2):
        print("\nYour score is " + str(score) + "/" + str(numq) + ", well done!"
              "\nConsider playing the quiz again to win an award.")  
    else: 
        print("\nYour score is " + str(score) + "/" + str(numq) + ", better luck next time. " 
              "\nConsider (continuing) the practice mode.")    


def eurovision_overview(data):
    """ 
    Creates a new dictionary with the numbers of times each country has won 
    (if it doesn't yet exist in the directory) and displays a graph on this data. 
    Then returns to the main function.
    """
    if path.exists("eurovision_overview.png") == False:
        wins = {}
        for year in data:
            for country in data[year]['Winner'].split('|'):
                if country not in wins:
                    wins[country] = 1
                else:
                    wins[country] += 1
        del wins['COVID-19']
        countries = sorted(list(wins.keys()))
        counts = [wins[country] for country in countries]
        overview = {'x': countries, 'y': counts}
        plt.figure(figsize=(14, 7))
        sns.barplot(x = 'x', y = 'y', data = overview)
        plt.xticks(rotation=45, ha='right', fontsize=14)
        plt.yticks(fontsize=14)
        plt.xlabel('Country', fontsize=14, fontweight = 'bold')
        plt.ylabel('Number of Wins', fontsize=14, fontweight = 'bold')
        plt.title('Eurovison Winners', fontsize=22, fontweight = 'bold')
        plt.savefig("eurovision_overview.png", dpi=500, bbox_inches = 'tight') 
    image = SimpleImage("eurovision_overview.png")
    print("\nHere you go!")
    time.sleep(2)
    image.show()       
    print("\nReturning to the menu...")


if __name__ == '__main__':
    main()