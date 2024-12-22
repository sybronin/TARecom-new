from app.models import TravelInfo,Comment,User
from app.utils.GetHomeData import getTimeNow
import json

#通过景点id获取景点全部数据
def getTravelInfoById(id):
    travel = TravelInfo.objects.get(id=id)
    # 获取该景点所有评论
    comments = Comment.objects.filter(travel_info=travel).order_by('-created_at')  # 按照评论时间倒序排列
    travel.comments = comments  # 将评论列表添加到景点数据中
    return travel

#增添评论
def addComents(commentData):
    year, month, day = getTimeNow()
    travelInfo = commentData['travelInfo']

    # 解析 JSON 字符串为 Python 列表
    if isinstance(travelInfo.comments, str):
        travelInfo.comments = json.loads(travelInfo.comments)

    # 追加评论
    travelInfo.comments.append({
        'author': commentData['userInfo'].username,
        'score': commentData['rate'],
        'comment': commentData['content'],
        'date': str(year) + '-' + str(month) + '-' + str(day),
        'userId': commentData['userInfo'].id,
    })

    # 将列表转换回 JSON 字符串
    travelInfo.comments = json.dumps(travelInfo.comments)

    # 保存数据
    travelInfo.save()
