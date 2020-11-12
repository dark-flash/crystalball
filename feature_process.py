
import argparse
from utils.register import *
from utils.common import *
import pandas as pd

#####################################
def process_train_data():
    all_feature_extractor_file = load_json_file('./config/all_feature_extractor.json')
    protein_feature_file = all_feature_extractor_file['protein_feature_file']
    smile_feature_file = all_feature_extractor_file['smiles_feature_file']
    ##读取配置文件
    save_protein_middle_file, protein_feature = load_feature_file(protein_feature_file)
    save_smile_middle_file, smile_feature = load_feature_file(smile_feature_file)

    # 开始注册所有的特征处理类
    register_handler_dict = register_handlers()
    protein_process_handler_dict, smile_process_handler_dict, feature_name_config_dict = get_process_handler_dict(protein_feature, smile_feature, register_handler_dict)

    ##注册所有的scale处理的类
    register_scale_handler_dict = register_scale_handlers()
    scale_handler_dict = get_process_scale_handler_dict(protein_feature, smile_feature, register_scale_handler_dict)

    ##将待处理的原始数据读入
    raw_data_path = all_feature_extractor_file["train_file_path"]
    all_raw_df, protein_input, smiles_input = load_raw_data(raw_data_path)
    #print(len(protein_input), len(smiles_input))

    protein_feature_processed_dict = process_feat(protein_process_handler_dict, protein_input)
    smile_feature_processed_dict = process_feat(smile_process_handler_dict, smiles_input)

    protein_df, protein_feature_index_name = process_protein_smile_split(protein_input, protein_feature_processed_dict)
    smile_df, smile_feature_index_name = process_protein_smile_split(smiles_input, smile_feature_processed_dict)

    union_protein_feat_raw_data = pd.merge(all_raw_df, protein_df, left_on='PROTEIN_SEQUENCE',
                                           right_index=True, how='left')

    union_protein_smile_feat_raw_data = pd.merge(union_protein_feat_raw_data, smile_df, left_on='COMPOUND_SMILES',
                                                 right_index=True, how='left')

    # print("before scale the union df is::::::::")
    # print(union_protein_smile_feat_raw_data['protein_1gram_tfidf_0'])

    save_middle_file(protein_df, all_feature_extractor_file["middle_file_prefix"],
                     save_flag=save_protein_middle_file)
    save_middle_file(smile_df, all_feature_extractor_file["middle_file_prefix"],
                     save_flag=save_smile_middle_file)

    # union_protein_smile_feat_raw_data, protein_feature_index_name, smile_feature_index_name, feature_name_config_dict

    ##遍历每个feature，看看是否需要scale进行处理
    feature_index_name = protein_feature_index_name + smile_feature_index_name

    scale_dict, union_protein_smile_feat_raw_data = scale_handler_process(feature_index_name, feature_name_config_dict,
                                                                          scale_handler_dict, union_protein_smile_feat_raw_data)

    #
    # ##保存scale，当做新的测试数据的middle_file
    scale_file_path = all_feature_extractor_file["scale_file_path_prefix"] + 'scale.json'
    save_scale_file(scale_dict, scale_file_path)

    # ####将进行scale之后的train数据保存下来
    train_process_file_prefix_path = all_feature_extractor_file["train_process_file_prefix_path"]
    train_file_name = 'processed_train.csv'
    union_protein_smile_feat_raw_data.to_csv(train_process_file_prefix_path + train_file_name, index=False)
    #########################################

def process_test_data():
    all_feature_extractor_file = load_json_file('./config/all_feature_extractor.json')
    protein_feature_file = all_feature_extractor_file['protein_feature_file']
    smile_feature_file = all_feature_extractor_file['smiles_feature_file']
    ##读取配置文件
    save_protein_middle_file, protein_feature = load_feature_file(protein_feature_file)
    save_smile_middle_file, smile_feature = load_feature_file(smile_feature_file)

    # 开始注册所有的特征处理类
    register_handler_dict = register_handlers()
    protein_process_handler_dict, smile_process_handler_dict, feature_name_config_dict = get_process_handler_dict(
        protein_feature, smile_feature, register_handler_dict)

    ##将待处理的原始数据读入
    raw_data_path = all_feature_extractor_file["test_file_path"]
    all_raw_df, protein_input, smiles_input = load_raw_data(raw_data_path)

    protein_feature_processed_dict = process_feat(protein_process_handler_dict, protein_input)
    smile_feature_processed_dict = process_feat(smile_process_handler_dict, smiles_input)

    protein_df, protein_feature_index_name = process_protein_smile_split(protein_input, protein_feature_processed_dict)
    smile_df, smile_feature_index_name = process_protein_smile_split(smiles_input, smile_feature_processed_dict)

    union_protein_feat_raw_data = pd.merge(all_raw_df, protein_df, left_on='PROTEIN_SEQUENCE',
                                           right_index=True, how='left')

    union_protein_smile_feat_raw_data = pd.merge(union_protein_feat_raw_data, smile_df, left_on='COMPOUND_SMILES',
                                                 right_index=True, how='left')

    save_middle_file(protein_df, all_feature_extractor_file["middle_file_prefix"],
                     is_train=False, save_flag=save_protein_middle_file)
    save_middle_file(smile_df, all_feature_extractor_file["middle_file_prefix"],
                     is_train=False, save_flag=save_smile_middle_file)

    ##将训练集的scale.json进行读取
    scale_file_path = all_feature_extractor_file["scale_file_path_prefix"] + 'scale.json'
    scale_dict = load_json_file(scale_file_path)

    ##注册所有的scale处理的类
    register_scale_handler_dict = register_scale_handlers()
    scale_handler_dict = get_process_scale_handler_dict(protein_feature, smile_feature, register_scale_handler_dict)

    ##遍历每个feature，看看是否需要scale进行处理
    feature_index_name = protein_feature_index_name + smile_feature_index_name
    union_protein_smile_feat_raw_data = scale_handler_reconstruct_process(scale_dict, feature_index_name, feature_name_config_dict,
                                      scale_handler_dict, union_protein_smile_feat_raw_data)

    #最后将处理好的test文件进行保存
    train_process_file_prefix_path = all_feature_extractor_file["test_process_file_prefix_path"]
    train_file_name = 'processed_test.csv'
    union_protein_smile_feat_raw_data.to_csv(train_process_file_prefix_path + train_file_name, index=False)

#process_train_data()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-task", "--task_type", type=str)
    args = parser.parse_args()

    if args.task_type == "train":
        process_train_data()
    elif args.task_type == "test":
        process_test_data()
    elif args.task_type == "all":
        process_train_data()
        process_test_data()
    else:
        raise ValueError("task type is invalid!")










