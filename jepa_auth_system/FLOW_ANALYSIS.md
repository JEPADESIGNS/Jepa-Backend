# SYSTEM BEHAVIOR & CONNECTION AUDIT

## PART A: CRITICAL FLOW ANALYSIS

### FLOW 1: CREATE REPORT

**Current Implementation:**
```
open_report_view()
  ↓
User enters form (project_id REQUIRED manually)
  ↓
Click "Save Daily Report" button
  ↓
_save() function:
  - Validates project_id (int parse)
  - Calls create_report(project_id, report_date, ..., created_by=user_id)
  ↓
IF SUCCESS:
  - Shows messagebox: "Site report created with id {report_id}"
  - Calls _refresh() to reload tree
  ↓
User sees updated tree with new report

PROBLEMS IDENTIFIED:
1. ❌ user_id is passed but never actually sent by caller
   - open_report_view() called as: open_report_view(parent)
   - user_id parameter in signature but never populated
   - DEFAULT: user_id = None (always)

2. ❌ No context tracking
   - User must manually type project_id
   - No "Current Project" context
   - No indication this report affects compliance

3. ❌ Silent save-and-refresh
   - Messagebox shown but immediately disappears
   - _refresh() called but user sees generic tree update
   - No indication of impact: "Report added. Compliance now 95%"

4. ❌ No propagation
   - Report saved but dashboard not updated
   - Missing reports counter not recalculated
   - No notification to admins

5. ❌ Hardcoded date
   - "2026-06-11" as default
   - Not today's actual date
   - Outdated value persists
```

---

### FLOW 2: CREATE TASK

**Current Implementation:**
```
open_task_view()
  ↓
User enters form (project_id REQUIRED manually)
  ↓
Click "Save Task" button
  ↓
_save() function:
  - Validates project_id, site_id (ints)
  - Calls create_task(project_id, site_id, title, status, progress_percent, assigned_user_id=user_id)
  ↓
IF SUCCESS:
  - Shows messagebox: "Task created with id {task_id}"
  - Calls _refresh() to reload tree
  ↓
User sees updated tree with new task

PROBLEMS IDENTIFIED:
1. ❌ assigned_user_id NOT TRACKED
   - Parameter assigned_user_id=user_id
   - BUT user_id is passed from open_task_view(user_id=None)
   - DEFAULT: user_id = None (always)
   - Task created with NO ASSIGNEE

2. ❌ Assigned user cannot see their task
   - No "My Tasks" view exists
   - Even if task has assigned_user_id, user can't find it
   - User must manually filter by user_id in database

3. ❌ No assignment notification
   - Task assigned but assignee not notified
   - No alert in notifications
   - No email sent

4. ❌ Context missing
   - User must manually enter project_id
   - No indication: "Task created in Project X"

5. ❌ No workflow validation
   - Can create task with any status (not enforced)
   - progress_percent can be any number (no validation)
   - No state machine

FLOW CONSEQUENCE:
- Tasks created but invisible to assigned users
- Tasks pile up in database
- No one knows what they're supposed to do
- System feels broken to team members
```

---

### FLOW 3: CREATE ISSUE

**Current Implementation:**
```
open_issue_view()
  ↓
Project selector shows dropdown (GOOD - has context)
  ↓
Click "New Issue" button
  ↓
_open_form(None) opens modal
  ↓
User fills: title, description, priority, status
  ↓
Click "Save" button
  ↓
_save() function:
  - Validates project_id (from dropdown)
  - Calls create_issue(pid, title, description, priority, created_by=None, status=status)
  ↓
IF SUCCESS:
  - Modal closes (top.destroy())
  - Calls refresh() to reload tree
  ↓
User sees updated tree with new issue

PROBLEMS IDENTIFIED:
1. ❌ NO SUCCESS FEEDBACK
   - Modal just closes silently
   - User doesn't know if save worked or failed
   - No messagebox confirmation
   - No visual indication: "Issue #123 created"

2. ❌ created_by=None
   - create_issue() called with created_by=None (always)
   - Issue not linked to creator
   - Can't track "who raised this issue"

3. ❌ assigned_to_id NOT CAPTURED
   - Form doesn't have "Assign to" field
   - Issues can't be assigned
   - No one owns the resolution

4. ❌ No notification on assignment
   - Even if assigned, no alert sent
   - Assigned user doesn't know they have new issue

5. ⚠️ PARTIAL GOOD: Project context
   - Project selected from dropdown (GOOD)
   - Issue properly linked to project (GOOD)
   - refresh() filtered by project (GOOD)
   BUT:
   - Assigned_to_id field NOT in form
   - Can't assign to user

FLOW CONSEQUENCE:
- Issues created but no one assigned
- No tracking of who reported vs who's fixing
- No notifications
- User doesn't get feedback modal closed silently
```

