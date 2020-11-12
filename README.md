# crystalball
for smiles and protein feature process

# all_feature_extractor.json
train_file_path 是待处理的原始训练数据
test_file_path 是待处理的原始测试数据
protein_feature_file 是蛋白相关特征的配置文件，一并放在config下
smiles_feature_file 是分子相关特征的配置文件，一并放在config下
scale_file_path_prefix 是连续特征进行归一化处理之后的scale文件
sign_index_file_path_prefix 是分类特征进行one-hot处理后(id, 类别)的文件，这部分可以在以后用到更多分类特征后使用
middle_file_prefix 是指特征处理中，分别生成的分子、蛋白的特征csv
train_process_file_prefix_path 生成的最终的特征训练集
test_process_file_prefix_path 生成的最终的特征测试集

# protein_feature.json和smiles_feature.json
save_middle 是指是否需要保存蛋白\分子的各自中间特征
feature_list里面对应的是每一个类型的特征处理
------process_handler:指每个field的特征对应下的处理方法，和/feature_handler目录下的处理类名相对应
------scale:指进行处理时候用的规则化工具，主要是针对连续型特征处理用的，和/scale_handler目录下的处理类名相对应
------predict_missing_value:当某个特征有缺失值时候，是否进行补全，这部分功能还没有完成
------args:用于handler进行初始化的输入参数，主要是定制化复用handler使用，基本格式是(key:value)|(key:value)|...

#执行
bash run.sh
分别对应了三种运行模式，
第一种是只执行训练数据集的生成，
第二种是执行测试集的生成，
第三种是先执行训练集的生成，然后执行测试集的生成

#增加数据处理模块
如果要添加新的特征，可以先尝试在feature_handler里找到有没有特征处理类可以复用，如果有，在protein_feature.json/
smile_feature.json里添加相应的block，process_handler沿用可复用的类名，在args里添加想处理的参数即可；如果没有找到
自己需要的process_handler，则需要继承feature_handler/abstract_feature这个类，实现自己的initialize和process方法
然后在utils/register.py中的register_handlers()进行handler注册，最后再protein_feature.json/
smile_feature.json添加对应的配置
同样，scale的配置类似，如果需要自己使用新的scale，先继承abstract_scale,然后注册，最后配置


