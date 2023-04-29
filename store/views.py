from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from . import serializers
from .models import Cart, CartItem, Collection, Customer, Order, OrderItem, Product, Review
from .permissions import IsAdminOrReadOnly, ViewCustomerHistoryPermission


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = serializers.CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ['title']
    search_fields = ['title']


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related('collection').all()
    serializer_class = serializers.ProductSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    permission_classes = [IsAdminOrReadOnly]
    ordering_fields = ['title', 'last_update', 'price']
    search_fields = ['title', 'collection__title']


class ReviewViewSet(ModelViewSet):
    serializer_class = serializers.ReviewSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['products_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['products_pk']}


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = serializers.CartSerializer
    permission_classes = [IsAuthenticated]


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['carts_pk']).select_related('product')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return serializers.UpdateCartItemSerializer
        return serializers.CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['carts_pk']}


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = serializers.CustomerSerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self):
        return Response('ok')

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == 'GET':
            serializer = serializers.CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = serializers.CustomerSerializer(
                customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        customer = Customer.objects.only(
            'id').get_or_create(user_id=self.request.user.id)
        return Order.objects.filter(customer_id=customer)

    def create(self, request, *args, **kwargs):
        serializer = serializers.CreateOrderSerializer(
            data=request.data, context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = serializers.OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.CreateOrderSerializer
        return serializers.OrderSerializer

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}
