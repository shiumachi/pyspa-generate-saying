import MeCab
import sys
import logging
import argparse

MECAB_USER_DIC = "dic/pyspa.dic"
MECAB_DIC = "/usr/local/lib/mecab/dic/mecab-ipadic-neologd"

m = MeCab.Tagger('-u {0} -d {1}'.format(MECAB_USER_DIC, MECAB_DIC))
m.parse('')

# option settings
parser = argparse.ArgumentParser(description='pyspa saying generator')
parser.add_argument('--log', type=str, default='INFO', help='set log level (INFO, DEBUG)')


class Morpheme(object):
    def __init__(self, node):
        self.node = node
        self.surface = node.surface

        feature = node.feature.split(',')
        self.word_class = feature[0]
        self.word_class_detail = feature[1]
        self.word_class_detail_2 = feature[2]
        self.word_class_detail_3 = feature[3]
        self.conjugation = feature[4]
        self.conjugation_2 = feature[5]
        self.original_form = feature[6]

        #以下のパラメータは与えられない形態素も存在する

        if len(feature) >= 8:
            self.reading = feature[7]
            self.pronounciation = feature[8]

        self.converted = False


def parse_line(line):
    node = m.parseToNode(line)
    node = node.next
    converted_arr = []
    words = {}
    words['nouns'] = []
    words['verbs'] = []
    words['organizations'] = []
    words['adjective_verbs'] = []

    morphemes = []

    while node:
        logging.debug("{0}: {1}".format(node.surface, node.feature))
        word = node.surface
        mrp = Morpheme(node)
        morphemes.append(mrp)
        node = node.next

    converted_arr = []
    l = len(morphemes)

    for i in range(1, l+1):
        mrp = morphemes[l-i]

        #既に他の語とともに処理済み
        if mrp.converted is True:
            continue

        word = mrp.surface

        if i < l:
            mrp_next = morphemes[l-(i+1)]
            # 名詞+的は形容動詞として変換
            if mrp.word_class_detail_2 == '形容動詞語幹' and mrp_next.word_class == '名詞':
                word = mrp_next.surface + mrp.surface
                converted_arr.append("\"{" + word + "}\"")
                mrp.converted = True
                mrp_next.converted = True
                words['adjective_verbs'].append(word)
                continue

        if mrp.word_class == '名詞':
            # 一般名詞は{何}に変換
            if mrp.word_class_detail == "一般":
                words['nouns'].append(word)
                word = "\"{" + word + "}\""
            # 組織固有名詞は{企業}に変換
            elif mrp.word_class_detail == "固有名詞" and mrp.word_class_detail_2 == "組織":
                words['organizations'].append(word)
                word = "\"{" + word + "}\""
            # サ変接続は{サ変}に変換
            elif mrp.word_class_detail == "サ変接続":
                words['verbs'].append(word)
                word = "\"{" + word + "}\""

        converted_arr.append(word)

    return ''.join(converted_arr[::-1]), words


def generate(input_arr):
    # 一般名詞、サ変名詞は{}で囲う。それ以外の部分は全て""で囲う。
    # 名詞を"{}"で囲み、最後に全体の文頭・文末に""を付加することで実現。

    nouns = []
    verbs = []
    organizations = []
    adjective_verbs = []
    converted_input = []

    for line in input_arr:
        converted_line, words_per_line = parse_line(line)
        converted_input.append(converted_line)
        nouns += words_per_line['nouns']
        verbs += words_per_line['verbs']
        organizations += words_per_line['organizations']
        adjective_verbs += words_per_line['adjective_verbs']

    nouns = list(set(nouns))
    verbs = list(set(verbs))
    organizations = list(set(organizations))

    generated_text = "\"" + '\n'.join(converted_input) + "\""

    out_arr = []

    out_arr.append(generated_text)

    for n in nouns:
        out_arr.append("{0}(何)".format(n))

    for v in verbs:
        out_arr.append("{0}(サ変)".format(v))

    for o in organizations:
        out_arr.append("{0}(企業)".format(o))

    for av in adjective_verbs:
        out_arr.append("{0}(形容動詞)".format(av))

    return "!let(" + ",".join(out_arr) + ")"


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
