import unittest

from database.db import get_connection
from jepa_site_manager.projects.models import ProjectRecord
from jepa_site_manager.projects.project_service import create_project, list_projects
from jepa_site_manager.reports.report_service import create_report, list_reports
from jepa_site_manager.materials.material_service import create_material, list_materials


class JEPAProjectModuleTests(unittest.TestCase):
    def test_project_report_and_material_services_work(self):
        project_name = "Test JEPA Project"
        project_id = create_project(
            ProjectRecord(
                project_name=project_name,
                client="Test Client",
                location="Test Location",
                budget=25000,
                start_date="2026-06-11",
                end_date="2026-07-11",
                status="Planning",
            )
        )

        self.assertGreater(project_id, 0)
        projects = list_projects()
        self.assertTrue(any(item["project_name"] == project_name for item in projects))

        report_id = create_report(project_id, "2026-06-11", "Sunny", "Foundation works", "10", "No issues")
        self.assertGreater(report_id, 0)
        self.assertTrue(any(item["project_id"] == project_id for item in list_reports(project_id)))

        material_id = create_material(project_id, "Cement", 50, "Test Supplier", "2026-06-11", None, 50)
        self.assertGreater(material_id, 0)
        self.assertTrue(any(item["project_id"] == project_id for item in list_materials(project_id)))

        with get_connection() as conn:
            conn.execute("DELETE FROM site_reports WHERE id = ?", (report_id,))
            conn.execute("DELETE FROM materials WHERE id = ?", (material_id,))
            conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            conn.commit()


if __name__ == "__main__":
    unittest.main()
