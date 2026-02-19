import random
import string
from abc import ABC, abstractmethod
from typing import List, Optional

import nltk

nltk.download('words')


class PasswordGenerator(ABC):
    """
    Base class for generating passwords.
    """
    @abstractmethod
    def generate(self) -> str:
        """
        Subclasses should override this method to generate password.
        """
        pass


class RandomPasswordGenerator(PasswordGenerator):
    """
    Class to generate a random password.
    """
    def __init__(self, length: int = 8, include_uppercase: bool = True, include_lowercase: bool = True, include_numbers: bool = False, include_symbols: bool = False, exclude_similar: bool = False, no_repeated_characters: bool = False):
        self.length = length
        self.no_repeated_characters = no_repeated_characters
        self.characters: str = ""
        if include_uppercase:
            self.characters += string.ascii_uppercase
        if include_lowercase:
            self.characters += string.ascii_lowercase
        if include_numbers:
            self.characters += string.digits
        if include_symbols:
            self.characters += string.punctuation
        
        # Exclude visually similar characters: O, 0, l, 1, I
        if exclude_similar:
            similar_chars = "O0l1I"
            self.characters = "".join(char for char in self.characters if char not in similar_chars)

    def generate(self) -> str:
        """
        Generate a password from specified characters.
        """
        if self.no_repeated_characters:
            if self.length > len(self.characters):
                raise ValueError(f"Cannot generate password with {self.length} unique characters from a pool of {len(self.characters)} characters.")
            return ''.join(random.sample(self.characters, self.length))
        else:
            return ''.join(random.choice(self.characters) for _ in range(self.length))


class MemorablePasswordGenerator(PasswordGenerator):
    """
    Class to generate a memorable password.
    """
    def __init__(
        self,
        no_of_words: int = 5,
        separator: str = "-",
        capitalization: bool = False,
        vocabulary: Optional[List[str]] = None,
        suffix_length: int = 0,
        rng_seed: Optional[int] = None,
    ):
        if vocabulary is None:
            vocabulary = nltk.corpus.words.words()

        self.no_of_words: int = no_of_words
        self.separator: str = separator
        # if True, capitalize first letter of each word
        self.capitalization: bool = capitalization
        self.suffix_length: int = max(0, int(suffix_length))
        self.vocabulary: List[str] = vocabulary

        # Use an independent RNG seeded at construction so the generator is deterministic
        # per instance (useful when stored in session state)
        if rng_seed is None:
            rng_seed = random.SystemRandom().randint(0, 2**64 - 1)
        self._rng = random.Random(rng_seed)

    def generate(self) -> str:
        """
        Generate a password from a list of vocabulary words.
        """
        password_words = [self._rng.choice(self.vocabulary) for _ in range(self.no_of_words)]

        if self.capitalization:
            # Capitalize first letter of each word for readability
            password_words = [w.capitalize() for w in password_words]

        password = self.separator.join(password_words)

        if self.suffix_length > 0:
            suffix = ''.join(self._rng.choice(string.digits) for _ in range(self.suffix_length))
            password = f"{password}{suffix}"

        return password


class PinCodeGenerator(PasswordGenerator):
    """
    Class to generate a numeric pin code.
    """
    def __init__(self, length: int = 4):
        self.length: int = length

    def generate(self) -> str:
        """
        Generate a numeric pin code.
        """
        # Block common or insecure PINs and avoid sequential/repeating digits
        blocked = {"1234", "0000", "1111", "2580"}

        def is_repeating(pin: str) -> bool:
            return len(set(pin)) == 1

        def is_sequential(pin: str) -> bool:
            # detect strictly ascending or descending by 1 (no wrap)
            if len(pin) < 2:
                return False
            diffs = [int(pin[i+1]) - int(pin[i]) for i in range(len(pin)-1)]
            return all(d == 1 for d in diffs) or all(d == -1 for d in diffs)

        max_attempts = 1000
        for _ in range(max_attempts):
            pin = ''.join(random.choice(string.digits) for _ in range(self.length))
            if pin in blocked:
                continue
            if is_repeating(pin):
                continue
            if is_sequential(pin):
                continue
            return pin

        raise ValueError(f"Unable to generate a secure PIN after {max_attempts} attempts. Try a different length.")
