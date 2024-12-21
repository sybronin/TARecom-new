from django.urls import path,include
from rest_framework import permissions
from app import views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="API Title",
        default_version='v1',
        description="API Description",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('login/',views.login,name='login'),
    path('register/',views.register, name='register'),
    path('home/',views.home,name='home'),
    path('logout/',views.logout,name='logout'),
    path('changeSelfInfo/',views.changeSelfInfo,name='changeSelfInfo'),
    path('changePassword/',views.changePassword, name='changePassword'),
    path('tableData/',views.tableData,name='tableData'),
    path('addComments/<int:id>',views.addComments,name='addComments'),
    path('cityChar/',views.cityChar,name='cityChar'),
    path('rateChar/',views.rateChar,name='rateChar'),
    path('priceChar',views.priceChar,name='priceChar'),
    path('commentsChar/',views.commentsChar,name='commentsChar'),
    path('recommendation/',views.recommendation,name='recommendation'),
    path('toggle_favorite/<int:travel_info_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('search/', views.search_travel_info, name='search_travel_info'),
]