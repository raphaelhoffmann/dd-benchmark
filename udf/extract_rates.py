#! /usr/bin/env python3

import fileinput
import re

import phonenumbers

from dstruct.Mention import Mention
from dstruct.Sentence import Sentence
from helper.easierlife import get_dict_from_tsv_line, get_all_phrases_in_sentence2, tsv_string_to_list, no_op
from helper.dictionaries import load_dict

MAXN = 1000
MINN = 10

POS_EXCLUDE = frozenset(("VB", "VBD", "VBG", "VBP", "VBZ"))
NER_EXCLUDE = frozenset(("PERSON", "LOCATION"))

MAX_PHRASE_LENGTH = 4  # Only looking at phrases of up to this size

regex_alpha = re.compile("[a-zA-Z0-9]")
regex_numbers_letters = re.compile("^[0-9]+[A-Za-z]+$")

currencies = frozenset((
    "$", "dollar", "dollars", "dlr", "bucks", "dlrs", "roses", "rose", "kisses", "euro", "euros", "eur", "EUR", "eu", "EU", "aud", "AUD", "£", "€", "dandelions", "credits", "¢", "¥"))
per = frozenset(("per", "one", "a"))

hours_numbers_words = frozenset(("one", "two", "three", "four", "five", "six", "seven", "eight",
                                 "nine", "ten", "twelve", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "24", "48"))

hours_words = frozenset(("hour", "hours", "hrs", "hr"))

minutes = frozenset((10, 15, 20, 30, 35, 40, 45, 60, 75, 90, 120))
minutes_numbers_words = frozenset(("10", "15", "20", "25", "30", "35", "40", "45",
                                   "60", "75", "90", "120", "ten", "fifteen", "twenty", "thirty", "sixty", "ninety"))
minutes_words = frozenset(
    ("minutes", "minute", "mins", "min", "mnts", "minutos"))
duration_words = hours_words | minutes_words

min_suffixes = frozenset(("m", "min", "mins", "minutes", "minute"))

quick_singles = frozenset((
    "qv", "qh", "qhr", "qk", "15min", "15mins", "15-mins", "15-min", "15mnts", "15m"
    "10min", "10mins", "10-mins", "10-min", "quick", "ss", "sv", "shortstay", "15 minS"
    "q/stop", "quck", "quickly", "qwickie"))
quick_suffixes = quick_singles | frozenset(("q", "short"))
half_singles = frozenset((
    "hh", "hhr", "30min", "30 min", "30mins", "30 m", "30m", "halfhour", "halfhours", "half hour", "half", "h/h", "hallf", "1/2", "1/2", "half",
    "30-mins", "1/2hr", "1/2h", "hf", "h/hour", "halfh", "h.h", "hhrs", "halfn", "h hr", "h hour", "half", "hlf", "1/2 hour", "1/2 hr", "1/2 hours"))
half_suffixes = half_singles
hour_singles = frozenset((
    "1hr", "fh", "fhr", "hr", "60m", "60mins", "60min", "60-minutes", "60-mins", "60-min", "60minute", "1/h", "1/hr", "fullhour", "fullhours", "full hour", "an hour", "a hr", "whole"))
hour_suffixes = hour_singles | frozenset(("full", "h", "hours", "hour"))
fourtyfive_singles = frozenset(
    ("45min", "45 min", "45mins", "45 mins", "45m", "45 m", "45minutes", "45-mins"))
fourtyfive_suffixes = fourtyfive_singles
twoh_singles = frozenset(("2hr", "2/h", "2/hr", "2hour", "2hrs", "two hours", "2 hours"))
twoh_suffixes = twoh_singles
threeh_singles = frozenset(("3hr", ))
threeh_suffixes = threeh_singles

full_singles = frozenset(("outcalls", "outcall", "overnite"))
full_suffixes = full_singles

two_grams_prefixes = frozenset((
    "1/2", "1/2", "half", "1.5", "hlf", "full", "an hour", "a hr", "whole", "multiple", "additional", "first", "multi", "add", "complete"))
two_grams_durations = frozenset((
    "quick visits", "quick visit", "quick fix", "short stay", "short visit", "quick stay", "short fix"))

