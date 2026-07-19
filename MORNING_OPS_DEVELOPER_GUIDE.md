# Morning Operations Center — Developer Guide

## Quick Start

### Opening the Operations Center
```python
from jepa_site_manager.core.morning_operations_center import open_morning_operations_center

# After user login
open_morning_operations_center(
    parent=None,  # None for main window, or Toplevel parent
    user_id=123,  # User ID from database
    username="julius_osesa",  # Username for greeting
    role="site_engineer"  # Role for filtering data
)
```

### Accessing Operations Service Data
```python
from jepa_site_manager.core.operations_service import (
    get_today_priorities,
    get_role_specific_alerts,
    get_quick_actions,
    get_user_dashboard_greeting,
)

# Get today's priorities for a user
priorities = get_today_priorities(user_id=123, role="project_manager")
# Returns: [
#   {"title": "Submit Daily Report", "priority": 1, "action": "Submit", ...},
#   {"title": "Low Stock Alert", "priority": 2, "action": "Check", ...},
# ]

# Get role-specific alerts
alerts = get_role_specific_alerts(user_id=123, role="site_engineer")
# Returns: [
#   {"title": "High Absence Rate", "severity": "warning", "icon": "⚠️", ...},
# ]

# Get quick action buttons
actions = get_quick_actions(role="site_engineer")
# Returns: [
#   {"label": "Submit Report", "icon": "📋", "action": "submit_report"},
# ]

# Get personalized greeting
greeting = get_user_dashboard_greeting(role="site_engineer", username="julius")
# Returns: "Good morning, Site Engineer julius! Ready for today's operations?"
```

---

## Architecture

### File Structure
```
jepa_site_manager/
├── core/
│   ├── morning_operations_center.py    # Main UI component (900+ lines)
│   ├── operations_service.py           # Business logic (350+ lines)
│   ├── hub.py                          # Legacy hub (still available)
│   └── dashboard_service.py            # Metrics service (reused)
└── ...

auth/
└── login.py                            # Modified entry point
```

### Data Flow
```
login.py (authenticate)
  ↓
open_morning_operations_center()
  ├─→ get_user_dashboard_greeting()
  ├─→ get_active_projects_count()
  ├─→ get_missing_reports_count()
  ├─→ get_low_stock_alerts()
  ├─→ get_today_priorities()
  ├─→ get_role_specific_alerts()
  ├─→ get_quick_actions()
  └─→ get_recent_activity()
```

---

## Customizing the Dashboard

### Adding a New Priority Type

**Step 1:** Add query to `operations_service.py`
```python
def get_high_priority_tasks(user_id: int) -> list[dict]:
    """Get unassigned high-priority tasks assigned to projects."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT t.id, t.title, p.name as project_name, t.due_date
        FROM tasks t
        JOIN projects p ON t.project_id = p.id
        WHERE t.priority = 'high' AND t.assigned_to IS NULL
        ORDER BY t.due_date ASC
        LIMIT 5
    """
    cursor.execute(query)
    return [{"id": r[0], "title": r[1], "project": r[2], "due": r[3]} for r in cursor.fetchall()]
```

**Step 2:** Update `get_today_priorities()` to include new type
```python
def get_today_priorities(user_id: int, role: str) -> list[dict]:
    # ... existing code ...
    
    # Add new priority type
    if role in ("project_manager", "site_engineer"):
        high_tasks = get_high_priority_tasks(user_id)
        for task in high_tasks:
            priorities.append({
                "title": f"Assign Task: {task['title']}",
                "priority": 1,
                "action": "Assign",
                "type": "task",
                "project_id": None,
            })
    
    return sorted(priorities, key=lambda x: x["priority"])[:5]
```

### Adding a New Alert Type

**Step 1:** Query the data
```python
def get_overdue_tasks(user_id: int) -> list[dict]:
    """Get tasks overdue from today."""
    # Similar to above...
```

**Step 2:** Add to `get_role_specific_alerts()`
```python
def get_role_specific_alerts(user_id: int, role: str) -> list[dict]:
    # ... existing code ...
    
    if role in ("project_manager", "site_engineer"):
        overdue = get_overdue_tasks(user_id)
        if overdue:
            alerts.append({
                "title": f"{len(overdue)} Overdue Tasks",
                "severity": "critical",
                "icon": "🔴",
                "description": f"Tasks are overdue",
            })
    
    return sorted(alerts, key=lambda x: {"critical": 0, "warning": 1, "info": 2}[x["severity"]])[:5]
```

### Adding a New Quick Action

**Step 1:** Add to `get_quick_actions()`
```python
def get_quick_actions(role: str) -> list[dict]:
    # ... existing code ...
    
    if role == "site_engineer":
        actions.append({
            "label": "Record Attendance",
            "icon": "👥",
            "action": "record_attendance",
        })
    
    return actions[:4]  # Limit to 4 actions
```

**Step 2:** Add routing in `morning_operations_center.py`
```python
def _on_action(action_type=action["action"]):
    if action_type == "record_attendance":
        open_site_manager_module(window, "workforce", user_id=user_id, role=role_label)
    # ... other actions ...
```

---

## Role-Based Access Control

### How Filtering Works

All service functions accept `role` parameter and filter accordingly:

