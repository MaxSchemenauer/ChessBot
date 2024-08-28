import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Initial Rectangle
rect = pygame.Rect(100, 100, 50, 50)
rect_color = (255, 0, 0)

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
            dragging = False  # Reset dragging flag

        if event.type == pygame.MOUSEMOTION:
            if start_pos:
                # Calculate distance from start position
                dx, dy = event.pos[0] - start_pos[0], event.pos[1] - start_pos[1]
                if (dx**2 + dy**2) > click_threshold**2:  # Pythagorean distance
                    dragging = True  # Start dragging if threshold exceeded
                    rect.topleft = (event.pos[0] - rect.width // 2, event.pos[1] - rect.height // 2)

        if event.type == pygame.MOUSEBUTTONUP:
            if not dragging:
                # If no drag occurred, treat as click
                if rect.collidepoint(event.pos):
                    rect_color = (0, 255, 0)  # Turn green on click
            dragging = False  # Reset dragging
            start_pos = None  # Clear start_pos to prevent unintended behavior

    # Drawing
    screen.fill((255, 255, 255))  # Clear screen
    pygame.draw.rect(screen, rect_color, rect)  # Draw rectangle
    pygame.display.flip()  # Update display
    clock.tick(60)  # Cap frame rate
