#!/usr/bin/env python3
"""
Test login UI for each role and verify dashboard access.
"""
import sys
import sqlite3

sys.path.insert(0, '.')

from database.db import get_connection
from auth.security import verify_password
from jepa_site_manager.auth.permissions import get_accessible_site_manager_actions, get_default_dashboard_module
from jepa_site_manager.auth.roles import get_accessible_modules, get_role_label, ROLE_ACCESS

TEST_CREDENTIALS = [
    ("test_superadmin", "TestPass123!@#", "super_admin"),
    ("test_admin", "TestPass123!@#", "admin"),
    ("test_contractor", "TestPass123!@#", "contractor"),
    ("test_projmgr", "TestPass123!@#", "project_manager"),
    ("test_siteengineer", "TestPass123!@#", "site_engineer"),
    ("test_storekeeper", "TestPass123!@#", "store_keeper"),
    ("test_equipofficer", "TestPass123!@#", "equipment_officer"),
    ("test_client", "TestPass123!@#", "client"),
    ("test_consultant", "TestPass123!@#", "consultant"),
]

def test_login_and_dashboard(username, password, expected_role):
    """Simulate login and check dashboard access."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        
        # Simulate login form submission
        user = conn.execute(
            "SELECT id, username, password_hash, role, full_name, email FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        
        if not user:
            return {
                "status": "FAILED",
                "reason": "User not found",
                "login_ok": False,
                "dashboard_ok": False,
            }
        
        # Verify password
        if not verify_password(password, user["password_hash"]):
            return {
                "status": "FAILED",
                "reason": "Invalid password",
                "login_ok": False,
                "dashboard_ok": False,
            }
        
        # Extract user data
        user_id = user["id"]
        actual_role = user["role"]
        full_name = user["full_name"]
        email = user["email"]
        
        # Check if role matches
        if actual_role != expected_role:
            return {
                "status": "FAILED",
                "reason": f"Role mismatch: expected {expected_role}, got {actual_role}",
                "login_ok": False,
                "dashboard_ok": False,
            }
        
        # Try to load dashboard data
        try:
            accessible_modules = get_accessible_modules(actual_role)
            default_module = get_default_dashboard_module(actual_role)
            actions = get_accessible_site_manager_actions(actual_role)
            role_label = get_role_label(actual_role)
            
            # Check ROLE_ACCESS
            if actual_role not in ROLE_ACCESS:
                return {
                    "status": "FAILED",
                    "reason": f"Role {actual_role} not in ROLE_ACCESS",
                    "login_ok": True,
                    "dashboard_ok": False,
                }
            
            return {
                "status": "SUCCESS",
                "user_id": user_id,
                "username": username,
                "role": actual_role,
                "role_label": role_label,
                "full_name": full_name,
                "email": email,
                "login_ok": True,
                "dashboard_ok": True,
                "accessible_modules": sorted(accessible_modules),
                "num_modules": len(accessible_modules),
                "default_module": default_module,
                "num_actions": len(actions),
            }
        except Exception as e:
            return {
                "status": "FAILED",
                "reason": f"Dashboard load error: {e}",
                "login_ok": True,
                "dashboard_ok": False,
            }

def main():
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  LOGIN & DASHBOARD ACCESS TEST FOR ALL 9 ROLES".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    print()
    
    print("="*78)
    print("LOGIN TEST RESULTS")
    print("="*78)
    
    results = []
    
    for username, password, expected_role in TEST_CREDENTIALS:
        result = test_login_and_dashboard(username, password, expected_role)
        results.append(result)
        
        if result["status"] == "SUCCESS":
            print(f"✓ {result['role_label']:20s} | {username:18s} | {result['user_id']:3d} | Modules: {result['num_modules']:2d} | Default: {result['default_module']}")
        else:
            print(f"✗ {expected_role:20s} | {username:18s} | {result['reason']}")
    
    print()
    print("="*78)
    print("DASHBOARD ACCESS SUMMARY")
    print("="*78)
    
    for result in results:
        if result["status"] == "SUCCESS":
            role = result["role"]
            print(f"\n{result['role_label']} ({role})")
            print(f"  User: {result['username']} (ID: {result['user_id']})")
            print(f"  Name: {result['full_name']}")
            print(f"  Email: {result['email']}")
            print(f"  Accessible Modules ({result['num_modules']}): {', '.join(result['accessible_modules'])}")
            print(f"  Default Dashboard: {result['default_module']}")
    
    print()
    print("="*78)
    print("VERIFICATION SUMMARY")
    print("="*78)
    
    successful_logins = sum(1 for r in results if r["status"] == "SUCCESS")
    successful_dashboards = sum(1 for r in results if r.get("dashboard_ok"))
    
    print(f"Successful logins:       {successful_logins}/9")
    print(f"Dashboard loads:         {successful_dashboards}/9")
    print(f"Overall:                 {'✓ ALL TESTS PASSED' if successful_logins == 9 and successful_dashboards == 9 else '✗ SOME TESTS FAILED'}")
    
    # Failed results
    failed = [r for r in results if r["status"] == "FAILED"]
    if failed:
        print(f"\nFailed tests ({len(failed)}):")
        for r in failed:
            print(f"  ✗ {r.get('reason', 'Unknown error')}")
    
    print()
    return results

if __name__ == "__main__":
    results = main()
