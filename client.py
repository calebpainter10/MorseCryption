# =-- Dependencies --= #
from util.crypto_utils import encrypt, decrypt
import asyncio

# =-- Static Key --= #
KEY = b'pGpzH4eWEfjn30EIR40DPA=='

# =-- Client Class --= #
class Client:
    def __init__(self, name, private_key_b64):
        self.name = name
        self.inbox = []
        self.running = True
        self.key = private_key_b64

        asyncio.create_task(self._message_loop()) # Immediately start inbox loop

    async def send(self, recipient, plaintext_message):
        """
        Sends a message to the recipient.
        :param recipient: A recipient object of class Client
        :param plaintext_message: The plaintext message contents.
        :return: None
        """
        iv, encrypted_message = encrypt(plaintext_message, self.key)
        recipient.receive(self.name, encrypted_message, iv)

    def receive(self, sender, message, iv):
        """
        Adds a message to the inbox.
        :param sender: The sender object of class Client.
        :param message: The message contents.
        :param iv: The initial initialization vector.
        :return: None
        """
        self.inbox.append((sender, message, iv))

    async def _message_loop(self):
        """
        Background async task loop to check for incoming messages
        :return:
        """
        while self.running:
            if self.inbox: # If there are many messages
                for sender, message, iv in self.inbox: # Log messages
                    print(f"[MESSAGE HANDLER] ({self.name} -> {sender}) | {message}")
                    print(f"[ENCRYPTION/DECRYPTION HANDLER] Decrypting incoming message from {sender}...")
                    try:
                        decrypted_message = decrypt(message, iv, self.key)
                        print(f"[ENCRYPTION/DECRYPTION HANDLER] {self.name} decrypted incoming message from {sender}: {decrypted_message}")
                    except Exception as e:
                        print("[ENCRYPTION/DECRYPTION HANDLER] Error: ", e)
                self.inbox.clear() # Delete the processed messages
            await asyncio.sleep(1)



async def main():
    client_a = Client("Client A", KEY)
    client_b = Client("Client B", KEY)

    await client_a.send(client_b, ".... . .-.. .-.. ---")
    await client_b.send(client_a, ".... . .-.. .-.. ---")

asyncio.run(main())