
from KnowledgeBase import KnowledgeBase
from Algorithms import Algorithms


def main_function(file_path, search_method):
    with open(file_path, "r") as KB_file:
        KB_file.readline()
        initial_sentences = KB_file.readline().strip("\n").split("; ")
        KB_file.readline()
        alpha = KB_file.readline().strip("\n")

    sentences = []
    for i in initial_sentences:
        sentences.append(i.strip(";"))

    kb = KnowledgeBase(sentences, alpha)
    algo = Algorithms(kb)
    print(algo.call_algorithm(search_method))