```python
def get_today_priorities(user_id: int, role: str) -> list[dict]:
    """Role-based filtering example."""
    
    priorities = []
    
    # Only Super Admin and Admin see budget overruns
    if role in ("super_admin", "admin"):
        # ... add budget overrun priorities ...
    
    # Only Project Manager sees pending approvals
    if role == "project_manager":
        # ... add pending material approvals ...
    
    # Only Site Engineer and Equipment Officer see maintenance
    if role in ("site_engineer", "equipment_officer"):
        # ... add equipment maintenance alerts ...
    
    return priorities[:5]
```

### Adding New Role Filters

**Step 1:** Check role in service function
```python
# In operations_service.py
if role in ("project_manager", "admin"):
    # This data is only for these roles
    priorities.append({...})
```

**Step 2:** Verify role exists in `auth/roles.py`
```python
# Check that role is defined
ROLES = {
    "project_manager": "Project Manager",
    # ... other roles ...
}
```

---

## Database Queries

### SQL Patterns Used

#### Get counts
```sql
SELECT COUNT(*) FROM projects WHERE status = 'active' AND owner_id = ?
```

#### Get activity feed
```sql
SELECT timestamp, type, subject, action FROM activity_log 
WHERE project_id IN (SELECT id FROM projects WHERE owner_id = ?)
ORDER BY timestamp DESC LIMIT 6
```

#### Get role-filtered data
```sql
SELECT * FROM materials 
WHERE status = 'low_stock'
AND project_id IN (SELECT id FROM projects WHERE store_keeper_id = ?)
```

### Performance Tips

1. **Use indexes** on `user_id`, `role`, `status`, `timestamp`
2. **Limit results** - Always use LIMIT 5-6 for priorities/alerts
3. **Cache results** - Consider caching metrics for 5-10 minutes
4. **Batch queries** - Combine related queries when possible
5. **Monitor slow queries** - Log queries taking >1000ms

---

## Testing

### Unit Tests

```python
# tests/test_operations_service.py

def test_get_today_priorities_site_engineer():
    priorities = get_today_priorities(user_id=1, role="site_engineer")
    assert isinstance(priorities, list)
    assert all("title" in p for p in priorities)
    assert all("priority" in p for p in priorities)
    assert len(priorities) <= 5

def test_get_today_priorities_filters_by_role():
    site_eng = get_today_priorities(user_id=1, role="site_engineer")
    admin = get_today_priorities(user_id=1, role="admin")
    # Site engineer should see different priorities than admin
    assert site_eng != admin

def test_get_role_specific_alerts():
    alerts = get_role_specific_alerts(user_id=1, role="project_manager")
    assert all("severity" in a for a in alerts)
    assert all(a["severity"] in ("critical", "warning", "info") for a in alerts)

def test_get_quick_actions():
    actions = get_quick_actions("site_engineer")
    assert len(actions) <= 4
    assert all("label" in a and "action" in a for a in actions)
```

### Integration Tests

```python
# Verify entire flow
def test_morning_operations_center_loads():
    from jepa_site_manager.core.morning_operations_center import open_morning_operations_center
    
    # Create test window
    root = tk.Tk()
    try:
        open_morning_operations_center(root, user_id=1, username="test", role="admin")
        root.update()
        # Verify no exceptions
        assert True
    finally:
        root.destroy()
```

---

## Troubleshooting

### Issue: "ImportError: No module named 'jepa_site_manager.core.operations_service'"

**Solution:** Ensure PYTHONPATH includes the project root
```bash
cd /path/to/jepa_auth_system/jepa_auth_system
python app.py
```

### Issue: "TypeError: get_user_dashboard_greeting() missing required argument: 'role'"

**Solution:** Always pass role parameter from normalized role
```python
from dashboard import normalize_role

role = normalize_role("Site_Engineer")  # "site_engineer"
greeting = get_user_dashboard_greeting(role=role, username="julius")
```

### Issue: Dashboard shows no priorities

**Solution:** Check database has data and queries return results
```python
# Debug queries
priorities = get_today_priorities(user_id=1, role="site_engineer")
print(priorities)  # Should show list of dicts

# Check if user has any projects
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM projects WHERE owner_id = 1")
print(cursor.fetchall())
```

### Issue: Slow dashboard load

**Solution:** Profile database queries
```python
import time

start = time.time()
priorities = get_today_priorities(user_id=1, role="site_engineer")
print(f"Priority query took {time.time() - start:.2f}s")

# If >1s, add index on user_id/project_id
```

---

## Future Enhancements

### Phase 1: Real-time Updates
- WebSocket for live priority/alert updates
- Automatic refresh when new priority arrives
- Sound/desktop notifications

### Phase 2: Customization
- Drag-and-drop to reorder sections
- Toggle sections on/off
- Pin important priorities
- User preferences storage

### Phase 3: Analytics
- Historical trends (priorities over time)
- Performance metrics (how fast are issues resolved?)
- Role-based KPIs (Site Engineer response time, Store Keeper fulfillment rate)

### Phase 4: Mobile
- Responsive design for tablets/mobile
- Touch-friendly UI
- Offline mode with sync

### Phase 5: Integration
- API endpoints for third-party integrations
- Webhooks for external systems
- Slack/WhatsApp notifications
- Email digest subscriptions

---

## Contact

For questions about the Morning Operations Center:
1. Check this developer guide first
2. Review operation_service.py docstrings
3. Review morning_operations_center.py comments
4. Check SPRINT_1_SUMMARY.md for architecture details

---

**Last Updated:** June 26, 2026  
**Version:** 1.0  
**Status:** Production Ready
