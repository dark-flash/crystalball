

class abstract_scale(object):
    def __init__(self):
        self.scale_params = dict()
        self.output = list()
        self.reconstruct = list()

    def calc_scale(self, input, col_name):
        pass

    def calc_reconstruct_scale(self, input, params):
        pass

    def emit_scale_params(self):
        return self.scale_params

    def emit_scale_result(self):
        return self.output

    def emit_scale_reconstruct_result(self):
        return self.reconstruct