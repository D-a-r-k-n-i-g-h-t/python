import pygame
import sys
import math

pygame.init()

# --------------------
# Display & Colors
# --------------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Football Tactical Board")

# Colors
WHITE      = (255, 255, 255)
BLACK      = (0, 0, 0)
GREEN      = (0, 128, 0)    # Field color
BLUE       = (0, 0, 255)    # Team 1
RED        = (255, 0, 0)    # Team 2
YELLOW     = (255, 255, 0)
LIGHT_GRAY = (200, 200, 200)

# --------------------
# Global variables & settings
# --------------------
toolbar_height = 50

# Define the field rectangle (inside margins)
field_margin = 0
field_rect = pygame.Rect(field_margin, field_margin + toolbar_height,
                           WIDTH - 2 * field_margin, HEIGHT - 2 * field_margin - toolbar_height)

# Store players as dictionaries with position and team color.
# For simplicity, we place team1 on the left half and team2 on the right half.
team1_players = []
team2_players = []
player_radius = 10

# Set up 11 players per team (positions chosen arbitrarily within the field)
for i in range(11):
    # Spread players vertically in team 1
    x = field_rect.x + field_rect.width * 0.25
    y = field_rect.y + 30 + i * ((field_rect.height - 60) / 10)
    team1_players.append({"pos": [x, y], "color": BLUE})
    
    # Spread players vertically in team 2
    x2 = field_rect.x + field_rect.width * 0.75
    y2 = field_rect.y + 30 + i * ((field_rect.height - 60) / 10)
    team2_players.append({"pos": [x2, y2], "color": RED})

# Combine players in one list for easier processing
players = team1_players + team2_players

# Create a ball object that can be moved
ball = {"pos": list(field_rect.center), "radius": 7}

# Variables for dragging objects (players or ball)
selected_player = None  # holds a reference to a player dictionary
selected_ball = None    # holds the ball if it is selected

# --------------------
# Tactical Drawing Mode
# --------------------
# Modes: None, "draw_rect", "draw_line"
tactical_mode = None
tactical_start = None  # starting point of the shape (when mouse button pressed)
tactical_shapes = []   # list to store drawn shapes; each is a dict: {type, start, end, color}

# Toolbar buttons: define two simple buttons for "Rect" and "Line"
button_rect = pygame.Rect(10, 10, 80, 30)
button_line = pygame.Rect(100, 10, 80, 30)

# --------------------
# Helper Functions
# --------------------
def draw_field():
    """Draw the football field inside a green rectangle with white lines."""
    # Field background
    pygame.draw.rect(screen, GREEN, field_rect)
    # Field boundary
    pygame.draw.rect(screen, WHITE, field_rect, 3)
    # Center line
    pygame.draw.line(screen, WHITE,
                     (field_rect.centerx, field_rect.top),
                     (field_rect.centerx, field_rect.bottom), 2)
    # Center circle (outline)
    center = field_rect.center
    pygame.draw.circle(screen, WHITE, center, 60, 2)
    # Penalty areas
    left_penalty = pygame.Rect(field_rect.left, field_rect.top + field_rect.height * 0.2,
                               100, field_rect.height * 0.6)
    pygame.draw.rect(screen, WHITE, left_penalty, 2)
    right_penalty = pygame.Rect(field_rect.right - 100, field_rect.top + field_rect.height * 0.2,
                                100, field_rect.height * 0.6)
    pygame.draw.rect(screen, WHITE, right_penalty, 2)
    # D areas (arcs)
    left_center = (field_rect.left + 100, field_rect.top + field_rect.height * 0.5)
    rect_arc = pygame.Rect(left_center[0] - 60, left_center[1] - 60, 120, 120)
    pygame.draw.arc(screen, WHITE, rect_arc, math.radians(270), math.radians(90), 2)
    right_center = (field_rect.right - 100, field_rect.top + field_rect.height * 0.5)
    rect_arc2 = pygame.Rect(right_center[0] - 60, right_center[1] - 60, 120, 120)
    pygame.draw.arc(screen, WHITE, rect_arc2, math.radians(90), math.radians(270), 2)
    # Goal posts
    goal_width = 60
    goal_depth = 10
    left_goal = pygame.Rect(field_rect.left - goal_depth, field_rect.centery - goal_width // 2,
                            goal_depth, goal_width)
    pygame.draw.rect(screen, WHITE, left_goal, 2)
    right_goal = pygame.Rect(field_rect.right, field_rect.centery - goal_width // 2,
                             goal_depth, goal_width)
    pygame.draw.rect(screen, WHITE, right_goal, 2)

def draw_players():
    """Draw all players as filled circles."""
    for p in players:
        pos = (int(p["pos"][0]), int(p["pos"][1]))
        pygame.draw.circle(screen, p["color"], pos, player_radius)

def fill_circle(cx, cy, radius):
    """
    Draw a filled circle using a modified Midpoint Circle Algorithm.
    For each calculated edge point, draw horizontal lines between symmetric points.
    """
    x = 0
    y = radius
    p = 1 - radius

    while x <= y:
        # Draw horizontal lines to fill the circle
        pygame.draw.line(screen, WHITE, (cx - x, cy - y), (cx + x, cy - y))
        pygame.draw.line(screen, WHITE, (cx - x, cy + y), (cx + x, cy + y))
        pygame.draw.line(screen, WHITE, (cx - y, cy - x), (cx + y, cy - x))
        pygame.draw.line(screen, WHITE, (cx - y, cy + x), (cx + y, cy + x))
        
        if p < 0:
            p += 2 * x + 3
        else:
            p += 2 * (x - y) + 5
            y -= 1
        x += 1

