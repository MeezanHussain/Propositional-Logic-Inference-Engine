import re
from itertools import product


def extract_operators(sentence):
    sentences_string = str(sentence)
    pattern = r'=>|&|\||!'
    operators = re.findall(pattern, sentences_string)
    return operators


def extract_symbols(sentence):
    sentences_string = str(sentence)
    pattern = r'\b[a-zA-Z]+\d*\b'
    proposition_symbols = re.findall(pattern, sentences_string)
    return proposition_symbols


def parse_expression(expression):
    pattern = r'(~|&|\|\||=>|<=>|\(|\))|(\b[a-zA-Z0-9]+\b)'
    tokens = re.findall(pattern, expression)
    tokens = [t[0] if t[0] else t[1] for t in tokens]  # Flatten the list
    return tokens


def eval_expression(tokens, model):
    # Convert infix to postfix (Reverse Polish Notation) using the Shunting Yard Algorithm
    prec = {'~': 3, '&': 2, '||': 2, '=>': 1, '<=>': 1}
    assoc = {'~': 'R', '&': 'L', '||': 'L', '=>': 'L', '<=>': 'L'}
    stack = []
    output = []
    for token in tokens:
        if token in prec:  # Operator token
            while (stack and stack[-1] != '(' and
                   (prec[stack[-1]] > prec[token] or
                    (prec[stack[-1]] == prec[token] and assoc[token] == 'L'))):
                output.append(stack.pop())
            stack.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        else:
            output.append(token)  # Propositional symbol or constant

    while stack:
        output.append(stack.pop())

    # Evaluate the postfix expression using stack for logical operations
    stack = []
    for token in output:
        if token in prec:  # Handling operators with logical operations
            if token == '~':
                arg = stack.pop()
                stack.append(int(not arg))
            else:
                arg2 = stack.pop()
                arg1 = stack.pop()
                if token == '&':
                    stack.append(int(arg1 and arg2))
                elif token == '||':
                    stack.append(int(arg1 or arg2))
                elif token == '=>':
                    stack.append(int(not arg1 or arg2))
                elif token == '<=>':
                    stack.append(int((not arg1 or arg2) and (not arg2 or arg1)))
        else:
            stack.append(model[token])

    return stack.pop()


def check_lhs_in_queue(queue, lhs):
    for element in lhs:
        if element not in queue:
            return False
    return True


def is_sentence_true(sentence):
    if len(extract_symbols(sentence)) > 1:
        return False
    return True


def relational_number(queue, lhs):
    number = 0
    for element in lhs:
        if element in queue:
            number += 1
    return number


def get_sentence_lhs(sentence):
    sentence_list = extract_symbols(sentence)
    return sentence_list[:-1]


def get_sentence_rhs(sentence):
    sentence_list = extract_symbols(sentence)
    return sentence_list[-1]


def check_fc_combinations(queue, sentence_dict):
    for rhs, lhs in sentence_dict.items():
        if check_lhs_in_queue(queue=queue, lhs=lhs):
            return True
    return False


class Algorithms:
    def __init__(self, kb):
        self.model_binary_table = list()
        self.KB = kb

    def is_valid_ask(self):
        all_symbols_tell = []
        for sentence in self.KB.sentences:
            all_symbols_tell += extract_symbols(sentence)
        all_symbols_ask = extract_symbols(self.KB.asked)
        for symbol in all_symbols_ask:
            if symbol not in all_symbols_tell:
                return False
        return True

    def call_algorithm(self, algorithm_name):
        if len(self.KB.sentences) == 0:
            return "NO"
        if algorithm_name == "TT":
            return self.truth_table()
        elif algorithm_name == "FC":
            return self.forward_chaining()
        elif algorithm_name == "BC":
            return self.backward_chaining()
        else:
            return "Invalid Algorithm"

    def truth_table(self):
        if not self.is_valid_ask():
            return "NO"
        models = list(product([True, False], repeat=len(self.KB.propositional_symbols)))
        results = []
        for model in models:
            model_dict = dict(zip(self.KB.propositional_symbols, model))
            if all(eval_expression(parse_expression(sentence), model_dict) for sentence in self.KB.sentences):
                results.append(model_dict)
        entails = all(eval_expression(parse_expression(self.KB.asked), model) for model in results)
        return "YES: {}".format(len(results)) if entails else "NO"

    def forward_chaining(self):
        if not self.is_valid_ask():
            return "NO"
        separated_sentence_dict = dict()
        queue = []
        for sentence in self.KB.sentences:
            if is_sentence_true(sentence):
                queue.append(sentence)
            else:
                separated_sentence_dict[get_sentence_rhs(sentence)] = get_sentence_lhs(sentence)
        if len(queue) == 0:
            return "NO"
        continue_loop = True
        while continue_loop:
            inferred_new_sentence = False
            if not check_fc_combinations(queue, separated_sentence_dict) or self.KB.asked in queue:
                continue_loop = False
                continue
            for rhs, lhs in separated_sentence_dict.items():
                if check_lhs_in_queue(queue=queue, lhs=lhs):
                    if rhs == self.KB.asked:
                        queue.append(rhs)
                        continue_loop = False
                        break
                    if rhs not in queue:
                        queue.append(rhs)
                        inferred_new_sentence = True
            if not inferred_new_sentence:
                continue_loop = False
        solution = ""
        if self.KB.asked in queue:
            solution += f"YES: {', '.join(queue)}"
        else:
            solution += "NO"
        return solution

    def backward_chaining(self):
        if not self.is_valid_ask():
            return "NO"
        true_sentences = []
        evaluated_true_sentences = []
        for sentence in self.KB.sentences:
            if is_sentence_true(sentence):
                true_sentences.append(sentence)
        if len(true_sentences) == 0:
            return "NO"
        solution = ""
        if self.truth_value(true_sentences, self.KB.asked, evaluated_true_sentences) and len(
                evaluated_true_sentences) > 0:
            solution += f"YES: {', '.join(evaluated_true_sentences)}"
        else:
            solution += "NO"
        return solution

    def truth_value(self, true_sentences, symbol, evaluated_true_sentences):
        ans = True
        for sentence in self.KB.sentences:
            if get_sentence_rhs(sentence) == symbol:
                for lhs in get_sentence_lhs(sentence):
                    if get_sentence_rhs(sentence) in true_sentences:
                        if get_sentence_rhs(sentence) not in evaluated_true_sentences:
                            evaluated_true_sentences.append(get_sentence_rhs(sentence))
                    else:
                        ans &= self.truth_value(true_sentences, lhs, evaluated_true_sentences)
                if ans:
                    if get_sentence_rhs(sentence) not in evaluated_true_sentences:
                        evaluated_true_sentences.append(get_sentence_rhs(sentence))
                    return True
        return ans
