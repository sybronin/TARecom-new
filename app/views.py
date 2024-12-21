from django.shortcuts import render,redirect
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib import messages
from app.models import User,TravelInfo,Comment,UserHistory,UserFavorites
from django.http import HttpResponse
from app.utils import GetHomeData,GetPublicData,GetChangSelfIndoData,GetAddCommentsData,GetEchartsData
from .recommendation import getUser_rating, user_bases_collaborative_filtering
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q


#登录
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        username = request.POST['username']
        password = request.POST['password']

        try:
            # 获取用户对象
            user = User.objects.get(username=username)

            # 使用check_password来验证密码
            if check_password(password, user.password):
                # 密码匹配，登录成功
                request.session['username'] = username
                return redirect('/app/home')
            else:
                return HttpResponse('用户名或密码错误')
        except User.DoesNotExist:
            return HttpResponse('用户名或密码错误')

#退出登录
def logout(request):
    request.session.clear()
    return redirect('/app/login')

#用户注册
def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    else:
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repassword = request.POST['repassword']

        # 检查该用户是否已经注册
        try:
            User.objects.get(username=username)
            return HttpResponse('该账号已存在')
        except User.DoesNotExist:
            # 检查输入是否合法
            if not username or not email or not password or not repassword:
                return HttpResponse('所有字段均为必填项')
            if password != repassword:
                return HttpResponse('两次密码不一致')

            # 对密码进行加密
            hashed_password = make_password(password)

            # 创建新用户
            User.objects.create(username=username, email=email, password=hashed_password)

            return redirect('/app/login')

#首页
def home(request):
    username = request.session['username']
    userInfo = User.objects.get(username=username)
    highScoreNum,provinceDicSort, commentsMaxTitle,highfraction,commentsNumMax,provinceTANum = GetHomeData.getHomeTagData()
    #获取首页两个排行榜数据（高分景点推荐榜，销量前十景点榜）
    top10TA,saleCountTop10 = GetHomeData.getRankingData()
    year,month,day = GetHomeData.getTimeNow()
    #获取用户创建时间数据
    userBarCharData = GetHomeData.getUserCreateTimeData()

    return render(request, 'home.html',{
        'userInfo':userInfo,
        'highScoreNum':highScoreNum,
        'provinceDicSort':provinceDicSort,
        'commentsMaxTitle':commentsMaxTitle,
        'highfraction':highfraction,
        'commentsNumMax':commentsNumMax,
        'provinceTANum':provinceTANum,
        'top10TA':top10TA,
        'nowTime':{'year':year,'month':month,'day':day},
        'userBarCharData':userBarCharData,
        'saleCountTop10':saleCountTop10,
    })

#个人信息修改
def changeSelfInfo(request):
    username = request.session['username']
    userInfo = User.objects.get(username=username)
    year, month, day = GetHomeData.getTimeNow()

    if request.method == "POST":
        try:
            # 调用修改个人信息的函数
            GetChangSelfIndoData.changeSelfIndoData(username, request.POST, request.FILES)
            userInfo = User.objects.get(username=username)
            # 如果修改成功，向用户显示成功消息
            messages.success(request, "个人信息修改成功！")
        except Exception as e:
            # 如果修改失败，向用户显示失败消息
            messages.error(request, f"修改失败: {str(e)}")

    return render(request, 'changeSelfInfo.html', {
        'userInfo': userInfo,
        'nowTime': {'year': year, 'month': month, 'day': day},
    })


#修改密码
def changePassword(request):
    username = request.session['username']
    userInfo = User.objects.get(username=username)
    year, month, day = GetHomeData.getTimeNow()

    if request.method == "POST":
        res = GetChangSelfIndoData.changePassword(userInfo, request.POST)

        # 处理密码修改结果
        if res:
            # 如果有错误信息，显示错误消息
            messages.error(request, res)
        else:
            # 密码修改成功
            messages.success(request, "密码修改成功！")

    return render(request, 'changePassword.html', {
        'userInfo': userInfo,
        'nowTime': {'year': year, 'month': month, 'day': day},
    })



