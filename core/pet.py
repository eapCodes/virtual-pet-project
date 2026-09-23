from datetime import datetime
import time
class Pet:
    def __init__ (self):
        self.hunger = 70
        self.energy = 70
        self.happiness = 70
        self.knowledge = 0
        self.health = 100
        self.last_updated = datetime.now()
        self.last_fed = datetime.now()
        self.last_played = datetime.now()
        self.last_rested = datetime.now()
        self.last_teach = datetime.now()

    def tick(self):
        elapsed = datetime.now() - self.last_updated
        elapsed_hours = elapsed.total_seconds() / 3600
        self.last_updated = datetime.now()

        self.hunger = self.hunger - (4 * elapsed_hours)
        self.hunger = max(0, min(100, self.hunger))

        self.energy = self.energy - (3 * elapsed_hours)
        self.energy = max(0, min(100, self.energy))

        self.happiness = self.happiness - (2 * elapsed_hours)
        self.happiness = max(0, min(100, self.happiness))

        if self.hunger ==0 or self.energy == 0:
            self.health = self.health - (10 * elapsed_hours)
            self.health = max(0, min(100, self.health))

    def feed(self):
        elapsed_since_fed = datetime.now() - self.last_fed
        elapsed_minutes = elapsed_since_fed.total_seconds() / 60

        if elapsed_minutes < 15:
            print("Not ready to feed yet.")
            return
        self.hunger += 30
        self.hunger = max(0, min(100, self.hunger))
        self.energy += 5
        self.energy = max(0, min(100, self.energy))
        self.last_fed = datetime.now()

    def play(self):
        elapsed_since_play = datetime.now() - self.last_played
        elapsed_minutes = elapsed_since_play.total_seconds() / 60

        if elapsed_minutes < 15:
            print("Not ready to play.")
            return
        self.happiness += 25
        self.happiness = max(0, min(100, self.happiness))
        self.energy -= 10
        self.energy = max(0, min(100, self.energy))
        self.last_played = datetime.now()

    def rest(self):
        elapsed_since_rest = datetime.now() - self.last_rested
        elapsed_minutes = elapsed_since_rest.total_seconds() / 60

        if elapsed_minutes < 30: 
            print("Not ready to sleep.")
            return
        self.energy += 40
        self.energy = max(0, min(100, self.energy))
        self.hunger -= 5
        self.hunger = max(0, min(100, self.hunger))
        self.last_rested = datetime.now()

    def teach(self):
        elapsed_last_teach = datetime.now() - self.last_teach
        elapsed_minutes = elapsed_last_teach.total_seconds() / 60

        if elapsed_minutes < 20:
            print("Not ready to learn")
            return
        self.knowledge += 15
        self.knowledge = max(0, min(100, self.knowledge))
        self.energy -= 15
        self.energy = max(0, min(100, self.energy))
        self.happiness -= 5
        self.happiness = max(0, min(100, self.happiness))
        self.last_teach = datetime.now()

    def mood(self):
        if self.health <= 0:
                return "Fading"
        elif self.hunger <= 15:
                return "Hungry"
        elif self.energy <= 15:
             return "tired"
        elif self.happiness <= 20:
                return "Sad"
        elif self.hunger >= 70 and self.energy >= 70 and self.happiness >= 70 and self.knowledge >= 70:
                return "Happy"
        else:
                return "Neutral"

if __name__ == "__main__":
    my_pet = Pet()  
    my_pet.tick()

    print(my_pet.hunger)
    print(my_pet.energy)
    time.sleep(3)
    elapsed = datetime.now() - my_pet.last_updated
    print(elapsed.total_seconds())
    print(my_pet.hunger)
    my_pet.feed()
    print(my_pet.hunger)
    my_pet.feed()  # call it again immediately
    print(my_pet.hunger)
    print(my_pet.happiness, my_pet.energy)
    my_pet.play()
    print(my_pet.happiness, my_pet.energy)
    my_pet.play()
    print(my_pet.happiness, my_pet.energy)
    print(my_pet.hunger, my_pet.energy)
    my_pet.rest()
    print(my_pet.hunger, my_pet.energy)
    my_pet.rest()
    print(my_pet.hunger, my_pet.energy)
    print(my_pet.knowledge, my_pet.energy, my_pet.happiness)
    my_pet.teach()
    print(my_pet.knowledge, my_pet.energy, my_pet.happiness)
    my_pet.teach()
    print(my_pet.knowledge, my_pet.energy, my_pet.happiness)
    print(my_pet.mood())
        