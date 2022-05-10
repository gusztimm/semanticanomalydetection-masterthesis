from labelparser.bertparser.bert_wrapper import SequenceTaggerBert, BertForLabelParsing
from labelparser.parsed_label import ParsedLabel
import labelparser.label_utils as label_utils

PARSER_PATH = "./input/bert_model/"


class BertTagger:

    def __init__(self):
        self.model = SequenceTaggerBert.load_serialized(PARSER_PATH, BertForLabelParsing)
        self.parse_map = {}

    def parse_label(self, label, print_outcome = False):
        if label in self.parse_map:
            return self.parse_map[label]
        split, tags = self.predict_single_label(label)
        result = ParsedLabel(label, split, tags, find_objects(split, tags), find_actions(split, tags))
        if print_outcome:
            print(label, ", act:", result.actions, ", bos:", result.bos, ', tags:', tags)
        self.parse_map[label] = result
        return result

    def get_tags_for_list(self, li: list) -> dict:
        tagged = {}
        for unique in li:
            unique = str(unique)
            if unique not in tagged:
                tagged[unique] = self.predict_single_label(unique)
        return tagged

    def predict_single_label(self, label):
        split = label_utils.split_label(label)
        return split, self.model.predict([split])[0][0]

    def predict_single_label_full(self, label):
        split = label_utils.split_label(label)
        return split, self.model.predict([split])

    @staticmethod
    def _fill_all(x, seen_tagged):
        uniquely_tagged = []
        tagging = str()
        for i in range(len(seen_tagged[x][0])):
            tagging = tagging + str(seen_tagged[x][0][i]) + '<>' + str(seen_tagged[x][1][i]) + ', '
        uniquely_tagged.append(tagging)
        return uniquely_tagged

    def get_action(self, label):
        if len(self.parse_label(label).actions) > 0:
            return self.parse_label(label).actions[0]
        return None


def find_objects(split, tags):
    return [tok for tok, bo in zip(split, tags) if bo == 'BO']


def find_actions(split, tags):
    return [tok for tok, a in zip(split, tags) if a in ['A', 'STATE']]