---

## PART B: MISSING CONNECTIONS

### Connection 1: User Context (CRITICAL)

```
CURRENT STATE:
- open_report_view(parent: tk.Misc, user_id: int | None = None, ...)
- open_task_view(parent: tk.Misc, user_id: int | None = None, ...)
- open_issue_view(parent: tk.Misc)  ← NO user_id parameter

HOW THEY'RE CALLED:
- From hub.py via open_site_manager_module(parent, module_name, role)
- dashboard/__init__.py router calls views with ONLY parent:
  - open_project_manager(parent)
  - open_report_view(parent)
  - open_attendance_view(parent)
  - open_equipment_view(parent)
  - NO user_id or project_id passed

CONSEQUENCE:
- Views have user_id parameter but never receive it
- Default: user_id = None (always)
- All actions recorded with user_id = None
- Can't track who did what

SOLUTION NEEDED:
- Global session object tracking: current_user_id, current_project_id
- Pass these through ALL view opens
- Store in module-level variable accessible to all
```

### Connection 2: Project Context (CRITICAL)

```
CURRENT STATE:
- Each view asks user to manually enter project_id
- No "current project" context
- Switching between modules requires re-entering project_id

CONSEQUENCE:
- Poor UX: "project_id = 1" required in every form
- Data fragmentation: each module sees different data
- No unified workspace per project

SOLUTION NEEDED:
- Session tracks current_project_id
- All views auto-filter by current project
- UI shows "Currently working on: Project X"
- Switching projects updates session context
```

### Connection 3: Data Propagation (MAJOR)

```
CURRENT STATE - Report Created:
- Report saved to database
- _refresh() reloads report tree
- But NO propagation to:
  - Dashboard compliance metrics
  - Admin missing-reports counter
  - Project summary

CURRENT STATE - Task Created:
- Task saved to database
- _refresh() reloads task tree
- But NO propagation to:
  - Assigned user's "My Tasks" view
  - Project progress calculation
  - Dashboard

CURRENT STATE - Issue Created:
- Issue saved to database
- refresh() reloads issue tree
- But NO propagation to:
  - Project issue count
  - Dashboard alerts
  - Assigned user notification

CONSEQUENCE:
- System feels disconnected
- Data exists but is invisible
- No cross-module awareness

SOLUTION NEEDED:
- Observer pattern or event system
- When report created → trigger compliance recalculation
- When task created → notify assigned user
- When issue created → update project summary
- All dashboards subscribe to data changes
```

### Connection 4: User Session (CRITICAL)

```
CURRENT STATE:
- After login, hub.py opens
- hub.py gets role parameter: open_site_manager_hub(role=row["role"])
- BUT user_id NOT PASSED to hub

- Module router receives NO user context:
  - open_site_manager_module(parent, module_name, role=role)
  - Views called WITHOUT user_id

CONSEQUENCE:
- No way to know "who is using the system right now"
- user_id always None
- Can't create personal dashboards
- All operations anonymous

SOLUTION NEEDED:
- Pass user_id through entire flow
- Store in global session object
- All modules access: session.current_user_id
```

### Connection 5: Navigation (LOGIC)

```
CURRENT STATE:
- hub.py shows modules
- Click "Overview" → calls open_site_manager_module(parent, "overview", role)
- "overview" case → calls open_site_manager_hub(parent, role=role)
- This opens ANOTHER hub window

CONSEQUENCE:
- Clicking "Overview" opens new hub (stacking windows)
- Potential infinite recursion/stack of windows
- No clear entry point

SOLUTION NEEDED:
- "Overview" should show personal dashboard (NOT hub)
- hub should not loop back to itself
- Clear entry point: login → personal dashboard → modules
```

---

## PART C: WHAT'S NOT HAPPENING (Silent Actions)

### Silent Save Pattern Across All Views

Each view has this pattern:
```python
def _save():
    data = collect_from_form()
    create_entity(data)
    messagebox.showinfo("Saved", f"Entity created with id {id}")
    _refresh()
```

**PROBLEMS:**
1. ❌ No data validation feedback (only project_id validated)
2. ❌ No error handling if create fails
3. ❌ No propagation to related views
4. ❌ No refresh of OTHER windows that should see the data
5. ❌ No notification system integration
6. ❌ No audit logging with user_id
7. ❌ No "undo" capability
8. ❌ No related data updates (e.g., project progress)

---

## PART D: MISSING INFRASTRUCTURE

### Missing: Global Session Context

```python
# DOES NOT EXIST:
class UserSession:
    current_user_id: int | None = None
    current_project_id: int | None = None
    current_role: str | None = None
    theme: str = "dark"

# Needed in: utils/session.py
# Usage: from utils.session import session
# Then: session.current_user_id
```

### Missing: Event/Observer System

