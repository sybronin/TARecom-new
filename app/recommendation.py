import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import json
import django
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TARecommendation.settings")
django.setup()

from app.models import TravelInfo
from app.models import TravelInfo, UserFavorites


# <editor-fold dec = 这是最初的代码，返回一个字典和景点的ID列表>
# 获取用户评分数据
# def getUser_rating():
#     user_rating = {}
#     for travel in TravelInfo.objects.all():
#         comments = json.loads(travel.comments)
#         for com in comments:
#             if isinstance(com, dict):  # 确保 com 是一个字典
#                 user_id = com.get('userId', -1)
#                 if user_id != -1:
#                     if user_rating.get(user_id, -1) == -1:
#                         user_rating[user_id] = {travel.id: com['score']}
#                     else:
#                         user_rating[user_id][travel.id] = com['score']
#     return user_rating
#
#
# # 协同过滤推荐
# def user_bases_collaborative_filtering(user_id, user_rating, top_n=3):
#     # 获取目标用户评分数据，避免 KeyError
#     target_user_rating = user_rating.get(user_id, {})  # 使用get()避免KeyError
#
#     if not target_user_rating:  # 如果目标用户没有评分数据
#         print(f"User {user_id} has no ratings.")
#         return []
#
#     # 初始化一个字典，用于保存其他用户与目标用户的相似度得分
#     user_similarity_scores = {}
#
#     # 目标用户的评分项目（标题）转化为列表
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
#     # 选择TOP N个相似用户喜欢的景点作为推荐结果
#     recommended_items = set()
#     for similar_user, _ in sorted_similar_user[:top_n]:
#         recommended_items.update(user_rating[similar_user].keys())
#
#     # 过滤目标用户已经评分的景点
#     recommended_items -= set(target_items)
#
#     return list(recommended_items)

# if __name__ == '__main__':
#     rating = getUser_rating()
#     recommend = user_bases_collaborative_filtering(1, rating, top_n=3)
#     print(recommend)
# </editor-fold>


# <editor-fold dec=这是第二段代码，结合了收藏数据进行推荐>
# # 获取用户评分数据并结合收藏数据
# def getUser_rating_with_favorites():
#     user_rating = {}
#
#     # 加载评分数据
#     for travel in TravelInfo.objects.all():
#         comments = json.loads(travel.comments)
#         for com in comments:
#             if isinstance(com, dict):
#                 user_id = com.get('userId', -1)
#                 if user_id != -1:
#                     if user_rating.get(user_id, -1) == -1:
#                         user_rating[user_id] = {travel.id: com['score']}
#                     else:
#                         user_rating[user_id][travel.id] = com['score']
#
#     # 加载收藏数据
#     for favorite in UserFavorites.objects.all():
#         user_id = favorite.user.id
#         travel_id = favorite.travel_info.id
#
#         # 如果用户没有对景点进行评分，但收藏了景点，设置默认评分（例如 4.0）
#         if user_id not in user_rating:
#             user_rating[user_id] = {travel_id: 4.0}
#         else:
#             if travel_id not in user_rating[user_id]:
#                 user_rating[user_id][travel_id] = 4.0
#             else:
#                 # 如果已经有评分，提升评分权重
#                 user_rating[user_id][travel_id] += 1.0  # 增加1分的收藏加权
#
#     return user_rating
#
#
# # 改进的协同过滤推荐
# def user_based_collaborative_filtering(user_id, user_rating, top_n=3):
#     # 获取目标用户评分数据
#     target_user_rating = user_rating.get(user_id, {})
#
#     if not target_user_rating:  # 如果目标用户没有评分数据
#         print(f"User {user_id} has no ratings or favorites.")
#         return []
#
#     # 初始化一个字典，用于保存其他用户与目标用户的相似度得分
#     user_similarity_scores = {}
#
#     # 目标用户的评分项目（景点ID）转化为列表
#     target_items = list(target_user_rating.keys())
#
#     # 计算目标用户与其他用户之间的相似度得分
#     for other_user_id, other_user_ratings in user_rating.items():
#         if other_user_id == user_id:
#             continue
#
#         # 将其他用户的评分转化为 numpy 数组（针对目标项目）
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
#     # 选择 TOP N 个相似用户喜欢的景点 ID 作为推荐结果
#     recommended_items = set()
#     for similar_user, _ in sorted_similar_user[:top_n]:
#         recommended_items.update(user_rating[similar_user].keys())
#
#     # 过滤目标用户已经评分的景点 ID
#     recommended_items -= set(target_items)
#
#     return list(recommended_items)
#
#
# # 示例调用
# if __name__ == '__main__':
#     user_rating = getUser_rating_with_favorites()  # 获取结合收藏数据的用户评分数据
#     recommended_ids = user_based_collaborative_filtering(user_id=1, user_rating=user_rating, top_n=3)  # 推荐景点ID
#     print(recommended_ids)
# </editor-fold>

# <editor-fold dec=第三段代码，返回景点列表>
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
