import sys
import json
import pandas as pd
import random

def load_feature_file(feature_file):
    with open(feature_file, 'r') as f:
        feature_dict = json.load(f)
        save_protein_middle_file = feature_dict['save_middle']
        protein_feature = feature_dict['feature_list']
    return save_protein_middle_file, protein_feature

def load_json_file(top_file):
    with open(top_file, 'r') as f:
        json_dict = json.load(f)
    return json_dict

# 将protein的特征作为中间文件保存下来
def save_middle_file(df, feat_middle_file_prefix, is_train = True, save_flag=True, is_protein=True):
    if save_flag:
        if is_protein:
            if is_train:
                protein_feat_file = 'protein_feat.csv'
            else:
                protein_feat_file = 'test_protein_feat.csv'
            df.to_csv(feat_middle_file_prefix + protein_feat_file, index=True)
    # 将smile的特征作为中间文件保存下来
        else:
            if is_train:
                smile_feat_file = 'smile_feat.csv'
            else:
                smile_feat_file = 'test_smile_feat.csv'
            df.to_csv(feat_middle_file_prefix + smile_feat_file, index=True)

#将scale等json文件保存下来
def save_scale_file(scale_dict, scale_file_path):
    json_scale_params = json.dumps(scale_dict)
    with open(scale_file_path, 'w') as json_file:
        json_file.write(json_scale_params)

def load_raw_data(raw_data_path):
    raw_df_list = []
    for sub_file in raw_data_path:
        raw_df = pd.read_csv(sub_file)
        raw_df_list.append(raw_df)
    all_raw_df = pd.concat(raw_df_list)
    protein_input = list(set(all_raw_df['PROTEIN_SEQUENCE']))  # 分别做去重处理，防止同样的分子或者蛋白重复计算特征
    smiles_input = list(set(all_raw_df['COMPOUND_SMILES']))  # 分别做去重处理，防止同样的分子或者蛋白重复计算特征
    return all_raw_df, protein_input, smiles_input

####通过注册的handler得到本次实验中对蛋白、分子处理的handler，以及所有feat对应的config
def get_process_handler_dict(protein_feature, smile_feature, register_handler_dict):
    protein_process_handler_dict = {}
    smile_process_handler_dict = {}
    feature_name_config_dict = {}

    for config in protein_feature:
        handler_name = config["process_handler"]
        feature_name_config_dict[config["block_name"]] = config
        print(config)
        if handler_name in register_handler_dict.keys():
            handler = register_handler_dict[handler_name]
            handler.initialize(config["args"])
            protein_process_handler_dict[config["block_name"]] = handler
        else:
            raise ValueError("handler {} not in register dict!!!!".format(handler_name))

    for config in smile_feature:
        handler_name = config["process_handler"]
        feature_name_config_dict[config["block_name"]] = config
        print(config)
        if handler_name in register_handler_dict.keys():
            handler = register_handler_dict[handler_name]
            handler.initialize(config["args"])
            smile_process_handler_dict[config["block_name"]] = handler
        else:
            raise ValueError("handler {} not in register dict!!!!".format(handler_name))
    return protein_process_handler_dict, smile_process_handler_dict, feature_name_config_dict

##注册所有的scale处理的类
def get_process_scale_handler_dict(protein_feature, smile_feature, register_scale_dict):
    scale_handler_dict = {}
    for config in protein_feature:
        scale_name = config['scale']
        if len(scale_name) == 0:      #没有scale时
            continue
        if scale_name in register_scale_dict.keys():
            scale_handler_dict[scale_name] = register_scale_dict[scale_name]
        else:
            raise ValueError("scale handler {} not in scale handler register dict!!!!!".format(scale_name))
    for config in smile_feature:
        scale_name = config['scale']
        if len(scale_name) == 0:  # 没有scale时
            continue
        if scale_name in register_scale_dict.keys():
            scale_handler_dict[scale_name] = register_scale_dict[scale_name]
        else:
            raise ValueError("scale handler {} not in scale handler register dict!!!!!".format(scale_name))
    return scale_handler_dict

##分别处理protein和smile的特征，针对每一个block的特征处理
def process_feat(process_handler_dict, input):
    feature_processed_dict = dict()
    for (feature_name, handler) in process_handler_dict.items():
        handler.process(input)
        handler_output = handler.emit()
        if len(handler_output) == 0:
            print("{} feature extract fail!".format(feature_name))
            continue
        feature_processed_dict[feature_name] = (handler_output, handler.get_invalid_sets())
    return feature_processed_dict

##将protein、smile的特征分别进行聚合整理
def process_protein_smile_split(input, feature_processed_dict):
    split_df = pd.DataFrame(columns=[], index=input)
    feature_index_name = []
    for feature_name in feature_processed_dict.keys():
        handler_output, handler_processed_invalid_set = feature_processed_dict[feature_name]
        random_key = random.choice(list(handler_output.keys()))
        feature_dim = len(handler_output[random_key])
        assemble_feature_col_name = [feature_name + '_{}'.format(i) for i in range(feature_dim)]
        feature_index_name.append((feature_name, assemble_feature_col_name))
        feature_df = pd.DataFrame(handler_output).T
        feature_df.columns = assemble_feature_col_name
        split_df = pd.merge(split_df, feature_df, left_index=True, right_index=True, how='left')
    return split_df, feature_index_name

###用注册的scale对各个block进行处理
def scale_handler_process(feature_index_name, feature_name_config_dict, scale_handler_dict,
                          union_protein_smile_feat_raw_data):
    scale_dict = dict()
    for (feature_name, assemble_feature_col_name) in feature_index_name:
        config = feature_name_config_dict[feature_name]
        scale = config["scale"]
        if len(scale) == 0:
            continue
        scale_handler = scale_handler_dict[scale]
        ready_for_scale_data = union_protein_smile_feat_raw_data[assemble_feature_col_name].values
        #print(ready_for_scale_data)
        scale_handler.calc_scale(ready_for_scale_data, assemble_feature_col_name)
        scale_result = scale_handler.emit_scale_result()
        #print(scale_result)
        union_protein_smile_feat_raw_data[assemble_feature_col_name] = scale_result
        scale_dict[feature_name] = scale_handler.emit_scale_params()
    return scale_dict, union_protein_smile_feat_raw_data

###用注册的scale和scale.json对各个block做reconstrct处理
def scale_handler_reconstruct_process(scale_dict, feature_index_name, feature_name_config_dict,
                                      scale_handler_dict, union_protein_smile_feat_raw_data):
    for (feature_name, assemble_feature_col_name) in feature_index_name:
        config = feature_name_config_dict[feature_name]
        scale = config["scale"]
        if len(scale) == 0:
            continue
        params = scale_dict[feature_name]
        scale_handler = scale_handler_dict[scale]
        ready_for_scale_data = union_protein_smile_feat_raw_data[assemble_feature_col_name].values
        scale_handler.calc_reconstruct_scale(ready_for_scale_data, params)
        scale_reconstruct_result = scale_handler.emit_scale_reconstruct_result()
        union_protein_smile_feat_raw_data[assemble_feature_col_name] = scale_reconstruct_result
    return union_protein_smile_feat_raw_data