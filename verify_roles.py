#!/usr/bin/env python3
"""Verification script for registration role fix."""
import sys

# Add workspace to path
sys.path.insert(0, '.')

try:
    # Test imports
    from jepa_site_manager.auth.roles import ROLE_LABELS, USER_ROLES, ROLE_ACCESS
    from auth.register import ROLE_CHOICES
    
    print("✓ All imports successful\n")
    
    # Check ROLE_LABELS
    print(f"ROLE_LABELS count: {len(ROLE_LABELS)}")
    print(f"ROLE_LABELS roles: {sorted(ROLE_LABELS.keys())}\n")
    
    # Check USER_ROLES
    print(f"USER_ROLES count: {len(USER_ROLES)}")
    print(f"USER_ROLES roles: {sorted(USER_ROLES.keys())}\n")
    
    # Check ROLE_CHOICES (registration dropdown)
    print(f"ROLE_CHOICES count: {len(ROLE_CHOICES)}")
    role_choices_keys = set(role for label, role in ROLE_CHOICES)
    print(f"ROLE_CHOICES roles: {sorted(role_choices_keys)}\n")
    
    # Check ROLE_ACCESS (dashboard)
    print(f"ROLE_ACCESS count: {len(ROLE_ACCESS)}")
    print(f"ROLE_ACCESS roles: {sorted(ROLE_ACCESS.keys())}\n")
    
    # Expected roles
    expected = {"super_admin", "admin", "contractor", "project_manager", 
                "site_engineer", "store_keeper", "equipment_officer", "client", "consultant"}
    
    print("Expected roles count: 9")
    print(f"Expected roles: {sorted(expected)}\n")
    
    # Verify all match
    issues = []
    if set(ROLE_LABELS.keys()) != expected:
        issues.append("❌ ROLE_LABELS mismatch")
    else:
        print("✓ ROLE_LABELS contains all 9 roles")
    
    if set(USER_ROLES.keys()) != expected:
        issues.append("❌ USER_ROLES mismatch")
    else:
        print("✓ USER_ROLES contains all 9 roles")
    
    if role_choices_keys != expected:
        issues.append("❌ ROLE_CHOICES mismatch")
    else:
        print("✓ Registration dropdown (ROLE_CHOICES) contains all 9 roles")
    
    if set(ROLE_ACCESS.keys()) != expected:
        issues.append("❌ ROLE_ACCESS mismatch")
    else:
        print("✓ ROLE_ACCESS contains all 9 roles")
    
    # Show missing roles
    actual_all = role_choices_keys | set(USER_ROLES.keys()) | set(ROLE_ACCESS.keys())
    missing = expected - actual_all
    new = actual_all - expected
    
    if missing:
        print(f"\n⚠ Missing roles: {sorted(missing)}")
    if new:
        print(f"\n⚠ Unexpected roles: {sorted(new)}")
    
    if not issues:
        print("\n" + "="*50)
        print("✓ REGISTRATION ROLE FIX VERIFIED SUCCESSFULLY")
        print("="*50)
        print("\n Available roles in registration dropdown:")
        for label in sorted(USER_ROLES.values()):
            print(f"  - {label}")
        sys.exit(0)
    else:
        print("\n" + "="*50)
        print("❌ VERIFICATION FAILED")
        print("="*50)
        for issue in issues:
            print(issue)
        sys.exit(1)

except Exception as e:
    print(f"❌ Error during verification: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
