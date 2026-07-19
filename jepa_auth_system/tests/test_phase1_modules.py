import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from jepa_site_manager.auth.permissions import can_access_module
from jepa_site_manager.materials.material_service import create_material, list_materials
from jepa_site_manager.projects.project_service import create_project, list_projects
from jepa_site_manager.reports.pdf_export import generate_report_pdf
from jepa_site_manager.reports.report_service import create_report, list_reports


class Phase1ModulesTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_jepa.db"
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        schema_path = Path(__file__).resolve().parents[1] / "jepa_site_manager" / "database" / "schema.sql"
        self.conn.executescript(schema_path.read_text(encoding="utf-8"))
        self.conn.commit()

        self.patcher = mock.patch("jepa_site_manager.database.connection.get_connection", return_value=self.conn)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.conn.close()
        self.temp_dir.cleanup()

    def test_project_report_and_material_services_work(self):
        project_id = create_project(
            project_name="Tower Build",
            client="Acme Ltd",
            location="Kampala",
            budget=1200000,
            start_date="2026-06-01",
            end_date="2026-12-15",
            status="Active",
            created_by=1,
        )

        report_id = create_report(
            project_id=project_id,
            report_date="2026-06-10",
            weather="Sunny",
            activities="Excavation and rebar work",
            workers_present="18",
            issues="Minor delay on delivery",
            created_by=1,
        )

        material_id = create_material(
            project_id=project_id,
            material_name="Cement",
            quantity=50,
            supplier="BuildMart",
            date_received="2026-06-08",
            balance=45,
            created_by=1,
        )

        self.assertGreater(project_id, 0)
        self.assertGreater(report_id, 0)
        self.assertGreater(material_id, 0)

        projects = list_projects()
        reports = list_reports(project_id)
        materials = list_materials(project_id)

        self.assertEqual(projects[0]['project_name'], 'Tower Build')
        self.assertEqual(reports[0]['project_id'], project_id)
        self.assertEqual(materials[0]['material_name'], 'Cement')

    def test_pdf_export_generates_a_report_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'site_report.pdf'

            result = generate_report_pdf(
                output_path=path,
                project_name='Tower Build',
                client='Acme Ltd',
                report_date='2026-06-10',
                summary='Daily progress complete and materials delivered.',
            )

            self.assertTrue(result)
            self.assertTrue(path.exists())
            self.assertGreater(path.stat().st_size, 0)

    def test_role_permissions_cover_project_and_client_access(self):
        self.assertTrue(can_access_module('project_manager', 'projects'))
        self.assertTrue(can_access_module('site_engineer', 'reports'))
        self.assertFalse(can_access_module('client', 'attendance'))
        self.assertFalse(can_access_module('client', 'users'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
