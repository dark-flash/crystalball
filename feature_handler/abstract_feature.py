
class abstract_feature(object):
    def __init__(self):
        self.output = dict()

    def initialize(self, args):
        self.args = args
        self.invalid_sample = set()

    def process(self, input):
        pass

    def emit(self):
        return self.output

    def get_invalid_sets(self):
        return self.invalid_sample
