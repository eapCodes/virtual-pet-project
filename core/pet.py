import os
from dotenv import load_dotenv
from datetime import datetime
import time
import json
import requests
load_dotenv()

def weather_to_affinity(condition):
    if condition == "Clear":
        return "elemental"
    elif condition == "Thunderstorm":
        return "elemental"
    elif condition == "Snow":
        return "illusion"
    elif condition == "Rain" or condition == "Drizzle":
        return "restoration"
    else:
        return "dark"


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
        self.elemental = 0
        self.restoration = 0
        self.illusion = 0
        self.dark = 0
        self.nature = 0
        self.birth_time = datetime.now()
        self.checkpoint_1_passed = None
        self.checkpoint_2_passed = None

        birth_hour = self.birth_time.hour
        if birth_hour <  6 or  birth_hour >= 20:
            self.dark +=  6
        else:
            self.restoration += 5
        try:
            api_key = os.getenv("OPENWEATHER_API_KEY")
            city = "Pocatello"
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=imperial"
            response = requests.get(url)
            data = response.json()
            condition = data["weather"][0]["main"]
            school = weather_to_affinity(condition)
            if school == "elemental":
                self.elemental += 5
            elif school == "illusion":
                self.illusion += 5
            elif school == "restoration":
                self.restoration += 5
            elif school == "dark":
                self.dark += 5
        except:
            pass

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

        age = datetime.now() - self.birth_time
        age_hours = age.total_seconds() / 3600
        drift_multiplier = max(0, 1 - (age_hours / 6))

        if self.happiness >= 70:
            self.restoration += drift_multiplier * elapsed_hours
        elif self.happiness <= 20:
            self.dark += drift_multiplier * elapsed_hours
            self.health = self.health - (0.5 * drift_multiplier * elapsed_hours)
            self.health = max(0, min(100, self.health))

        if self.get_stage() >= 2 and self.checkpoint_1_passed is None:
             gap = abs(self.restoration - self.dark)
             self.checkpoint_1_passed = gap <= 10

        if self.get_stage() >= 3 and self.checkpoint_2_passed is None:
            gap = abs(self.restoration - self.dark)
            self.checkpoint_2_passed = gap <= 10

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

    def save(self):
        data = {
              "hunger": self.hunger,
              "energy": self.energy,
              "happiness": self.happiness,
              "knowledge": self.knowledge,
              "health": self.health,   
              "last updated": self.last_updated.isoformat(),
              "last fed": self.last_fed.isoformat(),
              "last rest": self.last_rested.isoformat(),
              "last played": self.last_played.isoformat(),
              "last teach": self.last_teach.isoformat(),
              "elemental": self.elemental,
              "restoration": self.restoration,
              "illusion": self.illusion,
              "dark": self.dark,
              "nature": self.nature,
              "birth": self.birth_time.isoformat(),
              "checkpoint 1": self.checkpoint_1_passed,
              "checkpoint 2": self.checkpoint_2_passed
         }
        with open("saves/pet_save.json", "w") as f:
            json.dump(data,f)
    @classmethod
    def load(cls):
        with open("saves/pet_save.json", "r") as f:
            data = json.load(f)
        new_pet = cls()
        new_pet.hunger = data["hunger"]
        new_pet.energy = data["energy"]
        new_pet.happiness = data["happiness"]
        new_pet.knowledge = data["knowledge"]
        new_pet.health = data["health"]
        new_pet.last_updated = datetime.fromisoformat(data["last updated"])
        new_pet.last_fed = datetime.fromisoformat(data["last fed"])
        new_pet.last_rested = datetime.fromisoformat(data["last rest"])
        new_pet.last_played = datetime.fromisoformat(data["last played"])
        new_pet.last_teach = datetime.fromisoformat(data["last teach"])
        new_pet.elemental = data["elemental"]
        new_pet.restoration = data["restoration"]
        new_pet.illusion = data["illusion"]
        new_pet.dark = data["dark"]
        new_pet.nature = data["nature"]
        new_pet.birth_time = datetime.fromisoformat(data["birth"])
        new_pet.checkpoint_1_passed = data["checkpoint 1"]
        new_pet.checkpoint_2_passed = data["checkpoint 2"]
        new_pet.tick()
        return new_pet

    def get_stage(self):
            age = datetime.now() - self.birth_time
            age_hours = age.total_seconds() / 3600

            if age_hours < 2:
                return 1
            if age_hours < 6:
                return 2
            if age_hours < 24 * 3:
                return 3
            if age_hours < 24 * 5:
                return 4
            else:
                return 5
            
    def get_twilight_status(self):
         if self.checkpoint_1_passed == True and self.checkpoint_2_passed == True:
              return "full"
         elif self.checkpoint_2_passed == True and self.checkpoint_1_passed != True:
              return "partial"
         else:
              return "none"
         
    def get_shares(self):
         total = self.elemental + self.restoration+ self.illusion + self.dark + self.nature
         if total == 0:
              return {"elemental": 0, "restoration": 0, "illusion": 0, "dark": 0, "nature": 0}
         shares = {
              "elemental": self.elemental /total,
              "restoration": self.restoration / total,
              "illusion" : self.illusion / total,
              "dark": self.dark / total,
              "nature": self.nature / total
         }
         return shares

    def get_tier(self):
        shares = self.get_shares()
        values = sorted(shares.values(), reverse=True)

        count = 0
        for value in values:
            if value >= 0.4:
                count += 1

        if count == 0:
             return "unranked"
        elif count == 1:
             return "pure"
        elif count == 2:
             return "hybrid"
        elif count == 3:
             return "tri-class"
        elif count == 4:
             return "quad-class"
        else:
             return "archmage"

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
    my_pet.feed()  
    print(my_pet.hunger)
    print(my_pet.happiness, my_pet.energy)
    my_pet.play()
    print(my_pet.happiness, my_pet.energy)
    my_pet.play()
    print(my_pet.happiness, my_pet.energy)
    print(my_pet.hunger,  my_pet.energy)
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
    print(my_pet.last_updated.isoformat())
    my_pet.save()   
    loaded_pet = Pet.load()
    print(loaded_pet.hunger, loaded_pet.energy, loaded_pet.happiness, loaded_pet.knowledge, loaded_pet.health)
    print(my_pet.restoration, my_pet.dark)
    print(my_pet.get_stage())
    print(my_pet.restoration, my_pet.dark)
    print(my_pet.get_twilight_status())
    print(my_pet.get_shares())
    print(my_pet.get_shares())
    print(my_pet.get_tier())