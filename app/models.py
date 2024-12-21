from django.db import models

#旅游景点信息
class TravelInfo(models.Model):
    id = models.AutoField('id',primary_key=True)
    title = models.CharField('景区名',max_length=255,default='')
    level = models.CharField('等级', max_length=255, default='')
    discount = models.CharField('折扣', max_length=255, default='')
    province = models.CharField('省份', max_length=255, default='')
    star = models.CharField('热度', max_length=255, default='')
    saleCount = models.CharField('销量', max_length=255, default='')
    detailAddress = models.CharField('景点详情地址', max_length=2550, default='')
    shortInfo = models.CharField('短评', max_length=255, default='')
    detailUrl = models.TextField('详情地址',  default='')
    score = models.CharField('评分', max_length=255, default='')
    price = models.CharField('价格', max_length=255, default='')
    commentsLen = models.CharField('评论个数', max_length=255, default='')
    detailIntro = models.TextField('详情介绍',  default='')
    img_list = models.ImageField('图片列表', max_length=2550, default='')
    comments = models.TextField('用户评论', default='')
    cover = models.CharField('封面', max_length=2550, default='')
    createTime = models.DateTimeField('爬取时间', auto_now_add=True)
    favorite_travel_info = models.ManyToManyField('TravelInfo', through='UserFavorites', related_name='favorite_travel_info_users', blank=True)

    # 浏览历史
    history_travel_info = models.ManyToManyField('TravelInfo', through='UserHistory',related_name='history_travel_info_users', blank=True)

#用户
class User(models.Model):
    id = models.AutoField('id',primary_key=True)
    username = models.CharField('用户名', max_length=255, default='')
    password = models.CharField('密码', max_length=255, default='')
    email = models.CharField('邮箱', max_length=255, default='')
    sex = models.CharField('性别', max_length=255, default='')
    address = models.CharField('地址', max_length=255, default='')
    avatar = models.ImageField('头像', upload_to='avatar/', default='avatar/default.png')
    textarea = models.CharField('个人简介', max_length=255, default='')
    createTime = models.DateTimeField('创建时间', auto_now_add=True)
    favorite_travel_info = models.ManyToManyField('TravelInfo', through='UserFavorites',related_name='favorite_travel_info_set', blank=True)

#评论
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 外键关联到用户
    travel_info = models.ForeignKey('TravelInfo', on_delete=models.CASCADE)  # 外键关联到景点
    content = models.TextField()  # 评论内容
    rate = models.IntegerField()  # 评分
    created_at = models.DateTimeField(auto_now_add=True)  # 评论时间，自动生成创建时间

    def __str__(self):
        return f"Comment by {self.user.username} on {self.travel_info.title}"

#浏览历史
class UserHistory(models.Model):
    history_id = models.AutoField('浏览ID', primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='user_histories')  # 关联到User表
    travel_info = models.ForeignKey('TravelInfo', on_delete=models.CASCADE, related_name='travel_histories')  # 关联到TravelInfo表
    browse_time = models.DateTimeField('浏览时间', auto_now_add=True)

#用户收藏
class UserFavorites(models.Model):
    favorite_id = models.AutoField('收藏id', primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='user_favorites')  # 关联到User表
    travel_info = models.ForeignKey('TravelInfo', on_delete=models.CASCADE, related_name='travel_favorites')  # 关联到TravelInfo表
    favorite_time = models.DateTimeField('收藏时间', auto_now_add=True)
