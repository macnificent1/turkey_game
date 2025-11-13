import pygame
import random
import time

# --- Configuration Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TURKEY_SPEED_MIN = 1
TURKEY_SPEED_MAX = 3
SPAWN_RATE = 60  # Higher means slower spawn rate
GRAVITY = 0.5

# --- Pygame Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Turkey Drop Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# --- Load Images and Scale (Assuming images exist) ---
try:
    TURKEY_IMAGE_RAW = pygame.image.load('turkey.png').convert_alpha()
    COOKED_IMAGE_RAW = pygame.image.load('cooked.png').convert_alpha()
    # Scale images for reasonable size
    TURKEY_IMAGE = pygame.transform.scale(TURKEY_IMAGE_RAW, (60, 60))
    COOKED_IMAGE = pygame.transform.scale(COOKED_IMAGE_RAW, (60, 60))
except pygame.error as e:
    print(f"Error loading images: {e}")
    print("Please ensure 'turkey.png' and 'cooked.png' are in the script directory.")
    pygame.quit()
    exit()

# --- Game State Variables ---
score = 0
game_over = False
cook_mode_active = False
cook_mode_start_time = 0
cook_mode_button_visible = False
button_display_time = 0
button_rect = None
BUTTON_DURATION = 5  # seconds

class Turkey(pygame.sprite.Sprite):
    def __init__(self, cooked=False):
        super().__init__()
        self.cooked = cooked
        self.update_image()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = random.randint(TURKEY_SPEED_MIN, TURKEY_SPEED_MAX)
        self.points = 1 if not self.cooked else 2

    def update_image(self):
        """Sets the correct image and point value based on cooked status."""
        if self.cooked:
            self.image = COOKED_IMAGE
            self.points = 2
        else:
            self.image = TURKEY_IMAGE
            self.points = 1
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom >= SCREEN_HEIGHT:
            global game_over
            game_over = True
            # Stop falling off the screen once game over is triggered
            self.rect.bottom = SCREEN_HEIGHT

all_turkeys = pygame.sprite.Group()

def reset_game():
    """Resets all game state variables for a new round."""
    global score, game_over, cook_mode_active, cook_mode_start_time, cook_mode_button_visible, button_display_time, button_rect
    score = 0
    game_over = False
    cook_mode_active = False
    cook_mode_start_time = 0
    cook_mode_button_visible = False
    button_display_time = 0
    button_rect = None
    all_turkeys.empty()

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def create_cook_button():
    """Generates a random location for the COOK MODE button."""
    global button_rect, button_display_time, cook_mode_button_visible
    # Ensure button doesn't go off-screen (approx button size 150x50)
    x = random.randint(0, SCREEN_WIDTH - 150)
    y = random.randint(50, SCREEN_HEIGHT - 100)
    button_rect = pygame.Rect(x, y, 150, 50)
    button_display_time = time.time()
    cook_mode_button_visible = True

# --- Main Game Loop ---
running = True
reset_game()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_over:
                if retry_button_rect.collidepoint(event.pos):
                    reset_game()
            else:
                # Handle turkey clicks
                clicked_turkeys = [s for s in all_turkeys if s.rect.collidepoint(event.pos)]
                for turkey in clicked_turkeys:
                    score += turkey.points
                    turkey.kill()
                
                # Handle button clicks
                if cook_mode_button_visible and button_rect.collidepoint(event.pos):
                    cook_mode_active = True
                    cook_mode_start_time = time.time()
                    cook_mode_button_visible = False
                    button_rect = None
                    # Convert all existing turkeys to cooked
                    for turkey in all_turkeys:
                        turkey.cooked = True
                        turkey.update_image()

    if not game_over:
        # --- Game Logic ---
        screen.fill((135, 206, 235))  # Sky blue background

        # 1. Spawning turkeys randomly
        if random.randint(0, SPAWN_RATE) == 0:
            new_turkey = Turkey(cooked=cook_mode_active)
            all_turkeys.add(new_turkey)

        # 2. Update and draw turkeys
        all_turkeys.update()
        all_turkeys.draw(screen)
        
        # 3. Check cook mode timing
        if cook_mode_active:
            if time.time() - cook_mode_start_time >= 10:
                cook_mode_active = False
                # Revert all existing turkeys back to normal
                for turkey in all_turkeys:
                    turkey.cooked = False
                    turkey.update_image()
        
        # 4. Manage 'COOK MODE' button appearance
        if not cook_mode_active and not cook_mode_button_visible:
            if random.randint(0, 500) == 0: # Random chance to make button appear
                create_cook_button()
        
        if cook_mode_button_visible:
            if time.time() - button_display_time >= BUTTON_DURATION:
                cook_mode_button_visible = False
                button_rect = None
            else:
                # Draw the button
                pygame.draw.rect(screen, (255, 100, 0), button_rect)
                draw_text("COOK MODE", font, (255, 255, 255), screen, button_rect.x + 10, button_rect.y + 15)

        # 5. Draw the "ground" (where turkeys cannot cross)
        pygame.draw.rect(screen, (34, 139, 34), (0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))

        # 6. Display Score and Status
        status_text = "COOK MODE: ACTIVE" if cook_mode_active else "Status: Normal"
        status_color = (255, 0, 0) if cook_mode_active else (0, 0, 0)
        draw_text(f"Score: {score}", font, (0, 0, 0), screen, 10, 10)
        draw_text(status_text, font, status_color, screen, 10, 40)

    else:
        # --- Game Over Screen ---
        screen.fill((220, 220, 220)) # Gray background for game over
        draw_text("GAME OVER", pygame.font.Font(None, 100), (255, 0, 0), screen, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100)
        draw_text(f"Final Score: {score}", font, (0, 0, 0), screen, SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2)
        
        # Retry Button
        retry_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 50, 150, 50)
        pygame.draw.rect(screen, (0, 200, 0), retry_button_rect)
        draw_text("Try Again?", font, (255, 255, 255), screen, retry_button_rect.x + 15, retry_button_rect.y + 15)

    # Update the display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()