singles = quick_singles | half_singles | hour_singles | fourtyfive_singles | \
    twoh_singles | threeh_singles
suffixes = quick_suffixes | half_suffixes | hour_suffixes | \
    fourtyfive_suffixes | twoh_suffixes | threeh_suffixes | min_suffixes

STOP_WORDS = load_dict("stopwords")
ALL_ENGLISH_WORDS = load_dict("english") - \
    (singles | suffixes | two_grams_prefixes | {"quick", })

sregex_1w_num_min = re.compile("^(15|20|30|45|60|90|120)/?-?min")
sregex_1w_num_hour = re.compile("^(1|2|3|one|two|three)/?-?h")

regex_min = re.compile("min$|mins|minut")
regex_half = re.compile("hlf|half")
regex_hh = re.compile("hh")
regex_slash = re.compile("/")
regex_hour = re.compile("hrs?$|hours?")
regex_hyphen = re.compile("-")
regex_common_minute_number = re.compile(
    "15$|15\D+|30$|30\D+|45$|45\D+|60$|60\D+|90$|90\D+")
regex_common_hour_spelled = re.compile("one|two|three")
regex_quick = re.compile("qk|qky|qq|quick")
regex_number = re.compile("(\d+)")
regex_dimensions = re.compile("\d\d[a-zA-Z]+-\d\d-\d\d")
regex_with = re.compile("w/")
regex_dollar_sign = re.compile("\$")
regex_percent = re.compile("%")
regex_bad_word = re.compile(
    "secs|second|year|yr|day|week|month|lb|pound|ever|dd|cm|mm|inch|under|over"
)
regex_alpha = re.compile("[a-zA-Z0-9]")
regex_24_7 = re.compile("24/7")
regex_signed = re.compile("^\+|^-")

minute_set1 = frozenset(
    ["WORD0_CONTAINS_MIN", "WORD0_CONTAINS_COMMON_MINUTE_NUMBER"])
hour_set1 = frozenset(
    ["WORD0_CONTAINS_HOUR", "WORD0_CONTAINS_COMMON_HOUR_NUMBER_SPELLED"])
hh_set1 = frozenset(["WORD0_CONTAINS_HH"])

minute_set = frozenset(
    ["WORD0_CONTAINS_COMMON_MINUTE_NUMBER", "WORD1_CONTAINS_MIN"])
hour_set = frozenset(
    ["WORD0_CONTAINS_COMMON_HOUR_NUMBER_SPELLED", "WORD1_CONTAINS_HOUR"])
hour_spelled_set = frozenset(
    ["WORD0_CONTAINS_COMMON_HOUR_NUMBER_SPELLED", "WORD1_CONTAINS_HOUR"])
half_hour_set = frozenset(["WORD0_CONTAINS_HALF", "WORD1_CONTAINS_HOUR"])
full_hour_set = frozenset(["WORD0_CONTAINS_FULL", "WORD1_CONTAINS_HOUR"])

dimension_set = frozenset(
    ["WORD0_CONTAINS_DIMENSION", "WORD1_CONTAINS_DIMENSION"])
with_set = frozenset(
    ["WORD0_CONTAINS_WITH", "WORD1_CONTAINS_WITH"])
dollar_sign_set = frozenset(
    ["WORD0_CONTAINS_DOLLAR_SIGN", "WORD1_CONTAINS_DOLLAR_SIGN"])
percent_set = frozenset(
    ["WORD0_CONTAINS_PERCENT", "WORD1_CONTAINS_PERCENT"])
bad_word_set = frozenset(
    ["WORD0_CONTAINS_BAD_WORD", "WORD1_CONTAINS_BAD_WORD"])
set_24_7 = frozenset(
    ["WORD1_CONTAINS_24_7",  "WORD1_CONTAINS_24_7"])
signed_set = frozenset(["WORD0_SIGNED", "WORD1_SIGNED"])

negative = frozenset(["%", "and", "&"])

def transfer(x):
  ret = "NO DURATION"
  if x in quick_suffixes | two_grams_durations: ret = "15 MINS"
  if x in half_singles: ret = "30 MINS"
  if x in fourtyfive_singles: ret = "45 MINS"
  if x in hour_suffixes: ret = "1 HOUR"
  if x in twoh_singles: ret = "2 HOURS"
  if x in threeh_suffixes: ret = "3 HOURS"
  if x in full_suffixes: ret = "LONG TIME"
  return ret


