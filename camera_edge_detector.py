import Hobot.GPIO as GPIO
import cv2
import time
import os

# === Configuration ===
# Use BOARD mode pins for Hobot GPIO compatibility
LED_PIN = 31        # Physical pin 31 (was 33)
BUTTON_PIN = 13     # Physical pin 13

# === Setup ===
# Use BOARD mode instead of BCM for Hobot GPIO
GPIO.setmode(GPIO.BOARD)

# Add error handling for GPIO setup
try:
    GPIO.setup(LED_PIN, GPIO.OUT)
    print(f"LED pin {LED_PIN} setup successful")
except Exception as e:
    print(f"Error setting up LED pin {LED_PIN}: {e}")
    print("Trying alternative LED pins...")
    # Try common alternative pins
    for alt_pin in [29, 31, 33, 35, 37]:
        try:
            LED_PIN = alt_pin
            GPIO.setup(LED_PIN, GPIO.OUT)
            print(f"LED pin {LED_PIN} setup successful")
            break
        except:
            continue
    else:
        print("Could not setup any LED pin")
        exit(1)

try:
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PULL_DOWN)
    print(f"Button pin {BUTTON_PIN} setup successful")
except AttributeError:
    # If PULL_DOWN doesn't exist, try alternatives
    try:
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=0)  # 0 for pull-down
        print(f"Button pin {BUTTON_PIN} setup successful (using integer constant)")
    except:
        GPIO.setup(BUTTON_PIN, GPIO.IN)  # No pull resistor
        print(f"Button pin {BUTTON_PIN} setup successful (no pull resistor)")
except Exception as e:
    print(f"Error setting up button pin {BUTTON_PIN}: {e}")
    print("Trying alternative button pins...")
    # Try common alternative pins
    for alt_pin in [11, 13, 15, 16, 18]:
        try:
            BUTTON_PIN = alt_pin
            GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PULL_DOWN)
            print(f"Button pin {BUTTON_PIN} setup successful")
            break
        except:
            try:
                GPIO.setup(BUTTON_PIN, GPIO.IN)
                print(f"Button pin {BUTTON_PIN} setup successful (no pull resistor)")
                break
            except:
                continue
    else:
        print("Could not setup any button pin")
        exit(1)

# Create output directory if not exists
OUTPUT_DIR = "captured_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Camera could not be opened.")
    exit(1)

print(f"Ready to capture. Press the button on pin {BUTTON_PIN}!")
print(f"LED is on pin {LED_PIN}")

try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
            print("Button Pressed! Capturing...")

            GPIO.output(LED_PIN, GPIO.HIGH)  # Turn on LED
            
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame!")
                GPIO.output(LED_PIN, GPIO.LOW)
                continue
            
            # Generate unique filename using timestamp
            timestamp = int(time.time())
            original_filename = os.path.join(OUTPUT_DIR, f"image_{timestamp}.jpg")
            edges_filename = os.path.join(OUTPUT_DIR, f"edges_{timestamp}.jpg")
            
            # Save original
            cv2.imwrite(original_filename, frame)
            print(f"Saved original image as {original_filename}")
            
            # Convert to grayscale and apply Canny edge detector
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            cv2.imwrite(edges_filename, edges)
            print(f"Saved edges image as {edges_filename}")
            
            time.sleep(0.5)
            GPIO.output(LED_PIN, GPIO.LOW)  # Turn off LED

            # Wait for button release
            while GPIO.input(BUTTON_PIN) == GPIO.HIGH:
                time.sleep(0.1)

except KeyboardInterrupt:
    print("\nProgram interrupted by user")
except Exception as e:
    print(f"Runtime error: {e}")
finally:
    print("\nCleaning up...")
    cap.release()
    GPIO.cleanup()
    print("Done.")
