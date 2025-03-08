# =-- Dependencies --= #
import gpiozero
import time

# =-- Morse Code Tree --= #
MorseCodeDict = {
    'A': '.-', 'B': '-...', 'C': '-.-.',
    'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..',
    'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-',
    'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', ',': '--.--'
}

class Node:
    def __init__(self, value=None):
        self.value = value
        self.left = None
        self.right = None


class MorseCodeTree:
    def __init__(self):
        self.root = Node()  # Empty root node

    def populate_tree(self):
        """
        Iterates through the MorseCodeDict and populates the tree with nodes.
        :return:
        """
        for EnglishChar, MorseCode in MorseCodeDict.items():
            current = self.root  # Set current reference
            for mark in MorseCode:
                # Create new node if it does not already exist
                # Set new current reference
                match mark:
                    case '.':
                        # Left branch
                        if not current.left:
                            current.left = Node()
                        current = current.left
                    case '-':
                        # Right branch
                        if not current.right:
                            current.right = Node()
                        current = current.right

            # Set the node value to its decoded English character
            current.value = EnglishChar

    def decode(self, code):
        """
        Decodes a morse code string into English characters.
        :param code: Morse code string to decode
        :return:
        """
        words = code.split('/')  # Use / character to split individual words
        decoded_string = []  # Final decoded string

        # Iterate through each word (e.g. '.... . .-.. .-.. ---')
        for word in words:
            decoded_word = ""  # Final decoded individual word
            characters = word.split()  # Split word into characters

            # Iterate through each signal group (e.g. '.-..' or '-..')
            for SignalGroup in characters:
                current = self.root  # Current reference

                # Iterate through individual signal (i.e. '.' or '-')
                for signal in SignalGroup:
                    match signal:
                        case '.':
                            # Continue down left branch
                            if current.left:
                                current = current.left
                            else:
                                raise ValueError("Invalid morse code!")
                        case '-':
                            # Continue down right branch
                            if current.right:
                                current = current.right
                            else:
                                raise ValueError("Invalid morse code!")
                        case _:
                            raise ValueError(f"Invalid morse code signal: {signal}")

                # Append decoded English CHARACTER to full word
                decoded_word += current.value

            # Append decoded English WORD to full string
            decoded_string.append(decoded_word)

        # Return decoded string
        return " ".join(decoded_string)

def confirm_sequence(code, led: gpiozero.LED):
    """
    Flashes an LED on the Rpi to confirm a morse code sequence.
    :param led: The gpiozero LED
    :param code:
    The morse code sequence
    :return: None
    """
    dash_time = 2 # Dash duration
    dot_time = 0.25 # Dot duration
    signal_interval = 0.5 # Pause between signals
    word_interval = 1.5 # Pause between words
    words = code.split("/")
    for word in words:
        for signal in word:
            match signal:
                case '.':
                    led.on()
                    time.sleep(dot_time)
                    led.off()
                case '-':
                    led.on()
                    time.sleep(dash_time)
                    led.off()
            time.sleep(signal_interval) # Pause between signals
        time.sleep(word_interval) # Pause between words