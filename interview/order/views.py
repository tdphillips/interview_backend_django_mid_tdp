from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from interview.order.models import Order, OrderTag
from interview.order.serializers import OrderSerializer, OrderTagSerializer

# Create your views here.
class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    

class OrderTagListCreateView(generics.ListCreateAPIView):
    queryset = OrderTag.objects.all()
    serializer_class = OrderTagSerializer


class DeactivateOrderView(APIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def update(self, request, id):
        try:
            order = self.queryset.get(id=id)
        except Order.DoesNotExist:
            #  Q about organization's operating procedures - this could be used to scrape for order existence;
            #  Is this okay in this instance or, my preference, should this be a 200 OK
            return Response({"message:" "Cannot deactivate nonexistent order"}, status=404)
        #  Ask product owner, can orders that have/have not started be deactivated? Same q for embargo dates.
        #  Should we have a deactivation date?
        order.is_active = False
        serializer = self.serializer_class(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": f"Order {order.pk} deactivated"})
        else:
            return Response({"message": "Order deactivation failed", "details": serializer.errors}, status=400)
