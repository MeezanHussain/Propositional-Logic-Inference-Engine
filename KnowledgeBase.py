import re
from itertools import product


class KnowledgeBase:
    def __init__(self, sentences, asked):
        self.sentences = sentences
        self.propositional_symbols = self.extract_symbols()
        self.operators = self.extract_operators()
        self.asked = asked

    def extract_symbols(self):
        sentences_string = str(self.sentences)
        pattern = r'\b[a-zA-Z]+\d*\b'
        duplicate_proposition_symbols = re.findall(pattern, sentences_string)
        proposition_symbols = []
        for symbol in duplicate_proposition_symbols:
            if symbol not in proposition_symbols:
                proposition_symbols.append(symbol)
        return proposition_symbols

    def extract_operators(self):
        sentences_string = str(self.sentences)
        pattern = r'~|&|\|\||=>|<=>'
        operators = re.findall(pattern, sentences_string)
        return operators
