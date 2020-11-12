from feature_handler.abstract_feature import abstract_feature
import re
from gensim.models import Word2Vec
import numpy as np

class protein_w2v_feature(abstract_feature):
    def __init__(self):
        super().__init__()

    def initialize(self, args):
        super(protein_w2v_feature, self).initialize(args)
        self.params_dict = dict()
        self.need_parameter = ['window', 'model_name']
        arg_list = self.args.split('|')
        for arg in arg_list:
            single_arg = arg.split(':')
            if len(single_arg) != 2:
                raise ValueError("feature args num wrong!!!")
            self.params_dict[single_arg[0]] = single_arg[1]

        for named_paramter in self.need_parameter:
            if named_paramter not in self.params_dict.keys():
                raise ValueError("parametr {} not contain!!".format(named_paramter))

        w2v_model_path_prefix = '/Users/siqi/PycharmProjects/Crystalball/resources/pretrain_model/'
        w2v_model_path = w2v_model_path_prefix + self.params_dict['model_name']
        self.model = Word2Vec.load(w2v_model_path)
        self.window_size = int(self.params_dict['window'])
        self.w2v_dict = self.model.wv.vocab

    def process(self, input):
        assemble_input = []
        if isinstance(input, str):
            assemble_input.append(input)
        elif isinstance(input, list):
            assemble_input = input
        else:
            raise ValueError("input type is not support!!")

        protein_seq_text = []
        for protein_seq in input:
            for shift in range(0, self.window_size):
                protein_seq_text.append([word for word in re.findall(r'.{' + str(self.window_size) + '}', protein_seq[shift:])])

        start = 0
        w2v_feat = []
        while start <= len(protein_seq_text) - self.window_size:
            sum_w2v = np.zeros(shape=(128,))
            for i in range(start, start + self.window_size):
                for word in protein_seq_text[i]:
                    if word in self.w2v_dict.keys():
                        sum_w2v += self.model[word]
            start += self.window_size
            w2v_feat.append(sum_w2v)

        for idx in range(len(w2v_feat)):
            self.output[assemble_input[idx]] = w2v_feat[idx]

