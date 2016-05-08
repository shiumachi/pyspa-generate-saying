import MeCab
import sys
import logging
import argparse

m = MeCab.Tagger('')
m.parse('')

# option settings
parser = argparse.ArgumentParser(description='pyspa saying generator')
parser.add_argument('--log', type=str, default='INFO', help='set log level (INFO, DEBUG)')


def parse_line(line):
    node = m.parseToNode(line)
    node = node.next
    converted_arr = []
    nouns = []

    while node:
        logging.debug("{0}: {1}".format(node.surface, node.feature))
        word = node.surface
        feature = node.feature.split(',')
        word_class = feature[0]
        if word_class == "名詞":
            nouns.append(word)
            word = "\"{" + word + "}\""
        converted_arr.append(word)
        node = node.next

    return ''.join(converted_arr), nouns


def generate(input_arr):
    # 名詞は{}で囲う。それ以外の部分は全て""で囲う。
    # 名詞を"{}"で囲み、最後に全体の文頭・文末に""を付加することで実現。

    nouns = []
    converted_input = []

    for line in input_arr:
        converted_line, nouns_per_line = parse_line(line)
        converted_input.append(converted_line)
        nouns += nouns_per_line

    generated_text = "\"" + '\n'.join(converted_input) + "\""

    out_arr = []

    out_arr.append(generated_text)

    for n in nouns:
        out_arr.append("{0}()".format(n))

    return "let(" + ",".join(out_arr) + ")"


if __name__ == '__main__':
    p = parser.parse_args()

    loglevel = p.log.upper()
    numeric_level = getattr(logging, loglevel, None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level)

    input_arr = []

    for line in sys.stdin:
        input_arr.append(line.strip())

    out = generate(input_arr)

    print(out)
