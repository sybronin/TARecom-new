# # <editor-fold dec=第三段代码，返回景点列表>
from sklearn.metrics.pairwise import cosine_similarity
import os
import json
import django
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TARecommendation.settings")
django.setup()

from app.models import TravelInfo
from app.models import TravelInfo, UserFavorites

# 获取用户评分数据
def get_user_rating():
    user_rating = {}
    for travel in TravelInfo.objects.all():
        comments = json.loads(travel.comments)
        for com in comments:
            if isinstance(com, dict):  # 确保 com 是一个字典
                user_id = com.get('userId', -1)
                if user_id != -1:
                    if user_rating.get(user_id, -1) == -1:
                        user_rating[user_id] = {travel.id: com['score']}  # 使用景点 ID
                    else:
                        user_rating[user_id][travel.id] = com['score']
    return user_rating


# 协同过滤推荐
def user_bases_collaborative_filtering(user_id, user_rating, top_n=3):
    # 获取目标用户评分数据，避免 KeyError
    target_user_rating = user_rating.get(user_id, {})

    if not target_user_rating:  # 如果目标用户没有评分数据
        print(f"User {user_id} has no ratings.")
        return []

    # 初始化一个字典，用于保存其他用户与目标用户的相似度得分
    user_similarity_scores = {}

    # 目标用户的评分项目（景点 ID）转化为列表
    target_items = list(target_user_rating.keys())

    # 计算目标用户与其他用户之间的相似度得分
    for other_user_id, other_user_ratings in user_rating.items():
        if other_user_id == user_id:
            continue

        # 将其他用户的评分转化为numpy数组（对于目标项目）
        other_user_ratings_list = np.array([
            other_user_ratings.get(item, 0) for item in target_items
        ])

        # 计算余弦相似度
        similarity_score = \
            cosine_similarity([other_user_ratings_list], [np.array(list(target_user_rating.values()))])[0][0]
        user_similarity_scores[other_user_id] = similarity_score

    # 对用户相似度得分进行降序排序
    sorted_similar_user = sorted(user_similarity_scores.items(), key=lambda x: x[1], reverse=True)

    # 选择 TOP N 个相似用户喜欢的景点作为推荐结果
    recommended_items = set()
    for similar_user, _ in sorted_similar_user[:top_n]:
        recommended_items.update(user_rating[similar_user].keys())

    # 过滤目标用户已经评分的景点
    recommended_items -= set(target_items)

    return list(recommended_items)


# 根据推荐的景点 ID 获取完整字段信息
def get_travel_info(recommended_ids):
    return list(TravelInfo.objects.filter(id__in=recommended_ids).values())
#
#
# 测试推荐算法
if __name__ == '__main__':
    # 获取用户评分数据
    user_rating = get_user_rating()

    # 示例：对 user_id=1 的用户生成推荐
    recommended_ids = user_bases_collaborative_filtering(user_id=1, user_rating=user_rating, top_n=3)

    # 查询推荐景点的完整信息
    recommended_info = get_travel_info(recommended_ids)

    # 输出结果
    print(recommended_info)
# </editor-fold>


# 神经网络算法


# 第四个修改算法

# 获取当前时间
def getTimeNow():
    now = datetime.now()
    return now.year, now.month, now.day


# 获取用户评分数据
def get_user_rating():
    """
    提取用户评分数据，用于推荐算法。
    返回 [(user_id, item_id, score), ...] 的列表。
    """
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


# 创建推荐模型
def create_recommendation_model(num_users, num_items, embedding_dim=16):
    """
    创建基于嵌入的神经网络推荐模型。

    参数：
        num_users: 用户总数
        num_items: 景点总数
        embedding_dim: 嵌入维度

    返回：
        一个编译后的 Keras 模型。
    """
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


# 基于神经网络的协同过滤算法
def user_bases_collaborative_filtering(user_id, user_rating, top_n=3):
    """
    使用基于神经网络的协同过滤实现推荐。

    参数：
        user_id: 当前用户的 ID
        user_rating: 用户评分数据 [(user_id, item_id, score), ...]
        top_n: 推荐的景点数量

    返回：
        List[int]: 推荐的景点 ID 列表
    """
    # 提取用户和景点评分数据
    user_ids, item_ids, scores = zip(*user_rating)
    user_ids = np.array(user_ids)
    item_ids = np.array(item_ids)
    scores = np.array(scores)

    # 确定用户和景点的数量
    num_users = user_ids.max() + 1
    num_items = item_ids.max() + 1

    # 创建并训练推荐模型
    model = create_recommendation_model(num_users, num_items)
    model.fit(
        [user_ids, item_ids],
        scores,
        epochs=10,
        batch_size=32
    )

    # 生成推荐：找到目标用户尚未评分的景点
    rated_items = set(item_ids[user_ids == user_id])  # 当前用户评分过的景点
    all_items = set(range(num_items))  # 系统中所有景点
    unrated_items = list(all_items - rated_items)  # 未评分的景点

    if not unrated_items:
        print(f"User {user_id} has no unrated items to recommend.")
        return []

    # 预测评分
    predictions = model.predict([np.full(len(unrated_items), user_id), np.array(unrated_items)])
    predicted_scores = dict(zip(unrated_items, predictions.flatten()))

    # 获取预测评分最高的 Top N 项
    recommended_ids = sorted(predicted_scores, key=predicted_scores.get, reverse=True)[:top_n]

    return recommended_ids


# 根据推荐的景点 ID 获取完整字段信息
def get_travel_info(recommended_ids):
    """
    根据推荐的景点 ID 查询数据库，返回完整的景点信息。
    """
    return list(TravelInfo.objects.filter(id__in=recommended_ids).values())


# 测试函数
if __name__ == '__main__':
    # 模拟 Django 环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TARecommendation.settings')
    import django

    django.setup()

    # 获取用户评分数据
    print("Fetching user rating data...")
    user_ratings = get_user_rating()

    # 假定测试用户 ID 为 1
    test_user_id = 1
    print(f"Generating recommendations for user {test_user_id}...")

    # 调用推荐算法生成推荐
    recommended_ids = user_bases_collaborative_filtering(test_user_id, user_ratings, top_n=5)

    # 获取推荐景点的详细信息
    recommended_info = get_travel_info(recommended_ids)

    # 输出推荐结果
    print(f"Recommended spots for user {test_user_id}:")
    for info in recommended_info:
        print(info)
