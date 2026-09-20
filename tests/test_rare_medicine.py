"""Tests for the Rare Medicine Query Service module in BaleMed."""

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.database import init_db
from app.handlers import route_update
from app.main import app
from app.rare_medicine import (
    DEFAULT_RARE_MEDICINE_CATALOG,
    DesignatedPharmacy,
    RareMedicineItem,
    RareMedicineQueryService,
    build_patient_guidance_text,
    get_rare_medicine_service,
    normalize_query_text,
    reset_rare_medicine_service_for_test,
)


class RareMedicineServiceTests(unittest.TestCase):
    def setUp(self):
        reset_rare_medicine_service_for_test()
        self.service = RareMedicineQueryService()

    def tearDown(self):
        reset_rare_medicine_service_for_test()

    def test_text_normalization(self):
        # Arabic kaf and yeh normalization
        self.assertEqual(normalize_query_text("تراستوزوماب"), "تراستوزوماب")
        self.assertEqual(normalize_query_text("تراستوزوماب"), normalize_query_text("تراستوزوماب"))
        # Kashida and diacritics removal
        self.assertEqual(normalize_query_text("هـِرسِپـتین"), "هرسپتین")
        # Arabic/Persian digits
        self.assertEqual(normalize_query_text("۲۹ فروردین"), "29 فروردین")
        # English lowercasing and punctuation stripping
        self.assertEqual(normalize_query_text("IVIG (5g/100ml)"), "ivig 5g 100ml")
        self.assertEqual(normalize_query_text(None), "")

    def test_default_catalog_loaded(self):
        self.assertGreaterEqual(self.service.total_count, 7)
        ivig = self.service.get_by_id("rare-ivig")
        self.assertIsNotNone(ivig)
        self.assertIn("اکتوگام", ivig.brand_names)
        self.assertEqual(ivig.scarcity_level, "critical")

    def test_search_by_persian_generic_and_brand_name(self):
        # Search by Persian generic
        res_trast = self.service.search("تراستوزوماب")
        self.assertGreaterEqual(res_trast.matched_count, 1)
        self.assertEqual(res_trast.items[0].id, "rare-trastuzumab")

        # Search by Persian brand
        res_herceptin = self.service.search("هرسپتین")
        self.assertGreaterEqual(res_herceptin.matched_count, 1)
        self.assertEqual(res_herceptin.items[0].id, "rare-trastuzumab")

        # Search by English brand
        res_octagam = self.service.search("Octagam")
        self.assertGreaterEqual(res_octagam.matched_count, 1)
        self.assertEqual(res_octagam.items[0].id, "rare-ivig")

    def test_search_filtering_by_province_and_category(self):
        # Filter by province
        res_tehran = self.service.search(query="IVIG", province="تهران")
        self.assertGreaterEqual(res_tehran.matched_count, 1)

        # Filter by non-existent province for this drug
        res_kerman = self.service.search(query="IVIG", province="بوشهر")
        self.assertEqual(res_kerman.matched_count, 0)

        # Filter by category
        res_onco = self.service.search(category="انکولوژی")
        self.assertGreaterEqual(res_onco.matched_count, 2)
        for item in res_onco.items:
            self.assertIn("انکولوژی", item.category)

    def test_search_filtering_by_scarcity_and_supply_status(self):
        res_crit = self.service.search(scarcity_level="critical")
        self.assertGreaterEqual(res_crit.matched_count, 2)
        for item in res_crit.items:
            self.assertEqual(item.scarcity_level, "critical")

        res_central = self.service.search(supply_status="central_pharmacy_only")
        self.assertGreaterEqual(res_central.matched_count, 1)
        self.assertEqual(res_central.items[0].id, "rare-temozolomide")

    def test_search_pagination(self):
        res_all = self.service.search(limit=2, offset=0)
        self.assertEqual(len(res_all.items), 2)
        self.assertGreater(res_all.matched_count, 2)

        res_next = self.service.search(limit=2, offset=2)
        self.assertEqual(len(res_next.items), 2)
        self.assertNotEqual(res_all.items[0].id, res_next.items[0].id)

    def test_get_by_id_and_missing(self):
        item = self.service.get_by_id("rare-factor-viii")
        self.assertIsNotNone(item)
        self.assertIn("فاکتور هشت", item.generic_name)

        missing = self.service.get_by_id("non-existent-id")
        self.assertIsNone(missing)

    def test_list_categories_provinces_pharmacies(self):
        categories = self.service.list_categories()
        self.assertIn("غدد و متابولیک", categories)

        provinces = self.service.list_provinces()
        self.assertIn("تهران", provinces)
        self.assertIn("فارس", provinces)

        pharmacies = self.service.list_pharmacies(province="تهران")
        self.assertGreaterEqual(len(pharmacies), 4)
        names = [p["name"] for p in pharmacies]
        self.assertIn("داروخانه ۱۳ آبان", names)

    def test_format_replies(self):
        ivig = self.service.get_by_id("rare-ivig")
        detail = self.service.format_detail_reply(ivig)
        self.assertIn("اطلاعات داروی کمیاب", detail)
        self.assertIn("ایمونوگلوبولین", detail)
        self.assertIn("سامانه ۱۹۰", detail)
        self.assertIn("داروخانه ۲۹ فروردین", detail)

        # Search summary with match
        res_match = self.service.search("سوماتروپین")
        summary_single = self.service.format_search_summary_reply(res_match)
        self.assertIn("سوماتروپین", summary_single)

        # Search summary with no match
        res_none = self.service.search("داروی غیرواقعی ۱۲۳")
        summary_none = self.service.format_search_summary_reply(res_none)
        self.assertIn("یافت نشد", summary_none)
        self.assertIn("۱۹۰", summary_none)

    def test_sqlite_persistence_and_seeding(self):
        conn = sqlite3.connect(":memory:")
        try:
            service_db = RareMedicineQueryService(connection=conn)
            # Verify rows in DB
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM rare_medicines")
            count = cursor.fetchone()[0]
            self.assertGreaterEqual(count, 7)

            # Add custom item and persist
            custom = RareMedicineItem(
                id="rare-custom-1",
                generic_name="داروی آزمایشی خاص",
                brand_names=["تست‌دارو"],
                category="تحقیقاتی",
                dosage_form="آمپول",
                strength="10mg",
                scarcity_level="critical",
                supply_status="available_limited",
                designated_pharmacies=[
                    DesignatedPharmacy(
                        name="داروخانه آزمایشی",
                        province="تهران",
                        city="تهران",
                        address="خیابان آزادی",
                        phone="021-11111111",
                    )
                ],
                required_documents=["نسخه ویژه"],
            )
            service_db.add_or_update(custom)
            self.assertEqual(service_db.get_by_id("rare-custom-1").generic_name, "داروی آزمایشی خاص")
        finally:
            conn.close()


class RareMedicineBotAndApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        self.orig_db = os.environ.get("DATABASE_PATH")
        os.environ["DATABASE_PATH"] = str(self.db_path)
        init_db()
        reset_rare_medicine_service_for_test()

    def tearDown(self):
        reset_rare_medicine_service_for_test()
        if self.orig_db is not None:
            os.environ["DATABASE_PATH"] = self.orig_db
        else:
            os.environ.pop("DATABASE_PATH", None)
        self.temp_dir.cleanup()

    def test_bot_rare_command_without_args(self):
        payload = {
            "message": {
                "message_id": 999,
                "chat": {"id": "rare-chat"},
                "text": "/rare",
            }
        }
        res = route_update(payload)
        self.assertTrue(res["ok"])
        reply_text = res["reply_result"]["text"]
        self.assertIn("راهنمای جستجوی داروی کمیاب", reply_text)
        self.assertIn("/rare هرسپتین", reply_text)
        self.assertIn("۱۹۰", reply_text)

    def test_bot_rare_command_with_search_query(self):
        payload = {
            "message": {
                "message_id": 1000,
                "chat": {"id": "rare-chat"},
                "text": "/rare هرسپتین",
            }
        }
        res = route_update(payload)
        self.assertTrue(res["ok"])
        reply_text = res["reply_result"]["text"]
        self.assertIn("تراستوزوماب", reply_text)
        self.assertIn("داروخانه‌های توزیع‌کننده منتخب", reply_text)

    def test_fastapi_rare_medicine_endpoints(self):
        client = TestClient(app)

        # GET /api/v1/rare-medicines/search
        resp = client.get("/api/v1/rare-medicines/search?q=IVIG")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreaterEqual(data["matched_count"], 1)
        self.assertEqual(data["items"][0]["id"], "rare-ivig")

        # GET /api/v1/rare-medicines/categories
        resp_cat = client.get("/api/v1/rare-medicines/categories")
        self.assertEqual(resp_cat.status_code, 200)
        self.assertIn("categories", resp_cat.json())

        # GET /api/v1/rare-medicines/pharmacies
        resp_pharm = client.get("/api/v1/rare-medicines/pharmacies?province=تهران")
        self.assertEqual(resp_pharm.status_code, 200)
        pharmacies = resp_pharm.json()["pharmacies"]
        self.assertGreaterEqual(len(pharmacies), 1)

        # GET /api/v1/rare-medicines/{medicine_id}
        resp_detail = client.get("/api/v1/rare-medicines/rare-ivig")
        self.assertEqual(resp_detail.status_code, 200)
        self.assertEqual(resp_detail.json()["generic_name"], "ایمونوگلوبولین وریدی (IVIG)")

        # GET 404 for missing
        resp_404 = client.get("/api/v1/rare-medicines/not-found-id")
        self.assertEqual(resp_404.status_code, 404)

        # GET /local/rare-medicines/summary
        resp_summary = client.get("/local/rare-medicines/summary")
        self.assertEqual(resp_summary.status_code, 200)
        self.assertGreaterEqual(resp_summary.json()["total_rare_medicines"], 7)


if __name__ == "__main__":
    unittest.main()
