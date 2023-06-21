import cv2
from cvzone.HandTrackingModule import HandDetector
import random
import time

# Constants
GESTURE_TIMEOUT = 2  # Timeout in seconds
DISPLAY_DURATION = 2  # Duration to display the computer's move in seconds
OPTIONS = ["Rock", "Paper", "Scissors"]
SCORES = {"Win": 0, "Lose": 0, "Draw": 0}

# Function to display text on the image
def display_text(img, text, position, color):
    cv2.putText(
        img,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        color,
        2,
    )

# Function to determine the winner
def determine_winner(user_choice, computer_choice):
    if user_choice == computer_choice:
        return "Draw"
    elif (
        (user_choice == "Rock" and computer_choice == "Scissors")
        or (user_choice == "Scissors" and computer_choice == "Paper")
        or (user_choice == "Paper" and computer_choice == "Rock")
    ):
        return "Win"
    else:
        return "Lose"

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Failed to open camera.")
    exit()

detector = HandDetector(maxHands=1)
gesture_start_time = time.time()
display_start_time = time.time() - DISPLAY_DURATION  # Initialize the display start time
computer_choice = None
user_choice = None
invalid_gesture_start_time = None

while True:
    success, img = cap.read()
    if not success:
        print("Failed to read frame.")
        break

    hands, img = detector.findHands(img)  # with draw

    # Display score
    display_text(img, f"Scores: {SCORES}", (10, 30), (0, 255, 0))

    if hands:
        hand = hands[0]
        fingers = detector.fingersUp(hand)

        # Gesture detection
        if time.time() - gesture_start_time >= GESTURE_TIMEOUT:
            if computer_choice is None:
                computer_choice = random.choice(OPTIONS)
                display_start_time = time.time()

            if time.time() - display_start_time <= DISPLAY_DURATION:
                if user_choice is not None:
                    display_text(
                        img,
                        f"Computer's Choice: {computer_choice}",
                        (10, 70),
                        (0, 0, 255),
                    )
            else:
                if fingers == [0, 0, 0, 0, 0]:
                    user_choice = "Rock"
                elif fingers == [1, 1, 1, 1, 1]:
                    user_choice = "Paper"
                elif fingers == [0, 1, 1, 0, 0]:
                    user_choice = "Scissors"
                else:
                    user_choice = "Invalid Gesture"
                    invalid_gesture_start_time = time.time()

                if user_choice != "Invalid Gesture":
                    display_text(
                        img,
                        f"Your Choice: {user_choice}",
                        (10, 110),
                        (255, 0, 0),
                    )

                    # Determine the winner
                    if time.time() - display_start_time > DISPLAY_DURATION:
                        result = determine_winner(user_choice, computer_choice)
                        SCORES[result] += 1
                        display_text(
                            img,
                            f"Result: {result}",
                            (10, 150),
                            (0, 255, 0),
                        )

                        # Reset for the next round
                        computer_choice = None
                        gesture_start_time = time.time()

                else:
                    if invalid_gesture_start_time and time.time() - invalid_gesture_start_time <= 2:
                        display_text(
                            img,
                            "Invalid Gesture! Please try again.",
                            (10, 150),
                            (0, 0, 255),
                        )
                    else:
                        user_choice = None
                        invalid_gesture_start_time = None

        else:
            # Calculate the remaining time for the countdown
            countdown_time = GESTURE_TIMEOUT - (time.time() - gesture_start_time)
            display_text(
                img,
                f"Time: {countdown_time:.1f}s",
                (10, 190),
                (255, 255, 0),
            )

    cv2.imshow("Image", img)
    if cv2.waitKey(1) == ord("q"):  # Exit when 'q' is pressed
        break

cap.release()
cv2.destroyAllWindows()