#景点数据展示表格
def tableData(request):
    username = request.session['username']
    userInfo = User.objects.get(username=username)
    year, month, day = GetHomeData.getTimeNow()

    # 获取所有旅行数据
    tableData = GetPublicData.getAllTravelInfoMapData()

    # 分页逻辑
    paginator = Paginator(tableData, 10)  # 每页10条数据
    page_number = request.GET.get('page')  # 获取当前页码
    page_obj = paginator.get_page(page_number)  # 获取当前页的数据

    # 处理用户浏览景点的记录
    if request.method == 'POST' and 'travel_id' in request.POST:
        travel_id = request.POST.get('travel_id')
        try:
            user = User.objects.get(username=username)
            travel_info = TravelInfo.objects.get(id=travel_id)

            # 创建用户浏览历史记录
            UserHistory.objects.create(
                user=user,
                travel_info=travel_info,
                browse_time=timezone.now()
            )

            return JsonResponse({'status': 'success'}, status=200)
        except TravelInfo.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'TravelInfo not found'}, status=404)

    return render(request, 'tableData.html', {
        'userInfo': userInfo,
        'nowTime': {'year': year, 'month': month, 'day': day},
        'tableData': page_obj,  # 将分页对象传递给模板
    })

#收藏
def toggle_favorite(request, travel_info_id):
    # 获取当前用户
    username = request.session.get('username')
    if not username:
        return redirect('login')  # 如果没有登录，重定向到登录页面

    user = User.objects.get(username=username)
    travel_info = TravelInfo.objects.get(id=travel_info_id)

    # 判断用户是否已经收藏
    favorite = UserFavorites.objects.filter(user=user, travel_info=travel_info).first()

    if favorite:
        # 如果已收藏，取消收藏
        favorite.delete()
    else:
        # 如果未收藏，添加收藏
        UserFavorites.objects.create(user=user, travel_info=travel_info)

    # 重定向回原来的页面
    return redirect(request.META.get('HTTP_REFERER', 'tableData'))  # 返回上一个页面

#添加评论
def addComments(request, id):
    username = request.session['username']
    userInfo = User.objects.get(username=username)  # 获取当前用户信息
    year, month, day = GetHomeData.getTimeNow()  # 获取当前日期
    travelInfo = TravelInfo.objects.get(id=id)  # 获取景点数据

    if request.method == "POST":
        rate = int(request.POST.get('rate'))  # 获取评分
        content = request.POST.get('content')  # 获取评论内容

        # 创建新的评论对象并保存到数据库
        new_comment = Comment(
            user=userInfo,
            travel_info=travelInfo,
            content=content,
            rate=rate,
        )
        new_comment.save()  # 保存评论数据

        # 重定向到评论列表页面（可以根据需求修改）
        return redirect('/app/tableData')

    return render(request, 'addComments.html', {
        'userInfo': userInfo,
        'nowTime': {'year': year, 'month': month, 'day': day},
        'travelInfo': travelInfo,
        'id': id,
    })

#模糊搜素
def search_travel_info(request):
    username = request.session['username']
    userInfo = User.objects.get(username=username)
    year, month, day = GetHomeData.getTimeNow()
    query = request.GET.get('q', '')  # 获取用户输入的搜索关键词

    # 如果用户有输入搜索词
    if query:
        # 查询联想词
        suggestions = TravelInfo.objects.filter(
            Q(title__icontains=query) |
            Q(level__icontains=query) |
            Q(province__icontains=query) |
            Q(shortInfo__icontains=query) |
            Q(detailAddress__icontains=query) |
            Q(detailIntro__icontains=query) |
            Q(comments__icontains=query)
        ).values_list('title', flat=True).distinct()

        # 对于有查询词的情况，执行完整的查询并分页
        results = TravelInfo.objects.filter(
            Q(title__icontains=query) |
            Q(level__icontains=query) |
            Q(province__icontains=query) |
            Q(shortInfo__icontains=query) |
            Q(detailAddress__icontains=query) |
            Q(detailIntro__icontains=query) |
            Q(comments__icontains=query)
        )
    else:
        results = TravelInfo.objects.all()
        suggestions = []

    # 设置分页
    paginator = Paginator(results, 10)  # 每页显示10个景点
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 检查是否为 AJAX 请求
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(list(suggestions), safe=False)

    return render(request, 'search_results.html', {
        'page_obj': page_obj,
        'query': query,
        'userInfo': userInfo,
        'nowTime': {'year': year, 'month': month, 'day': day},
    })