def supervise(mention):
  phrase = mention.words
  if len(phrase) == 1:
    if "/" in phrase[0].word.casefold():
      try:
        num = int(phrase[0].word.casefold().split('/')[0])
        if check_num(num) and (phrase[0].word.casefold().split('/')[1] in (singles | suffixes | two_grams_durations)):
          mention.is_correct = True
      except ValueError:
        pass

  if len(phrase) == 2:
    new_phrase = phrase[0].word.casefold().split(
        '/') + [phrase[1].word.casefold()]
    if len(new_phrase) != 3:
      index = 0
      # print (phrase[0].word.casefold())
      while True:
        try:
          int(phrase[0].word.casefold()[index])
          index += 1
        except:
          break
      new_phrase = [phrase[0].word.casefold()[:index]] + [phrase[0].word.casefold()[
          index:]], [phrase[1].word.casefold()]
    if len(new_phrase) == 3:
      try:
        num = int(new_phrase[0])
        if check_num(num) and (" ".join(new_phrase[1:]) in (singles | suffixes | two_grams_durations)):
          mention.is_correct = True
      except ValueError:
        pass

    if (phrase[1].word.casefold() in (singles | two_grams_durations)):
      try:
        num = int(phrase[0].word.casefold())
        if check_num(num):
          mention.is_correct = True
      except ValueError:
        pass
    if (phrase[0].word.casefold() in (singles | two_grams_durations)):
      try:
        num = int(phrase[1].word.casefold())
        if check_num(num):
          mention.is_correct = True
      except ValueError:
        pass
  if len(phrase) == 4:
    if (phrase[0].word.casefold() in currencies) and (phrase[2].word.casefold() in per) and (phrase[3].word.casefold() in (singles | suffixes | two_grams_durations)):
      try:
        num = int(phrase[1].word.casefold())
        if (check_num(num)):
          mention.is_correct = True
      except ValueError:
        pass
    if (phrase[1].word.casefold() in currencies) and (phrase[2].word.casefold() in per) and (phrase[3].word.casefold() in (singles | suffixes | two_grams_durations)):
      try:
        num = int(phrase[0].word.casefold())
        if (check_num(num)):
          mention.is_correct = True
      except ValueError:
        pass

  if (len(phrase) == 1):
    try:
      int(phrase[0].word.casefold())
      mention.is_correct = False
    except:
      pass
  for x in negative:
    for p in phrase:
      if x in p.word.casefold():
        mention.is_correct = False
        break
  # if sregex_1w_num_min.match(mention.words[0].word) or \
  #         sregex_1w_num_hour.match(mention.words[0].word):
  #   mention.is_correct = True
  # for feature in mention.features:
  # or feature == "LENGTH_2"
  #   if feature.startswith("SINGLE_[") or feature.startswith("SUFFIX_["):
  #     mention.is_correct = True
  #     break
  #   elif feature == "NEXT_1_GRAM_[%]":
  #     mention.is_correct = False
  if mention.features.intersection(dimension_set):
    mention.is_correct = False
  if mention.features.intersection(with_set):
    mention.is_correct = False
  if mention.features.intersection(dollar_sign_set):
    mention.is_correct = False
  if mention.features.intersection(percent_set):
    mention.is_correct = False
  if mention.features.intersection(bad_word_set):
    mention.is_correct = False
  if mention.features.intersection(set_24_7):
    mention.is_correct = False
  if mention.features.intersection(signed_set):
    mention.is_correct = False