def draw_ball():
    """Draw the soccer ball (a filled white circle) using the modified Midpoint Circle Algorithm."""
    fill_circle(ball["pos"][0], ball["pos"][1], ball["radius"])

def draw_arrow_line(surface, color, start, end, width=2, arrow_size=10, arrow_angle=math.radians(30)):
    """
    Draws a line from start to end with an arrowhead at the end.
    - width: thickness of the line.
    - arrow_size: length of the arrowhead sides.
    - arrow_angle: angle (in radians) between the line and each side of the arrowhead.
    """
    # Draw the main line
    pygame.draw.line(surface, color, start, end, width)
    # Compute the angle of the line
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    # Calculate the two arrowhead points
    left = (end[0] - arrow_size * math.cos(angle - arrow_angle),
            end[1] - arrow_size * math.sin(angle - arrow_angle))
    right = (end[0] - arrow_size * math.cos(angle + arrow_angle),
             end[1] - arrow_size * math.sin(angle + arrow_angle))
    # Draw a filled polygon for the arrowhead
    pygame.draw.polygon(surface, color, [end, left, right])

def draw_tactical_shapes():
    """Draw any tactical shapes (rectangles or lines with arrowhead) that were added."""
    for shape in tactical_shapes:
        if shape["type"] == "rect":
            x1, y1 = shape["start"]
            x2, y2 = shape["end"]
            rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
            pygame.draw.rect(screen, shape["color"], rect, 2)
        elif shape["type"] == "line":
            # Draw a line with an arrowhead
            draw_arrow_line(screen, shape["color"], shape["start"], shape["end"], 2, 10, math.radians(30))

def draw_toolbar():
    """Draw the toolbar with buttons."""
    toolbar_rect = pygame.Rect(0, 0, WIDTH, toolbar_height)
    pygame.draw.rect(screen, LIGHT_GRAY, toolbar_rect)
    
    # Draw the "Rect" button
    pygame.draw.rect(screen, (100, 200, 100), button_rect)
    font = pygame.font.SysFont(None, 20)
    text = font.render("Rect", True, BLACK)
    screen.blit(text, (button_rect.x + 10, button_rect.y + 5))
    
    # Draw the "Line" button
    pygame.draw.rect(screen, (200, 100, 100), button_line)
    text2 = font.render("Line", True, BLACK)
    screen.blit(text2, (button_line.x + 10, button_line.y + 5))

# --------------------
# Main Loop
# --------------------
clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)  # 60 FPS
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Mouse button down events
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # Check if click was on toolbar buttons first:
            if button_rect.collidepoint(mouse_pos):
                tactical_mode = "rect"
                tactical_start = None  # reset any previous shape
                continue
            elif button_line.collidepoint(mouse_pos):
                tactical_mode = "line"
                tactical_start = None
                continue
            # Otherwise, if click is inside the field:
            if field_rect.collidepoint(mouse_pos):
                if tactical_mode:
                    tactical_start = mouse_pos
                else:
                    # First check if the ball was clicked
                    if math.hypot(mouse_pos[0] - ball["pos"][0], mouse_pos[1] - ball["pos"][1]) <= ball["radius"]:
                        selected_ball = ball
                    else:
                        # Check if a player was clicked (using distance to center)
                        for p in players:
                            if math.hypot(mouse_pos[0] - p["pos"][0], mouse_pos[1] - p["pos"][1]) <= player_radius:
                                selected_player = p
                                break
        
        # Mouse motion events (dragging objects)
        elif event.type == pygame.MOUSEMOTION:
            new_x, new_y = event.pos
            if selected_ball is not None:
                # Optionally, constrain ball inside the field
                if field_rect.collidepoint(new_x, new_y):
                    ball["pos"] = [new_x, new_y]
            elif selected_player is not None:
                if field_rect.collidepoint(new_x, new_y):
                    selected_player["pos"] = [new_x, new_y]
        
        # Mouse button up events
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = pygame.mouse.get_pos()
            if tactical_mode and tactical_start:
                shape = {"type": tactical_mode, "start": tactical_start, "end": mouse_pos, "color": WHITE}
                tactical_shapes.append(shape)
                tactical_start = None
                tactical_mode = None
            # Deselect objects after dragging
            selected_ball = None
            selected_player = None
    
    # --------------------
    # Drawing
    # --------------------
    screen.fill(WHITE)  # Background
    
    draw_toolbar()          # Toolbar and buttons
    draw_field()            # Field and markings
    draw_tactical_shapes()  # Tactical shapes, if any
    draw_players()          # Players
    draw_ball()             # Draw the ball
    
    # Optional: preview tactical shape while drawing
    if tactical_mode and tactical_start:
        current_pos = pygame.mouse.get_pos()
        if tactical_mode == "rect":
            x1, y1 = tactical_start
            x2, y2 = current_pos
            preview_rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
            pygame.draw.rect(screen, WHITE, preview_rect, 1)
        elif tactical_mode == "line":
            # Draw preview arrow line with a thinner width (1 pixel)
            draw_arrow_line(screen, WHITE, tactical_start, current_pos, 1, 10, math.radians(30))
    
    pygame.display.flip()

pygame.quit()
sys.exit()
