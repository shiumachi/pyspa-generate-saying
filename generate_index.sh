#!/bin/bash

MECAB_DICT_INDEX=/usr/local/Cellar/mecab/0.996/libexec/mecab/mecab-dict-index
MECAB_DIC_DIR=/usr/local/lib/mecab/dic/ipadic
SOURCE_FILE=dic/pyspa.csv
TARGET_FILE=dic/pyspa.dic

${MECAB_DICT_INDEX} -d${MECAB_DIC_DIR} -u ${TARGET_FILE} -f utf8 -t utf8 ${SOURCE_FILE}