```python
# DOES NOT EXIST:
class EventBus:
    def subscribe(event_type, callback)
    def publish(event_type, data)

# Events needed:
- "task_created" → notify assigned user
- "report_created" → recalculate compliance
- "issue_created" → update project summary
- "project_updated" → refresh dashboards
```

### Missing: Success Feedback System

```python
# DOES NOT EXIST:
class Feedback:
    def success(message: str)
    def error(message: str)
    def info(message: str)
    def log_action(action, details)

# Needed for consistent feedback
```

---

## PART E: IMPLEMENTATION PRIORITY

### TIER 1: Blocking Issues (Do First)
1. ✋ Delete hub_new.py (syntax errors)
2. 🔄 Create global session context (utils/session.py)
3. 👤 Pass user_id through login → hub → views
4. 📦 Pass current_project_id through views
5. 🔄 Track current user at login

### TIER 2: Fix Silent Actions
6. 📣 Add success/error feedback to all saves
7. 🔄 Fix _refresh() to actually reload data
8. 📢 Add confirmation with details on save
9. ✅ Validate all inputs before save

### TIER 3: Connect Modules
10. 🔔 Create event system for data changes
11. 🔄 Wire up notifications when data created
12. 📊 Propagate data to dashboards
13. 👥 Make assigned tasks visible to users

### TIER 4: Fix Navigation
14. 🗺️ Fix hub loops (overview → personal dashboard)
15. 🧭 Ensure consistent entry points
16. 📍 Fix window stacking issues

---

## PART F: EXPECTED BEHAVIOR AFTER FIXES

### After Fixes Applied:

**Create Report:**
```
User logged in as: John (user_id=5)
Current project: "Project Alpha"
  ↓
Click Reports module
  ↓
Report form shows: "Project Alpha" (not empty, not requiring input)
  ↓
User fills: Weather, Activities, Workers
  ↓
Click "Save Daily Report"
  ↓
Backend:
  - Saves with user_id=5 (tracked)
  - Updates compliance: "Day 5: Reports 4/4 (100%)"
  - Triggers event: "report_created"
  - Logs: "John created report for Project Alpha"
  ↓
UI Feedback:
  - Success message: "Report saved! Compliance: 100%"
  - Report appears in tree immediately
  - (Optional) Dashboard updates compliance meter
```

**Create Task:**
```
User: Sarah (admin, user_id=3)
Current project: "Project Beta"
  ↓
Click Tasks module
  ↓
Form shows: "Project Beta" (context preserved)
  ↓
User fills: Title "Review Materials", Assign to "Mike"
  ↓
Click "Save Task"
  ↓
Backend:
  - Saves with assigned_user_id=7 (Mike's id)
  - created_by=3 (Sarah)
  - Triggers event: "task_assigned_to_user_7"
  - Sends notification to Mike: "New task assigned to you"
  - Logs audit: "Sarah assigned task to Mike"
  ↓
UI Feedback:
  - Success message: "Task assigned to Mike"
  - Task appears in tree
  - Mike gets notification immediately
  - Mike sees task in "My Tasks" view
```

**Create Issue:**
```
User: Tom (site_engineer, user_id=8)
Current project: "Project Gamma"
  ↓
Click Issues module
  ↓
Form shows: "Project Gamma" + Assign field (NEW)
  ↓
User fills: Title, Description, Priority, Assign to "PM"
  ↓
Click "Save Issue"
  ↓
Feedback (IMMEDIATE):
  - ✓ Success modal: "Issue #456 created and assigned to PM"
  - ✓ Issue appears in tree immediately
  - ✓ PM gets notification: "New critical issue assigned to you"
  - ✓ Project summary shows: "4 open issues"
  ↓
Later:
  - PM sees issue in their dashboard
  - PM can filter by "My Issues"
  - Audit log shows: "Tom raised Issue #456"
```

---

## PART G: FILES TO MODIFY

```
TIER 1 - CRITICAL:
□ jepa_site_manager/core/hub_new.py → DELETE
□ utils/session.py → CREATE (new file)
□ auth/login.py → MODIFY (track user_id)
□ jepa_site_manager/core/hub.py → MODIFY (receive user_id, project_id)
□ dashboard/__init__.py → MODIFY (pass context to views)

TIER 2 - FEEDBACK:
□ jepa_site_manager/reports/report_view.py → MODIFY
□ jepa_site_manager/tasks/task_view.py → MODIFY
□ jepa_site_manager/issues/issue_view.py → MODIFY

TIER 3 - EVENTS:
□ utils/event_bus.py → CREATE (new file)
□ jepa_site_manager/core/activity_service.py → MODIFY

TIER 4 - NAVIGATION:
□ jepa_site_manager/core/hub.py → MODIFY (fix loops)
□ dashboard/__init__.py → MODIFY (fix entry points)
```

