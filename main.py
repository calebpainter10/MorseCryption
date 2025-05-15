# =-- Dependencies --= #
from db.db import (list_all_messages, verify_client_by_id, verify_client_by_name, list_clients, list_clients_messages, \
    get_client_by_name, get_client_by_id, get_message_by_id)
from util.crypto_utils import hash_sha512, decrypt
from util.morse_utils import MorseCodeTree
from time import time, sleep
from client import Client
import gpiozero

# =-- Constant Settings --= #
active = True

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

# =-- Main Functions --= #
def authentication_flow():
    client1 = None
    client2 = None

    while True:
        client1_name = input("What would you like to call Client 1?")
        client1_master_password = input(f"What would you like to set as {client1_name}'s master password?")
        client1_enckey, client1_authkey = hash_sha512(client1_master_password)

        if get_client_by_name(client1_name):
            if not verify_client_by_name(client1_name, client1_authkey):
                print("Client 1 unable to be authenticated.")
                continue

        client2_name = input("What would you like to call Client 2?")
        client2_master_password = input(f"What would you like to set as {client2_name}'s master password?")
        client2_enckey, client2_authkey = hash_sha512(client2_master_password)

        if get_client_by_name(client2_name):
            if not verify_client_by_name(client2_name, client2_authkey):
                print("Client 1 password incorrect.")
                continue

        client1 = Client(client1_name, client1_enckey, client1_authkey)
        client2 = Client(client2_name, client2_enckey, client2_authkey)

        break

    connection_flow(client1, client2)

def database_flow():
    global active
    print("Welcome to the messaging logging database!")
    while active:
        print("""
        Options:
        1. List time log of all messages
        2. List all clients
        3. List time log of all messages from specific client
        4. Search client by name/ID
        5. Search and decrypt message by ID
        """)
        choice = input("Enter your choice: ")

        if choice == '1': # List time log of all messages
            messages = list_all_messages()
            for message in messages:
                print(
                    f"ID: {message.id} | Direction: {message.direction} | "
                    f"Sender ID: {message.sender_id} | Receiver ID: {message.receiver_id} |"
                    f" Timestamp: {message.timestamp}")
            sleep(3)

        elif choice == '2': # List all clients
            clients = list_clients()
            for client in clients:
                print(f"ID: {client.id} | Name: {client.name}")
            sleep(3)

        elif choice == '3': # List messages time log for specific client
            client_name = input("What is the name of the client you would like to query? ")
            client = get_client_by_name(client_name)

            if not client:
                print("Client not found.")
                continue

            messages = list_clients_messages(client)
            for message in messages:
                print(
                    f"ID: {message.id} | Direction: {message.direction} | "
                    f"Sender ID: {message.sender_id} | Receiver ID: {message.receiver_id} |"
                    f" Timestamp: {message.timestamp}")
                sleep(3)

        elif choice == '4': # Search client by name or id
            name_or_id = input("Would you like to search client by name (1) or ID (2)? ")
            if name_or_id == '1': # Name
                client_name = input("What is the name of the client you would like to query? ")
                client = get_client_by_name(client_name)

                if client is None:
                    print("Client not found.")
                    continue

                print(f"ID: {client.id} | Name: {client.name}")
            elif name_or_id == '2': # ID
                client_id = int(input("What is the ID of the client you would like to query? "))
                client = get_client_by_id(client_id)

                if client is None:
                    print("Client not found.")
                    continue

                print(f"ID: {client.id} | Name: {client.name}")
            else:
                print("Choice not recognized.")
                continue

            sleep(3)

        elif choice == '5': # Search and decrypt message by ID
            message_id = int(input("What is the ID of the message you would like to query? "))
            message = get_message_by_id(message_id)

            if message is None:
                print("Message not found.")
                continue

            db_receiver = get_client_by_id(message.receiver_id)

            print(f"The receiving client of the message is {db_receiver.name}")

            master_password = input("What is the master password of the *recipient* for the message you would like to decrypt? ")
            k_enc, k_auth = hash_sha512(master_password)

            verified = verify_client_by_id(message.receiver_id, k_auth)

            if not verified:
                print("Verification failed.")
                continue

            decrypted_message = decrypt(message.content, message.iv, k_enc)
            print(f"Decrypted message: {decrypted_message}")

            sleep(3)


def connection_flow(sending_client, receiving_client):
    global active
    print(f"[CONNECTION HANDLER] {sending_client.name} and {receiving_client.name} are connected.")

    morse_tree = MorseCodeTree()
    morse_tree.populate_tree()

    while active:
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

def main():
    while True:
        mode_selection = input("Would you like to view stored messages (enter 1) or establish a connection (enter 2)?")
        if mode_selection == '1':
            database_flow()
        elif mode_selection == '2':
            authentication_flow()
        else:
            print("Invalid input.")


main()