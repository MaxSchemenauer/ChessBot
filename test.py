import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Initial Rectangle
rect1 = pygame.Rect(100, 100, 50, 50)
rect2 = pygame.Rect(200, 200, 50, 50)
rect1_color = (255, 0, 0)
rect2_color = (0, 0, 255)

selected_rect = None  # rect was clicked or dragged
clicked_rect = None  # rect was clicked, not dragged
dragging = False
click_threshold = 10
start_pos = None

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            start_pos = event.pos  # Store initial mouse position
            if selected_rect:
                if selected_rect.collidepoint(event.pos):
                    print("clicked on selected rect")
                else:
                    pass
            # handle what was clicked on
            if rect1.collidepoint(event.pos):
                print("selected rect1")
                selected_rect = rect1
            if rect2.collidepoint(event.pos):
                print("selected rect2")
                selected_rect = rect2
            dragging = False  # Reset dragging flag

        if event.type == pygame.MOUSEMOTION:
            if start_pos and selected_rect:
                # Calculate distance from start position
                dx, dy = event.pos[0] - start_pos[0], event.pos[1] - start_pos[1]
                if (dx**2 + dy**2) > click_threshold**2:  # Pythagorean distance
                    dragging = True  # Start dragging if threshold exceeded, offset included
                    selected_rect.topleft = (event.pos[0] - selected_rect.width // 2, event.pos[1] - selected_rect.height // 2)

        if event.type == pygame.MOUSEBUTTONUP:
            if not dragging:
                # If no drag occurred, treat as click
                if selected_rect:
                    if selected_rect.collidepoint(event.pos):
                        print("clicked on a rect")
                        clicked_rect = selected_rect
                    else:
                        print("unselected rect")
                        selected_rect = None
                        clicked_rect = None
                else:
                    print("clicked board")
            else:
                print("ended drag")
            dragging = False  # Reset dragging
            start_pos = None  # Clear start_pos to prevent unintended behavior


    # Drawing
    screen.fill((255, 255, 255))  # Clear screen
    if rect1 == clicked_rect:
        rect1_color = (0, 255, 0)
    else:
        rect1_color = (255, 0, 0)
    if rect2 == clicked_rect:
        rect2_color = (0, 255, 0)
    else:
        rect2_color = (255, 0, 0)

    pygame.draw.rect(screen, rect1_color, rect1)  # Draw rectangle
    pygame.draw.rect(screen, rect2_color, rect2)  # Draw rectangle
    pygame.display.flip()  # Update display
    clock.tick(60)  # Cap frame rate
