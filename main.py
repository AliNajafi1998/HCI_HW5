import spotipy
import cv2
import mediapipe as mp
import tkinter as tk
import math
import time
from config import client_secret, client_id, redirect_uri
from spotify_controller import SpotifyController
from shazam_controller import shazam_controller
import threading

# Initialize controllers
spotify = SpotifyController(client_id, client_secret, redirect_uri)
shazam = shazam_controller()

# Global variables for displaying messages
message_duration = 10  # Duration to display the message in seconds
message_display_time = 0  # Timestamp when the message should disappear
message_text = ""  # The message to display

# Get screen dimensions using Tkinter
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Define the size of the OpenCV window
window_width = int(2 * screen_width / 3)
window_height = int(4 * screen_height / 5)

# Calculate the position to center the window
window_x = int((screen_width - window_width) / 2)
window_y = int((screen_height - window_height) / 2)

# Open the camera
cap = cv2.VideoCapture(0)

# Set camera resolution (Optional)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, window_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, window_height)

# OpenCV named window
cv2.namedWindow("Camera Feed", cv2.WINDOW_AUTOSIZE)
cv2.moveWindow("Camera Feed", window_x, window_y)
root.resizable(False, False)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

button_width = 150
button_height = 100

# Define buttons relative to the OpenCV window
buttons = {
    "Find": (int(1 * screen_width / 10), 10, int(1 * screen_width / 10) + button_width, 10 + button_height),
    "Play": (int(2 * screen_width / 10), 10, int(2 * screen_width / 10) + button_width, 10 + button_height),
    "Pause": (int(3 * screen_width / 10), 10, int(3 * screen_width / 10) + button_width, 10 + button_height),
    "Next": (int(4 * screen_width / 10), 10, int(4 * screen_width / 10) + button_width, 10 + button_height),
    "Prev": (int(5 * screen_width / 10), 10, int(5 * screen_width / 10) + button_width, 10 + button_height),  
}

def is_cursor_hovering(cursor_pos, button):
    """
    Check if the cursor is hovering over a button.
    """
    x1, y1, x2, y2 = button
    cursor_x, cursor_y = cursor_pos
    return x1 <= cursor_x <= x2 and y1 <= cursor_y <= y2

# Track the state of the pinch gesture
is_pinching = False
last_trigger_time = 0  # Timestamp of the last triggered event
cooldown_period = 0.5  # Cooldown period in seconds

def detect_pinch(landmarks):
    """
    Detect a pinching gesture based on the distance between the thumb and index fingertips.
    """
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    
    # Calculate Euclidean distance
    distance = math.sqrt((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2)
    
    # Define a threshold for the pinch
    return distance < 0.03

last_clicked_button = None

def handle_pinch_event(button_name):
    global last_clicked_button, message_text, message_display_time
    """
    Handle the pinch event and trigger button actions.
    """
    global last_trigger_time
    current_time = time.time()

    # Check if enough time has passed since the last event
    if current_time - last_trigger_time > cooldown_period:
        print(f"{button_name} button clicked")
        last_clicked_button = button_name  # Store the clicked button name
        if button_name == "Find":
            print("Recognizing Track...")

            # Show "Listening ..." message immediately when the button is clicked
            message_text = "Listening ..."
            message_display_time = time.time() + message_duration

            def play_the_song_on_spotify():
                global message_text, message_display_time
                song_details = shazam.listen_and_recognize()
                if song_details:
                    print(f"Recognized Song: {song_details['track']} by {song_details['artist']}")
                    search_query = f"{song_details['track']} {song_details['artist']}"
                    spotify.play_search_result(search_query)

                    # Show success message
                    message_text = f"Playing: {song_details['track']} by {song_details['artist']}"
                else:
                    print("Could not recognize the song.")
                    # Show error message
                    message_text = "Song not recognized."

                # Extend message display time after recognition
                message_display_time = time.time() + message_duration

            thread = threading.Thread(target=play_the_song_on_spotify)
            thread.start()

        elif button_name == "Play":
            print("Play")
            spotify.play()
        elif button_name == "Pause":
            print("Pause")
            spotify.pause()
        elif button_name == "Next":
            print("Next")
            spotify.next_track()
        elif button_name == "Prev":  # Handle the Previous Track button
            print("Previous Track")
            spotify.previous_track()

        # Update the last trigger time
        last_trigger_time = current_time

index_finger_color = mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=6, circle_radius=5)  # Green
default_color = mp.solutions.drawing_utils.DrawingSpec(color=(255, 255, 255), thickness=3, circle_radius=2)  # White

def draw_landmarks_with_custom_color(frame, hand_landmarks):
    # Draw connections and landmarks for the whole hand
    mp_drawing.draw_landmarks(
        frame,
        hand_landmarks,
        mp_hands.HAND_CONNECTIONS,
        default_color,  # Default style for connections
        default_color   # Default style for landmarks
    )

    # Highlight the index finger landmarks with custom color
    index_finger_landmarks = [4, 8]  # Index finger landmarks in MediaPipe Hands
    for idx in index_finger_landmarks:
        landmark = hand_landmarks.landmark[idx]
        x = int(landmark.x * frame.shape[1])
        y = int(landmark.y * frame.shape[0])
        cv2.circle(frame, (x, y), index_finger_color.circle_radius, index_finger_color.color, -1)

# Inside the main loop
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame for intuitive movement and convert to RGB
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe Hands
    results = hands.process(rgb_frame)

    # Get cursor position
    cursor_pos = (0, 0)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            draw_landmarks_with_custom_color(frame, hand_landmarks)

            # Get the index fingertip coordinates
            index_finger_tip = hand_landmarks.landmark[8]
            cursor_x = int(index_finger_tip.x * frame.shape[1])  # Use frame width
            cursor_y = int(index_finger_tip.y * frame.shape[0])  # Use frame height
            cursor_pos = (cursor_x, cursor_y)

            # Detect pinching gesture and perform button actions
            is_currently_pinching = detect_pinch(hand_landmarks.landmark)

            if is_currently_pinching and not is_pinching:
                # Pinch detected (transition from not pinching to pinching)
                for button_name, button_coords in buttons.items():
                    if is_cursor_hovering(cursor_pos, button_coords):
                        handle_pinch_event(button_name)

            # Update the pinching state
            is_pinching = is_currently_pinching

    # Draw buttons on the frame
    for button_name, (x1, y1, x2, y2) in buttons.items():
        color = (150, 150, 150)  # Default button color
        if is_cursor_hovering(cursor_pos, (x1, y1, x2, y2)):
            color = (255, 255, 0)  # Change color to cyan when hovered
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, -1)
        cv2.putText(frame, button_name, (x1 + (button_width // 3 - 2), y1 + (button_height // 2 - 2)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    # Display the message if it should be shown
    if time.time() < message_display_time:
        cv2.putText(frame, message_text, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the last clicked button on the screen
    if last_clicked_button:
        cv2.putText(frame, f"{last_clicked_button}", 
                    (100, 1000), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Display the frame
    cv2.imshow("Camera Feed", frame)

    # Break on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
