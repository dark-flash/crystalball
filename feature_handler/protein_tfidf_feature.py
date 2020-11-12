from feature_handler.abstract_feature import abstract_feature
import pickle

class protein_tfidf_feature(abstract_feature):
    def __init__(self):
        super().__init__()

    def initialize(self, args):
        super(protein_tfidf_feature, self).initialize(args)
        self.params_dict = dict()
        self.need_parameter = ['gram', 'model_name']
        arg_list = self.args.split('|')
        for arg in arg_list:
            single_arg = arg.split(':')
            if len(single_arg) != 2:
                raise ValueError("feature args num wrong!!!")
            self.params_dict[single_arg[0]] = single_arg[1]

        for named_paramter in self.need_parameter:
            if named_paramter not in self.params_dict.keys():
                raise ValueError("parametr {} not contain!!".format(named_paramter))

        gram_model_path_prefix = '/Users/siqi/PycharmProjects/Crystalball/resources/pretrain_model/'
        gram_model_path = gram_model_path_prefix + self.params_dict['model_name']
        self.model = pickle.load(open(gram_model_path, 'rb'))

    def process(self, input):
        assemble_input = []
        if isinstance(input, str):
            assemble_input.append(input)
        elif isinstance(input, list):
            assemble_input = input
        else:
            raise ValueError("input type is not support!!")

        result = self.model.transform(assemble_input).todense().tolist()
        for idx in range(len(result)):
            self.output[assemble_input[idx]] = result[idx]





