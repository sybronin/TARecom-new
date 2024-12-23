from django.contrib import admin
from .models import TravelInfo, User


# 注册旅游景点模型到 admin
class TravelInfoAdmin(admin.ModelAdmin):
    # 显示字段
    list_display = ('title', 'level', 'province', 'price', 'saleCount', 'score', 'createTime')

    # 搜索功能（在标题、等级、地址等字段上进行搜索）
    search_fields = ('title', 'level', 'province', 'detailAddress')

    # 筛选功能（支持按省份和爬取时间等筛选）
    list_filter = ('province', 'createTime', 'level')

    # 排序
    ordering = ('-createTime',)

    # 分组显示详细信息
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'level', 'discount', 'province', 'price', 'saleCount', 'score')
        }),
        ('详细信息', {
            'fields': ('detailAddress', 'shortInfo', 'detailIntro', 'detailUrl', 'img_list', 'cover')
        }),
        ('统计信息', {
            'fields': ('star', 'commentsLen', 'comments'),
        }),
    )


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # 列表显示的字段
    list_display = ('id', 'username', 'email', 'createTime', 'sex')

    # 搜索框
    search_fields = ('username', 'email')

    # 过滤器
    list_filter = ('sex', 'createTime')

    # 设置哪些字段是只读的（例如：createTime）
    readonly_fields = ('createTime',)

    # 排序方式
    ordering = ('-createTime',)

    # 表单显示的字段
    fields = ('username', 'email', 'sex', 'address', 'avatar', 'textarea', 'createTime')

# 注册模型
admin.site.register(TravelInfo, TravelInfoAdmin)
# admin.site.register(User, UserAdmin)

# 自定义 Admin 界面的标题和站点说明
admin.site.site_header = '旅游管理后台系统'
admin.site.site_title = '旅游管理系统'
admin.site.index_title = '旅游管理'