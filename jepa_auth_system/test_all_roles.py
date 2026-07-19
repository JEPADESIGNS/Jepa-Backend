#!/usr/bin/env python3
"""
Create test accounts for all 9 roles and test login/dashboard for each.
"""
import sys
import sqlite3
from datetime import datetime

sys.path.insert(0, '.')

from database.db import get_connection
from auth.security import hash_password, hash_answer, generate_recovery_code
from auth.validators import normalise_username, normalise_email
from jepa_site_manager.auth.roles import USER_ROLES, ROLE_LABELS

# Test account details
TEST_ACCOUNTS = [
    {
        "role": "super_admin",
        "username": "test_superadmin",
        "email": "test.superadmin@jepa.test",
        "phone": "+256701000001",
        "password": "TestPass123!@#",
        "full_name": "Super Admin Test",
    },
    {
        "role": "admin",
        "username": "test_admin",
        "email": "test.admin@jepa.test",
        "phone": "+256701000002",
        "password": "TestPass123!@#",
        "full_name": "Admin Test",
    },
    {
        "role": "contractor",
        "username": "test_contractor",
        "email": "test.contractor@jepa.test",
        "phone": "+256701000003",
        "password": "TestPass123!@#",
        "full_name": "Contractor Test",
    },
    {
        "role": "project_manager",
        "username": "test_projmgr",
        "email": "test.projmgr@jepa.test",
        "phone": "+256701000004",
        "password": "TestPass123!@#",
        "full_name": "Project Manager Test",
    },
    {
        "role": "site_engineer",
        "username": "test_siteengineer",
        "email": "test.siteengineer@jepa.test",
        "phone": "+256701000005",
        "password": "TestPass123!@#",
        "full_name": "Site Engineer Test",
    },
    {
        "role": "store_keeper",
        "username": "test_storekeeper",
        "email": "test.storekeeper@jepa.test",
        "phone": "+256701000006",
        "password": "TestPass123!@#",
        "full_name": "Store Keeper Test",
    },
    {
        "role": "equipment_officer",
        "username": "test_equipofficer",
        "email": "test.equipofficer@jepa.test",
        "phone": "+256701000007",
        "password": "TestPass123!@#",
        "full_name": "Equipment Officer Test",
    },
    {
        "role": "client",
        "username": "test_client",
        "email": "test.client@jepa.test",
        "phone": "+256701000008",
        "password": "TestPass123!@#",
        "full_name": "Client Test",
    },
    {
        "role": "consultant",
        "username": "test_consultant",
        "email": "test.consultant@jepa.test",
        "phone": "+256701000009",
        "password": "TestPass123!@#",
        "full_name": "Consultant Test",
    },
]

def create_test_accounts():
    """Create test accounts for all 9 roles."""
    print("="*70)
    print("CREATING TEST ACCOUNTS FOR ALL 9 ROLES")
    print("="*70)
    
    created = []
    errors = []
    
    for account in TEST_ACCOUNTS:
        try:
            username = normalise_username(account["username"])
            email = normalise_email(account["email"])
            phone = account["phone"]
            password = account["password"]
            role = account["role"]
            full_name = account["full_name"]
            
            pw_hash = hash_password(password)
            answer_hash = hash_answer("test_answer")
            recovery_code = generate_recovery_code()
            
            with get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO users
                        (username, email, phone, password_hash, role,
                         full_name, gender, security_question, security_answer_hash, recovery_code)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        username, email, phone, pw_hash, role,
                        full_name, "Prefer not to say",
                        "What is your middle name?", answer_hash, recovery_code,
                    ),
                )
                conn.commit()
                user_id = conn.execute(
                    "SELECT id FROM users WHERE username = ?", (username,)
                ).fetchone()["id"]
            
            print(f"✓ Created: {role:20s} | {username:18s} | ID: {user_id}")
            created.append({
                "role": role,
                "username": username,
                "user_id": user_id,
                "password": password,
            })
        except Exception as e:
            errors.append((account["role"], str(e)))
            print(f"✗ Failed: {account['role']:20s} | Error: {e}")
    
    print()
    return created, errors


def verify_database_entries(created_accounts):
    """Verify test accounts exist in database with correct roles."""
    print("="*70)
    print("VERIFYING DATABASE ENTRIES")
    print("="*70)
    
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        
        for account in created_accounts:
            row = conn.execute(
                "SELECT id, username, role, email FROM users WHERE id = ?",
                (account["user_id"],)
            ).fetchone()
            
            if row:
                db_role = row["role"]
                expected_role = account["role"]
                status = "✓" if db_role == expected_role else "✗"
                print(f"{status} ID {account['user_id']:3d} | {account['username']:18s} | Role in DB: {db_role:20s}")
            else:
                print(f"✗ ID {account['user_id']:3d} | {account['username']:18s} | NOT FOUND IN DATABASE")
    
    print()


