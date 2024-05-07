from datetime import datetime, timedelta
from rest_framework.test import APITestCase, APIRequestFactory


from interview.inventory.models import Inventory, InventoryLanguage, InventoryType
from interview.inventory.views import InventoryListCreateView


class InventoryListTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        lang = InventoryLanguage.objects.create(name="Quenya")
        inv_type = InventoryType.objects.create(name="Movie")
        doc = {"metadata": {}, "language_id": lang.id, "type_id": inv_type.id}
        self.new = Inventory.objects.create(**doc)
        self.old = Inventory.objects.create(**doc)
        self.old.created_at -= timedelta(days=1)
        self.old.save()

    def test_no_date_string(self):
        request = self.factory.get("")
        response = InventoryListCreateView().get(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        ids = {item["id"] for item in response.data}
        self.assertEqual(ids, {self.new.id, self.old.id})

    def test_invalid_date_string(self):
        for invalid_str in ["not-a-date", "2024-05-07 16:09:27.664496+00:00"]:
            with self.subTest(f"Testing date filtering with invalid date '{invalid_str}'"):
                request = self.factory.get(f"?created_after={invalid_str}")
                response = InventoryListCreateView().get(request)
                self.assertEqual(response.status_code, 400)
    
    def test_valid_date_string_with_new_date(self):
        request = self.factory.get(f"?created_after={str(self.old.created_at.date())}")
        response = InventoryListCreateView().get(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.new.id)

    def test_valid_date_string_with_old_date(self):
        request = self.factory.get(f"?created_after={str(self.old.created_at.date() - timedelta(days=1))}")
        response = InventoryListCreateView().get(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        ids = {item["id"] for item in response.data}
        self.assertEqual(ids, {self.new.id, self.old.id})
