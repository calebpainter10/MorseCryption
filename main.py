# =-- Dependencies --= #
from util.morse_utils import MorseCodeTree
from time import time, sleep
from client import Client
import gpiozero

# =-- Constant Settings --= #
KEY_BYTES = b'\xa4js\x1f\x87\x96\x11\xf8\xe7\xdfA\x08G\x8d\x03<'
KEY_BASE64 = b'pGpzH4eWEfjn30EIR40DPA=='

connection_established = True

# =-- Hardware --= #
yellow_led = gpiozero.LED(14)
green_led = gpiozero.LED(15)
button = gpiozero.Button(18)

# =-- Input Morse Code --= #
def input_morse_code():
    listen = True

    print("You may input your morse code message using the Raspberry Pi button now.")
    input_code = []

    button_timer = 7
    kill_loop = 6
    wait_for_space = 3
    wait_for_press = 1

    while listen:
        # If button presses happen within 1 second of each other, add either a dot or dash
        # If the button is pressed between 3 and 6 seconds, add a space
        # If the button is idle for 7 seconds, stop listening for button presses
        # Timer to check when button got pressed
        start_time = time()
        button.wait_for_press(timeout=button_timer)
        elapsed_time = time() - start_time

        # Timer to check when button was released for dots and dashes
        pressed_time = time()
        button.wait_for_release()
        elapsed_pressed_time = time() - pressed_time

        if wait_for_space <= elapsed_time <= kill_loop:
            input_code.append(' ')

        # Quit if we time out
        if elapsed_time > kill_loop:
            listen = False

        # Only activate add dot if button is pressed less than 1 second
        elif elapsed_pressed_time < wait_for_press:
            input_code.append('.')
            print(input_code)
        else:
            input_code.append('-')
            print(input_code)

    return "".join(input_code)

# =-- Main Function --= #
def main():
    global connection_established
    client1_name = input("What would you like to call Client 1?")
    client1 = Client(client1_name, KEY_BASE64)

    client2_name = input("What would you like to call Client 2?")
    client2 = Client(client2_name, KEY_BASE64)

    sending_client = client1
    receiving_client = client2

    print(f"[CONNECTION HANDLER] {client1_name} and {client2_name} are connected.")

    morse_tree = MorseCodeTree()
    morse_tree.populate_tree()

    while connection_established:
        # Input morse code
        print("[CONNECTION HANDLER] You are currently: ", sending_client.name)
        morse_code = input_morse_code()

        # Process input
        print("[CONNECTION HANDLER] Reminder - you are currently: ", sending_client.name)
        print("Final morse code: ", morse_code)
        print("This message decodes in English to: ", morse_tree.decode(morse_code))

        # Encrypt and send message
        sending_client.send(receiving_client, morse_code, green_led)

        # Flip clients
        sending_client, receiving_client = receiving_client, sending_client

        print("[CONNECTION HANDLER] Message fully processed.")
        yellow_led.on()
        sleep(1)
        yellow_led.off()

main()