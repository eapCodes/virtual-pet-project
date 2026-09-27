import pygame
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.pet import Pet

my_pet = Pet()

pygame.init()

screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Wizardling")

running = True
menu_rects = [
    pygame.Rect(24, 240, 70, 40),
    pygame.Rect(118, 240, 70, 40),
    pygame.Rect(212, 240, 70, 40),
    pygame.Rect(306, 240, 70, 40),
    pygame.Rect(24, 20, 70, 40),
    pygame.Rect(118, 20, 70, 40),
    pygame.Rect(212, 20, 70, 40),
    pygame.Rect(306, 20, 70, 40)
]
menu_items = ["Feed", "Play", "Rest", "Teach", "Status", "Cast spell", "Brew Potion", "Enter Dungeon"]
selected_index = 0
font = pygame.font.Font(None, 15)
current_screen = "main"
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                selected_index = selected_index + 1
                if selected_index >= len(menu_items):
                    selected_index = 0
            if event.key == pygame.K_LEFT:
                selected_index = selected_index - 1
                if selected_index < 0:
                    selected_index = len(menu_items) - 1
            if event.key == pygame.K_RETURN:
                if selected_index == 0:
                    my_pet.feed()
                elif selected_index == 1:
                    my_pet.play()
                elif selected_index == 2:
                    my_pet.rest()
                elif selected_index == 3:
                    my_pet.teach()
                elif selected_index == 4:
                    current_screen = "status"
                elif selected_index == 5:
                    print("cast spell not built")
                elif selected_index == 6:
                    print("brew Potion not built")
                elif selected_index == 7:
                    print("dungeon not built")
            if event.key == pygame.K_ESCAPE:
                current_screen = "main"

    screen.fill((30, 30, 60))

    if current_screen == "main":
        for i, rect in enumerate(menu_rects):
            if i == selected_index:
                color = (255, 255, 0)
            else:
                color = (100, 100, 100)
            pygame.draw.rect(screen, color, rect)
            label = font.render(menu_items[i], True, (255, 255, 255))
            screen.blit(label, (rect.x + 5, rect.y + 5))
    elif current_screen == "status":
        line1 = font.render(f"Hunger: {my_pet.hunger:.0f}", True, (255, 255, 255))
        screen.blit(line1, (20, 40))
        line2 = font.render(f"Energy: {my_pet.energy:.0f}", True, (255, 255, 255))
        screen.blit(line2, (20, 65))
        line3 = font.render(f"Happiness: {my_pet.happiness:.0f}", True, (255, 255, 255))
        screen.blit(line3, (20, 90))
        line4 = font.render(f"Knowledge: {my_pet.knowledge:.0f}", True, (255, 255, 255))
        screen.blit(line4, (20, 115))
        line5 = font.render(f"Mood: {my_pet.mood()}", True, (255, 255, 255))
        screen.blit(line5, (25,140))


    pygame.display.flip()
    print(current_screen)