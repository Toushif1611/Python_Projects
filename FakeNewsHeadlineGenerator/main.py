# 1- import the random moduley
import random

# 2- create subjects
subjects = [
    "Shahrukh Khan",
    "Virat Kohli",
    "a mumbai cat",
    "a group of mounkeys",
    "a group of ladies"
]

actions = [
    "launcies",
    "cancels",
    "dances with",
    "eats",
    "declares war"
]

places_or_things = [
    "at Red Fort",
    "in mumbai local Train",
    "inside parliament",
    "at footpath",
    "in the university"
]

# 3- start the headline generation
while True:
    subject = random.choice(subjects)
    action = random.choice(actions)
    place_or_thing = random.choice(places_or_things)

    headline = f"BREAKING NEWS: {subject} {action} {place_or_thing}"
    print("\n" + headline)

    user_input = input("\nDo you want another headline? (yes/no)").strip().lower()
    if user_input == "no":
        break

#print goodbye messege
print("\nThanks for using the Fake News Headline generetor. Have a fun day ")