def add_features(mention, sentence):
  for i, mention_word in enumerate(
          [w.word.casefold() for w in mention.words]):
    if regex_min.search(mention_word):
      mention.add_feature("WORD%d_CONTAINS_MIN" % i)
    if regex_half.search(mention_word):
      mention.add_feature("WORD%d_CONTAINS_HALF" % i)
    if regex_hh.search(mention_word):
      mention.add_feature("WORD%d_CONTAINS_HH" % i)
    # if regex_slash.search(mention_word):
    #    mention.add_feature("WORD%d_CONTAINS_SLASH" % i)
    if regex_hour.search(mention_word):
      mention.add_feature("WORD%d_CONTAINS_HOUR" % i)
    if regex_hyphen.search(mention_word):
      mention.add_feature("WORD%d_CONTAINS_HYPHEN" % i)
    if regex_common_minute_number.search(mention_word):
      mention.add_feature("WORD%d_CONTAINS_COMMON_MINUTE_NUMBER" % i)
    if regex_common_hour_spelled.search(mention_word):
      mention.add_feature(
          "WORD%d_CONTAINS_COMMON_HOUR_NUMBER_SPELLED" % i)
    if regex_quick.search(mention_word):
      mention.add_feature("WORD%d_CONTAINS_QUICK" % i)
    if regex_dimensions.search(mention_word):
      mention.add_feature("WORD%d_CONTAINS_DIMENSION" % i)
    if regex_with.search(mention_word):
      mention.add_feature("WORD%d_CONTAINS_WITH" % i)
    if regex_dollar_sign.search(mention_word):
      mention.add_feature("WORD%d_CONTAINS_DOLLAR" % i)
    if regex_percent.search(mention_word):
      mention.add_feature("WORD%d_CONTAINS_PERCENT" % i)
    if regex_bad_word.search(mention_word):
      mention.add_feature("WORD%d_CONTAINS_BAD_WORD" % i)
    if regex_signed.match(mention_word):
      mention.add_feature("WORD%d_SIGNED" % i)
    if regex_24_7.search(mention_word):
      mention.add_feature("WORD%d_CONTAINS_24_7" % i)
  if len(mention.words) == 2:
    mention.add_feature("LENGTH_2")
  elif len(mention.words) == 1:
    word = mention.words[0]
    text = word.word.casefold()
    try:
      int(text)
      mention.add_feature("ONLY_NUMBER")
    except:
      pass
    if text in singles:
      mention.add_feature("SINGLE_[{}]".format(text))
    elif "/" in text:
      tokens = text.split("/")
      if len(tokens) == 2:
        if tokens[1] in suffixes:
          mention.add_feature("SUFFIX_[{}]".format(tokens[1]))
        else:
          try:
            number_1 = int(tokens[0])
            number_2 = int(tokens[1])
            if number_1 > 120 and number_2 > 120:
              mention.add_feature("BIG_NUMBERS")
          except:
            pass
    elif "-" in text:
      tokens = text.split("-")
      if len(tokens) == 2:
        if tokens[1] in suffixes:
          mention.add_feature("SUFFIX_[{}]".format(tokens[1]))
    elif regex_numbers_letters.match(text):
      index = 0
      while True:
        try:
          int(text[index])
          index += 1
        except:
          break
      if text[index:] in suffixes:
        mention.add_feature("SUFFIX_[{}]".format(text[index:]))
  else:  # Impossible
    pass
  # [copied directly from Matteo's code in extract_prices.py]
  # Add NLP features
  start = mention.words[0].in_sent_idx
  end = mention.words[-1].in_sent_idx + 1
  for ngram in range(1, 4):
    if start - ngram >= 0:
      mention.add_feature("PREV_{}_GRAM_[{}]".format(
          ngram, "_".join(map(
              lambda x: x.lemma.casefold(),
              sentence.words[start - ngram:start]))))
      # mention.add_feature("PREV_{}_GRAM_SINGLE_[{}]".format(
      #     ngram, sentence.words[start - ngram].lemma.casefold()))
      mention.add_feature("PREV_{}_GRAM_POS_[{}]".format(
          ngram, "_".join(map(
              lambda x: x.pos,
              sentence.words[start - ngram:start]))))
    if end + ngram < len(sentence.words):
      mention.add_feature("NEXT_{}_GRAM_[{}]".format(
          ngram, "_".join(map(
              lambda x: x.lemma.casefold(),
              sentence.words[end:end + ngram]))))
      # mention.add_feature("NEXT_{}_GRAM_SINGLE_[{}]".format(
      #     ngram, sentence.words[end + ngram].lemma.casefold()))
      mention.add_feature("NEXT_{}_GRAM_POS_[{}]".format(
          ngram, "_".join(map(
              lambda x: x.pos,
              sentence.words[end:end + ngram]))))
  # [end copy]