#数据可视化——城市景点等级分析
def cityChar(request):
    username = request.session['username']
    userInfo = User.objects.get(username=username)
    year, month, day = GetHomeData.getTimeNow()
    #柱状图X、Y数据
    Xdata,Ydata = GetEchartsData.cityCharDataOne()
    #饼状图数据
    resultData = GetEchartsData.cityCharDataTwo()
    return render(request, 'cityChar.html', {
        'userInfo': userInfo,
        'nowTime': {'year': year, 'month': month, 'day': day},
        'cityCharOneData': {
            'Xdata':Xdata,
            'Ydata':Ydata,
        },
        'cityCharTwoData':resultData,
    })

#数据可视化——评分分析
def rateChar(request):
    username = request.session['username']
    userInfo = User.objects.get(username=username)
    year, month, day = GetHomeData.getTimeNow()
    #城市列表,可用于做城市选择下拉框
    cityList = GetPublicData.getCityList()
    #未进行城市选择时默认展示第一个数据
    travelList = GetPublicData.getAllTravelInfoMapData(cityList[0])
    charOneData = GetEchartsData.getRateCharDataOne(travelList)
    charTwoData = GetEchartsData.getRateCharDataTwo(travelList)


    #判断是否进行城市选择请求
    if request.method == "POST":
        travelList = GetPublicData.getAllTravelInfoMapData(request.POST.get('province'))
        #star数据
        charOneData = GetEchartsData.getRateCharDataOne(travelList)
        charTwoData = GetEchartsData.getRateCharDataTwo(travelList)

    return render(request, 'rateChar.html', {
        'userInfo': userInfo,
        'nowTime': {'year': year, 'month': month, 'day': day},
        'cityList': cityList,
        'charOneData': charOneData,
        'charTwoData': charTwoData,
    })

#数据可视化——价格销量分析（价格、销量、折扣）
def priceChar(request):
    username = request.session['username']
    userInfo = User.objects.get(username=username)
    year, month, day = GetHomeData.getTimeNow()
    # 城市列表,可用于做城市选择下拉框
    cityList = GetPublicData.getCityList()
    # 未进行城市选择时默认展示全部城市总数据
    travelList = GetPublicData.getAllTravelInfoMapData()
    #价格折线图x、y数据
    x1data,y1data = GetEchartsData.getPriceCharDataOne(travelList)
    #销量柱状图x、y数据
    x2data,y2data = GetEchartsData.getPriceCharDataTwo(travelList)
    #折扣数据
    discountPieData = GetEchartsData.getPriceCharDataThree(travelList)

    # 判断是否进行城市选择请求
    if request.method == "POST":
        travelList = GetPublicData.getAllTravelInfoMapData(request.POST.get('province'))
        x1data,y1data = GetEchartsData.getPriceCharDataOne(travelList)
        x2data,y2data = GetEchartsData.getPriceCharDataTwo(travelList)
        discountPieData = GetEchartsData.getPriceCharDataThree(travelList)

    return render(request, 'priceChar.html', {
        'userInfo': userInfo,
        'nowTime': {'year': year, 'month': month, 'day': day},
        'cityList': cityList,
        'echartsData':{
            'x1data':x1data,
            'y1data':y1data,
            'x2data':x2data,
            'y2data':y2data,
            'discountPieData':discountPieData,
        }
    })


#数据可视化——评论分析（评论时间、评论评分、评论个数）
def commentsChar(request):
    username = request.session['username']
    userInfo = User.objects.get(username=username)
    year, month, day = GetHomeData.getTimeNow()
    #评论时间折线图x、y数据
    x1Data,y1Data = GetEchartsData.getCommentsCharDataOne()
    #评论评分数据
    commentsScorePieData = GetEchartsData.getCommentsCharDataTwo()
    #评论个数数据
    x2Data,y2Data = GetEchartsData.getCommentsCharDataThree()
    return render(request, 'commentsChar.html', {
        'userInfo': userInfo,
        'nowTime': {'year': year, 'month': month, 'day': day},
        'echartsData': {
            'x1data': x1Data,
            'y1data': y1Data,
            'commentsScorePieData': commentsScorePieData,
            'x2data': x2Data,
            'y2data': y2Data,
        }
    })



#景点推荐
def recommendation(request):
    username = request.session['username']
    userInfo = User.objects.get(username=username)
    year, month, day = GetHomeData.getTimeNow()

    user_rating = getUser_rating()
    recommended = user_bases_collaborative_filtering(userInfo.id, user_rating)
    return render(request, 'recommendation.html', {
        'userInfo': userInfo,
        'nowTime': {'year': year, 'month': month, 'day': day},
        'recommended': recommended,

    })