def test_authentication(created_accounts):
    """Test login for each account."""
    print("="*70)
    print("TESTING AUTHENTICATION FOR EACH ROLE")
    print("="*70)
    
    from auth.security import verify_password
    
    auth_results = []
    
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        
        for account in created_accounts:
            try:
                # Simulate login
                row = conn.execute(
                    "SELECT id, username, password_hash, role FROM users WHERE username = ?",
                    (account["username"],)
                ).fetchone()
                
                if not row:
                    print(f"✗ {account['role']:20s} | {account['username']:18s} | NOT FOUND")
                    auth_results.append((account["role"], False, "User not found"))
                    continue
                
                # Verify password
                if verify_password(account["password"], row["password_hash"]):
                    stored_role = row["role"]
                    print(f"✓ {account['role']:20s} | {account['username']:18s} | Auth OK | DB Role: {stored_role}")
                    auth_results.append((account["role"], True, "Authentication successful"))
                else:
                    print(f"✗ {account['role']:20s} | {account['username']:18s} | Password mismatch")
                    auth_results.append((account["role"], False, "Password verification failed"))
                    
            except Exception as e:
                print(f"✗ {account['role']:20s} | {account['username']:18s} | Error: {e}")
                auth_results.append((account["role"], False, str(e)))
    
    print()
    return auth_results


def test_imports():
    """Test all imports needed for dashboard and permissions."""
    print("="*70)
    print("TESTING IMPORTS FOR DASHBOARD & PERMISSIONS")
    print("="*70)
    
    import_tests = []
    
    imports_to_test = [
        ("jepa_site_manager.auth.roles", ["ROLE_LABELS", "USER_ROLES", "ROLE_ACCESS", "normalize_role"]),
        ("jepa_site_manager.auth.permissions", ["can_access_module", "get_accessible_site_manager_actions"]),
        ("dashboard", ["get_default_dashboard_module", "get_role_title", "ROLE_ACCESS"]),
        ("auth.register", ["ROLE_CHOICES", "validate_registration_role"]),
    ]
    
    for module_name, attributes in imports_to_test:
        try:
            module = __import__(module_name, fromlist=attributes)
            for attr in attributes:
                if hasattr(module, attr):
                    print(f"✓ {module_name:40s} | {attr}")
                    import_tests.append((module_name, attr, True))
                else:
                    print(f"✗ {module_name:40s} | {attr} NOT FOUND")
                    import_tests.append((module_name, attr, False))
        except Exception as e:
            print(f"✗ {module_name:40s} | Import failed: {e}")
            import_tests.append((module_name, "import", False))
    
    print()
    return import_tests


def test_permissions_for_roles(created_accounts):
    """Test permissions for each role."""
    print("="*70)
    print("TESTING PERMISSIONS FOR EACH ROLE")
    print("="*70)
    
    from jepa_site_manager.auth.permissions import get_accessible_site_manager_actions, get_default_dashboard_module
    from jepa_site_manager.auth.roles import get_accessible_modules
    
    permission_results = []
    
    for account in created_accounts:
        try:
            role = account["role"]
            
            # Get accessible modules
            accessible = get_accessible_modules(role)
            num_modules = len(accessible)
            
            # Get default module
            default_module = get_default_dashboard_module(role)
            
            # Get available actions
            actions = get_accessible_site_manager_actions(role)
            num_actions = len(actions)
            
            print(f"✓ {role:20s} | Modules: {num_modules:2d} | Actions: {num_actions:2d} | Default: {default_module}")
            permission_results.append((role, True, f"Modules: {num_modules}, Actions: {num_actions}"))
            
        except Exception as e:
            print(f"✗ {role:20s} | Error: {e}")
            permission_results.append((role, False, str(e)))
    
    print()
    return permission_results


def main():
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  COMPREHENSIVE ROLE TESTING - ALL 9 ROLES".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    print()
    
    # Step 1: Create test accounts
    created_accounts, creation_errors = create_test_accounts()
    
    if creation_errors:
        print(f"⚠ {len(creation_errors)} account creation errors encountered")
        for role, error in creation_errors:
            print(f"  - {role}: {error}")
        print()
    
    # Step 2: Verify database entries
    verify_database_entries(created_accounts)
    
    # Step 3: Test authentication
    auth_results = test_authentication(created_accounts)
    
    # Step 4: Test imports
    import_results = test_imports()
    
    # Step 5: Test permissions
    permission_results = test_permissions_for_roles(created_accounts)
    
    # Summary
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    successful_auth = sum(1 for _, success, _ in auth_results if success)
    successful_permissions = sum(1 for _, success, _ in permission_results if success)
    import_pass = all(success for _, _, success in import_results)
    
    print(f"Accounts created:        {len(created_accounts)}/9")
    print(f"Authentication passed:   {successful_auth}/9")
    print(f"Permissions loaded:      {successful_permissions}/9")
    print(f"All imports successful:  {'✓ Yes' if import_pass else '✗ No'}")
    
    # List test account credentials
    print()
    print("="*70)
    print("TEST ACCOUNT CREDENTIALS")
    print("="*70)
    print("Use these to test login:")
    print()
    
    for account in created_accounts:
        print(f"Role: {account['role']:20s} | Username: {account['username']:18s} | Password: {account['password']}")
    
    print()
    
    # Return results for further testing
    return created_accounts, auth_results, permission_results


if __name__ == "__main__":
    created_accounts, auth_results, permission_results = main()
