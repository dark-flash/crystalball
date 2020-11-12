
from feature_handler.protein_tfidf_feature import protein_tfidf_feature
from feature_handler.protein_w2v_feature import protein_w2v_feature
from scale_handler.minmax_scale import minmax_scale

def register_handlers():
    register_class_dict = dict()
    register_class_dict['protein_tfidf_feature'] = protein_tfidf_feature()
    register_class_dict['protein_w2v_feature'] = protein_w2v_feature()
    return register_class_dict

def register_scale_handlers():
    register_scale_class_dict = dict()
    register_scale_class_dict['minmax'] = minmax_scale()
    return register_scale_class_dict