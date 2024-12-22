# # <editor-fold dec=第三段代码，返回景点列表>
# import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity
# import os
# import json
# import django
# from datetime import datetime
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TARecommendation.settings")
# django.setup()
#
# from app.models import TravelInfo
# from app.models import TravelInfo, UserFavorites
#
# # 获取用户评分数据
# def get_user_rating():
#     user_rating = {}
#     for travel in TravelInfo.objects.all():
#         comments = json.loads(travel.comments)
#         for com in comments:
#             if isinstance(com, dict):  # 确保 com 是一个字典
#                 user_id = com.get('userId', -1)
#                 if user_id != -1:
#                     if user_rating.get(user_id, -1) == -1:
#                         user_rating[user_id] = {travel.id: com['score']}  # 使用景点 ID
#                     else:
#                         user_rating[user_id][travel.id] = com['score']
#     return user_rating
#
#
# # 协同过滤推荐
# def user_bases_collaborative_filtering(user_id, user_rating, top_n=3):
#     # 获取目标用户评分数据，避免 KeyError
#     target_user_rating = user_rating.get(user_id, {})
#
#     if not target_user_rating:  # 如果目标用户没有评分数据
#         print(f"User {user_id} has no ratings.")
#         return []
#
#     # 初始化一个字典，用于保存其他用户与目标用户的相似度得分
#     user_similarity_scores = {}
#
#     # 目标用户的评分项目（景点 ID）转化为列表
#     target_items = list(target_user_rating.keys())
#
#     # 计算目标用户与其他用户之间的相似度得分
#     for other_user_id, other_user_ratings in user_rating.items():
#         if other_user_id == user_id:
#             continue
#
#         # 将其他用户的评分转化为numpy数组（对于目标项目）
#         other_user_ratings_list = np.array([
#             other_user_ratings.get(item, 0) for item in target_items
#         ])
#
#         # 计算余弦相似度
#         similarity_score = \
#             cosine_similarity([other_user_ratings_list], [np.array(list(target_user_rating.values()))])[0][0]
#         user_similarity_scores[other_user_id] = similarity_score
#
#     # 对用户相似度得分进行降序排序
#     sorted_similar_user = sorted(user_similarity_scores.items(), key=lambda x: x[1], reverse=True)
#
#     # 选择 TOP N 个相似用户喜欢的景点作为推荐结果
#     recommended_items = set()
#     for similar_user, _ in sorted_similar_user[:top_n]:
#         recommended_items.update(user_rating[similar_user].keys())
#
#     # 过滤目标用户已经评分的景点
#     recommended_items -= set(target_items)
#
#     return list(recommended_items)
#
#
# # 根据推荐的景点 ID 获取完整字段信息
# def get_travel_info(recommended_ids):
#     return list(TravelInfo.objects.filter(id__in=recommended_ids).values())
#
#
# # 测试推荐算法
# if __name__ == '__main__':
#     # 获取用户评分数据
#     user_rating = get_user_rating()
#
#     # 示例：对 user_id=1 的用户生成推荐
#     recommended_ids = user_bases_collaborative_filtering(user_id=1, user_rating=user_rating, top_n=3)
#
#     # 查询推荐景点的完整信息
#     recommended_info = get_travel_info(recommended_ids)
#
#     # 输出结果
#     print(recommended_info)
# # </editor-fold>


import os
import json
import django
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TARecommendation.settings")
django.setup()

from app.models import TravelInfo, UserFavorites

# <editor-fold desc=获取数据和构建模型>

# 获取用户评分数据
def get_user_rating():
    user_rating = []
    for travel in TravelInfo.objects.all():
        comments = json.loads(travel.comments)
        for com in comments:
            if isinstance(com, dict):  # 确保 com 是一个字典
                user_id = com.get('userId', -1)
                score = com.get('score', 0)
                if user_id != -1:
                    user_rating.append((user_id, travel.id, score))
    return user_rating


# 构建神经网络模型
def create_recommendation_model(num_users, num_items, embedding_dim=16):
    # 用户嵌入
    user_input = tf.keras.layers.Input(shape=(1,))
    user_embedding = tf.keras.layers.Embedding(input_dim=num_users, output_dim=embedding_dim)(user_input)
    user_vec = tf.keras.layers.Flatten()(user_embedding)

    # 物品嵌入
    item_input = tf.keras.layers.Input(shape=(1,))
    item_embedding = tf.keras.layers.Embedding(input_dim=num_items, output_dim=embedding_dim)(item_input)
    item_vec = tf.keras.layers.Flatten()(item_embedding)

    # 计算用户和物品交互得分
    dot_product = tf.keras.layers.Dot(axes=1)([user_vec, item_vec])
    output = tf.keras.layers.Activation('sigmoid')(dot_product)

    # 创建模型
    model = tf.keras.models.Model(inputs=[user_input, item_input], outputs=output)
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mse'])

    return model
# </editor-fold>


# <editor-fold desc=训练模型并生成推荐>
# 训练模型并生成推荐
def train_and_recommend(user_ratings, target_user_id, top_n=3):
    # 准备训练数据
    user_ids, item_ids, scores = zip(*user_ratings)
    user_ids = np.array(user_ids)
    item_ids = np.array(item_ids)
    scores = np.array(scores)

    # 确定用户和景点的最大数量
    num_users = user_ids.max() + 1
    num_items = item_ids.max() + 1

    # 拆分训练集和验证集
    X_user_train, X_user_test, X_item_train, X_item_test, y_train, y_test = train_test_split(
        user_ids, item_ids, scores, test_size=0.2, random_state=42
    )

    # 创建推荐模型
    model = create_recommendation_model(num_users, num_items)

    # 训练模型
    model.fit(
        [X_user_train, X_item_train],
        y_train,
        epochs=10,
        batch_size=32,
        validation_data=([X_user_test, X_item_test], y_test)
    )

    # 生成推荐：找到目标用户尚未评分的景点
    all_items = set(range(num_items))
    rated_items = set(item_ids[user_ids == target_user_id])
    unrated_items = list(all_items - rated_items)

    # 预测评分
    predictions = model.predict([np.full(len(unrated_items), target_user_id), np.array(unrated_items)])
    predicted_scores = dict(zip(unrated_items, predictions.flatten()))

    # 按得分排序获取 Top N
    recommended_ids = sorted(predicted_scores, key=predicted_scores.get, reverse=True)[:top_n]

    return recommended_ids
# </editor-fold>


# 根据推荐的景点 ID 获取完整字段信息
def get_travel_info(recommended_ids):
    return list(TravelInfo.objects.filter(id__in=recommended_ids).values())


# 测试推荐算法
if __name__ == '__main__':
    # 获取用户评分数据
    user_ratings = get_user_rating()

    # 示例：对 user_id=1 的用户生成推荐
    recommended_ids = train_and_recommend(user_ratings, target_user_id=1, top_n=3)

    # 查询推荐景点的完整信息
    recommended_info = get_travel_info(recommended_ids)

    # 输出结果
    print(recommended_info)