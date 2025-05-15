# =-- Dependencies --= #
from db.db import create_or_get_client, create_message
from util.morse_utils import confirm_sequence, MorseCodeTree
from util.crypto_utils import encrypt, decrypt
import gpiozero

# =-- Static Key --= #
KEY = b'pGpzH4eWEfjn30EIR40DPA=='

# =-- Client Class --= #
class Client:
    def __init__(self, name, private_key_b64, auth_key_b64):
        self.name = name
        self.inbox = []
        self.running = True
        self.key = private_key_b64
        self.auth_key = auth_key_b64
        self.morse_code_tree = MorseCodeTree()
        self.morse_code_tree.populate_tree()

        create_or_get_client(name, auth_key_b64) # Create client in DB if it does not already exist

    def send(self, recipient, plaintext_message, led):
        """
        Sends a message to the recipient.
        :param recipient: A recipient object of class Client
        :param plaintext_message: The plaintext message contents.
        :param led: The LED to verify.
        :return: None
        """
        print(f"[ENCRYPTION/DECRYPTION HANDLER] Encrypting outgoing message from {self.name} to {recipient.name}")
        iv, encrypted_message = encrypt(plaintext_message, recipient.key) # Encrypt using recipient's key
        print(f"[ENCRYPTION/DECRYPTION HANDLER] Encrypted outgoing message from {self.name} to {recipient.name}: {encrypted_message}")
        recipient.receive(self, encrypted_message, iv, led)

    def receive(self, sender, message, iv, led: gpiozero.LED):
        """
        Adds a message to the inbox.
        :param sender: The sender object of class Client.
        :param message: The message contents.
        :param iv: The initial initialization vector.
        :param led: The LED to verify.
        :return: None
        """
        receiver_client = create_or_get_client(self.name, self.auth_key)
        sender_client = create_or_get_client(sender.name, sender.auth_key)

        create_message(message, "sent", sender_client.id, receiver_client.id, self.auth_key, iv)

        self.inbox.append((sender, message, iv, led))
        self.process_inbox()

    def process_inbox(self):
        if self.inbox:  # If there are many messages
            for sender, message, iv, led in self.inbox:  # Log messages
                print(f"[MESSAGE HANDLER] ({self.name} -> {sender.name}) | {message}")
                print(f"[ENCRYPTION/DECRYPTION HANDLER] Decrypting incoming message from {sender.name}...")
                try:
                    decrypted_message = decrypt(message, iv, self.key)
                    print(
                        f"[ENCRYPTION/DECRYPTION HANDLER] {self.name} decrypted incoming message from {sender.name}: {decrypted_message}")
                    print("[ENCRYPTION/DECRYPTION HANDLER] Confirming sequence on LED.")
                    confirm_sequence(decrypted_message, led)

                    decoded_message = self.morse_code_tree.decode(decrypted_message)
                    print(f"[ENCRYPTION/DECRYPTION HANDLER] Decoded message from  {sender.name}: {decoded_message}")
                except Exception as e:
                    print("[ENCRYPTION/DECRYPTION HANDLER] Error: ", e)
            self.inbox.clear()  # Delete the processed messages