def check_num(num):
  if (num < MINN):
    return False
  if (num > MAXN):
    return False
  return True


def extract(sentence):
  mentions = []
  history = set()
  entity = ""
  # print ("template 1")
  for (start, end) in get_all_phrases_in_sentence2(sentence, MAX_PHRASE_LENGTH, -1):
    if start in history or end - 1 in history:
      continue
    phrase = sentence.words[start:end]
    create_mention = False

    if len(phrase) == 1:
      if "/" in phrase[0].word.casefold():
        try:
          num = int(phrase[0].word.casefold().split('/')[0])
          time = phrase[0].word.casefold().split('/')[1]
          if check_num(num) and (time in (singles | suffixes | two_grams_durations)):
            create_mention = True
            entity = ",".join([str(num), transfer(time)])
        except ValueError:
          pass

    if len(phrase) == 2:
      new_phrase = phrase[0].word.casefold().split(
          '/') + [phrase[1].word.casefold()]
      if len(new_phrase) != 3:
        index = 0
        while True:
          try:
            int(phrase[0].word.casefold()[index])
            index += 1
          except:
            break
        new_phrase = [phrase[0].word.casefold()[:index]] + [phrase[0].word.casefold()[
            index:]], [phrase[1].word.casefold()]
      if len(new_phrase) == 3:
        try:
          num = int(new_phrase[0])
          time = " ".join(new_phrase[1:])
          if check_num(num) and (time in (singles | suffixes | two_grams_durations)):
            create_mention = True
            entity = ",".join([str(num), transfer(time)])
        except ValueError:
          pass

    #   if (phrase[1].word.casefold() in (singles | two_grams_durations)):
    #     try:
    #       num = int(phrase[0].word.casefold())
    #       if check_num(num):
    #         create_mention = True
    #     except ValueError:
    #       pass
    #   if (phrase[0].word.casefold() in (singles | two_grams_durations)):
    #     try:
    #       num = int(phrase[1].word.casefold())
    #       if check_num(num):
    #         create_mention = True
    #     except ValueError:
    #       pass

    if len(phrase) == 4:
      try:
        num = int(phrase[1].word.casefold())
        if (check_num(num)):
          time = phrase[3].word.casefold()
          if (phrase[0].word.casefold() in currencies) and (phrase[2].word.casefold() in per) and (time in (singles | suffixes | two_grams_durations)):
            create_mention = True
            entity = ",".join([phrase[0].word.casefold() + str(num), transfer(time)])
          time = " ".join([phrase[2].word.casefold(), phrase[3].word.casefold()])
          if (phrase[0].word.casefold() in currencies) and (time in (singles | suffixes | two_grams_durations)):
            create_mention = True
            entity = ",".join([phrase[0].word.casefold() + str(num), transfer(time)])
      except ValueError:
        pass

      try:
        num = int(phrase[0].word.casefold())
        if (check_num(num)):
          time = phrase[3].word.casefold()
          if (phrase[1].word.casefold() in currencies) and (phrase[2].word.casefold() in per) and (time in (singles | suffixes | two_grams_durations)):
            create_mention = True
            entity = ",".join([phrase[1].word.casefold() + str(num), transfer(time)])
          time = " ".join([phrase[2].word.casefold(), phrase[3].word.casefold()])
          if (phrase[1].word.casefold() in currencies) and (time in (singles | suffixes | two_grams_durations)):
            create_mention = True
            entity = ",".join([phrase[1].word.casefold() + str(num), transfer(time)])
      except ValueError:
        pass

    if create_mention:
      # print (start, end, phrase)
      mention = Mention("RATES",
                        entity,
                        phrase)
      mentions.append(mention)
      for i in range(start, end):
        history.add(i)

  # print ("template 2")
  for (start, end) in get_all_phrases_in_sentence2(sentence, MAX_PHRASE_LENGTH + 1, 1):
    check = False
    for x in range(start, end):
      if x in history:
        check = True
    if check:
      continue
    phrase = sentence.words[start:end]
    # print (start, end, phrase)
    create_mention = False

    x = []

    for w in phrase:
      x = x + w.word.casefold().split("/")

    if (len(x[0]) == 0) or len(x[-1]) == 0:
      continue
    if (regex_alpha.match(x[0][0]) or x[0][0] in currencies) and (regex_alpha.match(x[-1][-1]) or x[-1][-1] in currencies):
      pass
    else:
      continue

    contain_num = False
    contain_time = False
    tmp = set()
    time = ""
    price = ""
    for i in range(0, len(x) - 1):
      if (i not in tmp) and (i + 1 not in tmp) and ((" ".join(x[i: i + 2]) in (singles | two_grams_durations)) or (x[i] in minutes_numbers_words | hours_numbers_words and x[i + 1] in minutes_words | hours_words)):
        tmp.add(i)
        tmp.add(i + 1)
        time = " ".join(x[i: i + 2])
        # print ("TIME", " ".join(x[i: i + 2]))
        contain_time = True

    for idx in range(len(x)):
      if (idx not in tmp) and (x[idx] in (singles | two_grams_durations) or sregex_1w_num_hour.match(x[idx]) or sregex_1w_num_min.match(x[idx])):
        contain_time = True
        time = x[idx]
        # print ("TIME", x[idx])
        tmp.add(idx)
    for idx in range(len(x)):
      try:
        num = int(x[idx])
        if (idx not in tmp) and (check_num(num)):
          tmp.add(idx)
          price = x[idx]
          # print ("NUM", x[idx])
          contain_num = True
      except:
        pass

    if (contain_num and contain_time):
      create_mention = True
      entity = ",".join([price, transfer(time)])

    if create_mention:
      # print (start, end, phrase)
      mention = Mention("RATES",
                        entity,
                        phrase)
      mentions.append(mention)
      for i in range(start, end):
        history.add(i)

  # print ("template 3")
  for (start, end) in get_all_phrases_in_sentence2(sentence, MAX_PHRASE_LENGTH + 1, 1):
    check = False
    for x in range(start, end):
      if x in history:
        check = True
    if check:
      continue
    phrase = sentence.words[start:end]
    create_mention = False
    contain_num = False
    contain_time = False
    time = ""
    price = ""

    x = []
    for w in phrase:
      x = x + w.word.casefold().split("/")

    if (len(x[0]) == 0) or len(x[-1]) == 0:
      continue
    if (regex_alpha.match(x[0][0]) or x[0][0] in currencies) and (regex_alpha.match(x[-1][-1]) or x[-1][-1] in currencies) and (x[0] not in negative) and (x[-1] not in negative):
      pass
    else:
      continue

    for w in x:
      if (w in (singles | suffixes | two_grams_durations) or sregex_1w_num_hour.match(w) or sregex_1w_num_min.match(w)):
        contain_time = True
        time = w
      try:
        num = int(w)
        if (check_num(num)):
          contain_num = True
          price = w
      except:
        pass
    for i in range(0, len(x) - 1):
      if (" ".join(x[i: i + 1]) in (singles | suffixes | two_grams_durations)):
        contain_time = True
        time = " ".join(x[i: i + 1])

    if (contain_num):
      create_mention = True
      entity = ",".join([price, transfer(time)])

    if create_mention:
      mention = Mention("RATES",
                        entity,
                        phrase)
      mentions.append(mention)
      for i in range(start, end):
        history.add(i)
  return mentions


if __name__ == "__main__":
  # Process the input
  with fileinput.input() as input_files:
    for line in input_files:
      line_dict = get_dict_from_tsv_line(
          line,
          ["doc_id", "sent_id", "words", "poses", "ners",
              "lemmas", "dep_paths", "dep_parents"],
          [no_op, int, tsv_string_to_list,
              tsv_string_to_list, tsv_string_to_list, tsv_string_to_list,
              tsv_string_to_list, lambda x: tsv_string_to_list(x, int)])
      sentence = Sentence(
          line_dict["doc_id"], line_dict["sent_id"],
          [x+1 for x in range(0, len(line_dict["words"]))], line_dict["words"],
          line_dict["poses"], line_dict["ners"], line_dict["lemmas"],
          line_dict["dep_paths"], line_dict["dep_parents"],
          [0 for x in line_dict["words"]])
      mentions = extract(sentence)
      for mention in mentions:
        add_features(mention, sentence)
        supervise(mention)
        print(mention.tsv_dump())
