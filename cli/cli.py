import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.pet import Pet

my_pet = Pet()
print(my_pet.hunger)

while True:
    my_pet.tick()

    print(my_pet.hunger)
    print(my_pet.energy)
    print(my_pet.happiness)
    print(my_pet.knowledge)
    print(my_pet.mood())

    print("1. Feed")
    print("2. Play")
    print("3. Rest")
    print("4. Teach")
    print("5. Quit")

    choice = input("> ")

    if choice == "1":
        my_pet.feed()
    elif choice == "2":
        my_pet.play()
    elif choice == "3":
        my_pet.rest()
    elif choice == "4":
        my_pet.teach()
    elif choice == "5":
        break