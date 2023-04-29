from rest_framework_nested import routers
from . import views


router = routers.DefaultRouter()
router.register('collection', views.CollectionViewSet, basename='collections')
router.register('product', views.ProductViewSet, basename='products')
router.register('cart', views.CartViewSet, basename='carts')
router.register('customer', views.CustomerViewSet, basename='customers')
router.register('order', views.OrderViewSet, basename='orders')

products_router = routers.NestedDefaultRouter(
    router, 'product', lookup='products')
products_router.register('reviews', views.ReviewViewSet,
                         basename='product-reviews')

carts_router = routers.NestedDefaultRouter(router, 'cart', lookup='carts')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + products_router.urls + carts_router.urls
