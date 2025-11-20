"""jnknkjkk"""
from datetime import datetime

def generate_profile(age=int):
    if 0<=age<=12:
        return "Child"
    elif 13<=age<=19:
        return "Teenager"
    elif 20<=age:
        return "Abult"
    

now = datetime.now()

user_name=input('Enter your full name: ')

while True:
    birth_year_str=input('Enter your birth year: ')
    birth_year=int(birth_year_str)
    if birth_year<=now.year:
        break
    else:
        print("Sorry, try again")

current_age=now.year-birth_year
hobbies=[]
life_stage=generate_profile(current_age)

while True:
    hobby=input("Enter your favorite hobby or type 'stop' to finish: ")
    if hobby.lower()=="stop":
        break
    else:
        hobbies.append(hobby.title())

user_profile={"name":user_name.title(),"age":current_age,"status":life_stage,"hobby":hobbies}

print("\n---")
print("Profile Summary:")
print(f"Name: {user_profile['name']}")
print(f"Age: {user_profile['age']}")
print(f"Life Stage: {user_profile['status']}")
if len(hobbies)==0:
    print("You didn't mention any hobbies.")
else:
    print(f"Favorite Hobbies ({len(hobbies)}):")
    for i in user_profile["hobby"]:
        print(f"- {i}")
print('---')