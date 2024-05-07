from datetime import date
from rest_framework.test import APITestCase, APIRequestFactory

from interview.inventory.models import Inventory, InventoryLanguage, InventoryType

from interview.order.models import Order
from interview.order.views import DeactivateOrderView


class DeactivateOrderViewTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        lang = InventoryLanguage.objects.create(name="Quenya")
        inv_type = InventoryType.objects.create(name="Movie")
        inventory = Inventory.objects.create(metadata={}, language_id=lang.id, type_id=inv_type.id)

        doc = {"start_date": date.today(), "embargo_date": date.today(), "inventory_id": inventory.id}
        self.order1 = Order.objects.create(is_active=True, **doc)
        self.order2 = Order.objects.create(is_active=True, **doc)

    def test_cannot_deactivate_non_existent_order(self):
        request = self.factory.get(f"/deactivate/{self.order2.id+1}/")
        request.data = {}
        response = DeactivateOrderView().update(request, self.order2.id+1)
        self.assertEqual(response.status_code, 404)

    def test_view_updates_proper_order(self):
        request = self.factory.get(f"/deactivate/{self.order1.id}/")
        request.data = {}
        response = DeactivateOrderView().update(request, self.order1.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], f"Order {self.order1.id} deactivated")

    def test_deactivating_deactivated_order(self):
        self.order1.is_active = False
        self.order1.save()
        request = self.factory.get(f"/deactivate/{self.order1.id}/")
        request.data = {}
        response = DeactivateOrderView().update(request, self.order1.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], f"Order {self.order1.id} deactivated")
