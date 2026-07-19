# 🏗️ JEPA DESIGN SYSTEM v1.0
## Sprint 2: Product Identity and Professional UI

**Version:** 1.0 (Specification)  
**Date:** June 26, 2026  
**Status:** 📋 **DESIGN SPECIFICATION - AWAITING APPROVAL**  
**Target:** Premium Construction Operations Platform

---

## DESIGN SYSTEM OVERVIEW

The JEPA Design System establishes visual and interaction standards for every screen in the application. This system ensures consistency, professionalism, and construction industry credibility.

### Core Principles
1. **Construction-First** - Every element reflects construction operations
2. **Data-Driven** - Visual design serves information clarity
3. **Professional** - Premium appearance matching construction industry standards
4. **Consistent** - No exceptions to system rules
5. **Accessible** - WCAG AA compliance minimum
6. **Responsive** - Works across screen sizes

---

## SECTION 1: COLOR SYSTEM

### Primary Palette

#### Neutral Scale (Foundation)
```
Name              Hex       Usage
─────────────────────────────────────
Neutral 50        #F9FAFB   Backgrounds
Neutral 100       #F3F4F6   Subtle backgrounds
Neutral 200       #E5E7EB   Borders, dividers
Neutral 300       #D1D5DB   Disabled, muted
Neutral 400       #9CA3AF   Secondary text
Neutral 500       #6B7280   Body text
Neutral 600       #4B5563   Strong text
Neutral 700       #374151   Headings
Neutral 800       #1F2937   Strong headings
Neutral 900       #111827   Black (rarely used)
```

#### Dark Mode Foundation (For Dashboard)
```
Name              Hex       Usage
─────────────────────────────────────
Dark 50           #0F1419   Background
Dark 100          #1A1F2E   Surface
Dark 150          #232B3C   Cards
Dark 200          #2D3847   Elevated surfaces
Dark 300          #3A4557   Hover state
Dark 400          #556B82   Secondary text
Dark 500          #7A8BA3   Muted text
Dark 600          #9CA3AF   Body text
Dark 700          #CBD5E1   Text
Dark 800          #E2E8F0   Light text
```

### Construction Industry Colors

#### Status Colors
```
Name              Hex       Meaning         Usage
────────────────────────────────────────────────────────
Success           #059669   On track        Green
Warning           #D97706   At risk         Amber/Orange
Critical          #DC2626   Blocked         Red
Info              #0891B2   Information     Cyan
Neutral           #6B7280   No status       Gray
```

#### Construction-Specific Colors
```
Name              Hex       Meaning                 Usage
─────────────────────────────────────────────────────────────
Site              #92400E   Physical site           Brown
Equipment         #7C2D12   Equipment/machinery     Dark orange
Materials         #FCD34D   Materials/inventory     Golden
Workers           #3B82F6   Team/workforce          Blue
Safety            #EF4444   Safety/compliance       Red
Progress          #10B981   Completion progress     Green
Timeline          #8B5CF6   Schedule/time           Purple
```

### Role-Based Accent Colors

Each user role has a distinct accent color for visual identity:

```
Role                    Accent Color    Meaning
──────────────────────────────────────────────────
Super Admin             #DC2626 (Red)   Authority, control
Admin                   #EA580C (Orange) Leadership
Project Manager         #0891B2 (Cyan)  Planning, strategy
Site Engineer           #059669 (Green) Operations, action
Store Keeper            #D97706 (Amber) Caution, inventory
Equipment Officer       #7C3AED (Purple) Maintenance, precision
Contractor              #0EA5E9 (Sky)   External, temporary
Client                  #06B6D4 (Cyan)  External, observer
Consultant              #8B5CF6 (Violet) Advisory, expertise
```

### Color Usage Rules

1. **Primary Actions** - Use role accent color
2. **Secondary Actions** - Use Neutral 600
3. **Destructive Actions** - Use Critical (#DC2626)
4. **Disabled Elements** - Use Neutral 300 + 50% opacity
5. **Status Indicators** - Use construction-specific colors
6. **Text on Color** - Use white if background Hex < #888888
7. **Hover States** - Darken by 10% or lighten 10%
8. **Borders** - Use Neutral 200 (light) or Dark 200 (dark)

---

## SECTION 2: TYPOGRAPHY SYSTEM

### Typeface Selection

```
Category          Typeface        Usage                   Fallback
──────────────────────────────────────────────────────────────────
Display           Inter Bold      Headers, titles         Segoe UI
Heading           Inter SemiBold  Section headers         Segoe UI
Body              Inter Regular   Body text               Segoe UI
Mono              Fira Code       Code, timestamps        Courier New
```

**Rationale:** Inter is modern, construction-appropriate, and highly readable at all sizes.

### Typography Scale

#### Heading Hierarchy

```
Level   Name           Font Size   Line Height   Weight    Margin
────────────────────────────────────────────────────────────────────
H1      Display        32px        40px          Bold      24px bottom
H2      Major Heading  24px        32px          SemiBold  16px bottom
H3      Section Header 18px        28px          SemiBold  12px bottom
H4      Card Title     16px        24px          SemiBold  8px bottom
H5      Label          14px        20px          SemiBold  4px bottom
H6      Small Label    12px        18px          SemiBold  2px bottom
```

#### Body Text

```
Level    Name           Font Size   Line Height   Weight    Usage
──────────────────────────────────────────────────────────────────
Body XL  Large text     18px        28px          Regular   UI text
Body L   Regular        16px        24px          Regular   Body text
Body M   Compact        14px        20px          Regular   List items
Body S   Small          13px        20px          Regular   Secondary
Body XS  Tiny           11px        16px          Regular   Meta/captions
```

#### Special Text

```
Code               12px    Fira Code   Regular   Code snippets, timestamps
Label              12px    Inter       Medium    Form labels, badges
Caption            11px    Inter       Regular   Descriptions, hints
Quote              16px    Inter       Italic    Testimonials, callouts
```

### Typography Rules

1. **Line Length** - Max 80 characters for body text (readability)
2. **Contrast** - Minimum 4.5:1 ratio for accessibility
3. **No Color** - All text follows color system rules
4. **No Justification** - Text is left-aligned or centered only
5. **Letter Spacing** - No modifications except headings (+0.5px for H1)
6. **Hierarchy** - Every screen must have clear reading order

### Font Weights

```
400 - Regular (body text, most common)
500 - Medium (labels, secondary emphasis)
600 - SemiBold (headings, strong emphasis)
700 - Bold (display, maximum emphasis)
```

---

## SECTION 3: SPACING SYSTEM

### Base Grid

**Primary Grid: 8px**

All spacing is a multiple of 8px (8, 16, 24, 32, 40, 48, 56, 64, 80, 96)

```
Grid Size   Use Case
───────────────────────────────────────
8px         Tight spacing (icon padding)
16px        Normal padding (components)
24px        Comfortable padding (cards)
32px        Section separation
40px        Large section break
48px        Major section break
64px        Page top/bottom
80px        Header height
96px        Empty state height
```

### Spacing Rules

#### Padding (Internal to Components)

```
Component Type        Padding
──────────────────────────────────
Button               12px 16px (top/bottom, left/right)
Card                 24px
Card Header          20px 24px
Form Input           12px 16px
Table Cell           16px
Badge                4px 8px
Alert                16px 20px
Modal                32px
```

#### Margins (External Spacing)

```
Level       Margin
─────────────────────
H1          0 0 24px 0
H2          0 0 16px 0
H3          0 0 12px 0
Paragraph   0 0 16px 0
List Item   0 0 8px 0
Card        0 0 16px 0
Section     0 0 32px 0
```

#### Gap (Between Items)

```
Container           Gap
──────────────────────────────
Button Row          8px
Card Row            16px
List                8px (compact) / 12px (loose)
Grid                16px
Form Group          12px
Modal Stack         8px
```

---

## SECTION 4: COMPONENT STYLES

### Buttons

#### Button Hierarchy

```
TYPE            USAGE                           STYLING
─────────────────────────────────────────────────────────────
Primary         Main action, default            Role accent bg, white text
Secondary       Alternative action              Neutral 200 bg, Neutral 700 text
Tertiary        Subtle action, link style       No background, colored text
Danger          Destructive action              #DC2626 bg, white text
Ghost           Minimal action                  Transparent, border
```

#### Button Sizes

```
SIZE        HEIGHT   PADDING          FONT SIZE   USAGE
────────────────────────────────────────────────────────
Large       48px     16px 24px        16px        Hero actions
Normal      40px     12px 16px        14px        Most buttons
Small       32px     8px 12px         13px        Compact spaces
Tiny        24px     4px 8px          11px        Inline actions
```

#### Button States

```
STATE       Style
────────────────────────────────────
Default     Base style
Hover       Darken by 10%
Active      Darken by 15%
Disabled    Neutral 300 text, Neutral 100 bg, 50% opacity
Loading     Show spinner, disable interaction
```

#### Button Group Example
```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ [Primary]   │ │ Secondary   │ │ Tertiary    │
├─────────────┤ ├─────────────┤ ├─────────────┤
│ All Actions │ │ Most States │ │ Link-style  │
└─────────────┘ └─────────────┘ └─────────────┘
```

### Cards

#### Card Structure
```
┌─────────────────────────────────────┐
│ Card Header (optional)              │  Padding: 24px
├─────────────────────────────────────┤  Border: 1px Neutral 200
│                                     │
│ Card Body Content                   │  Padding: 24px
│                                     │  Background: White or Dark 150
│                                     │
├─────────────────────────────────────┤
│ Card Footer (optional)              │  Padding: 20px 24px
└─────────────────────────────────────┘
```

#### Card Variants

```
TYPE            USAGE
─────────────────────────────────────────
Default         Standard information card
Outlined        Subtle, deemphasized card
Elevated        Emphasized, focused card
Interactive     Clickable, leading card
Danger          Alert, warning card
Success         Confirmation, positive card
Loading         Placeholder, shimmer effect
```

#### Card Styling Rules
- **Border Radius:** 8px
- **Border:** 1px solid (Neutral 200 light / Dark 200 dark)
- **Shadow:** Subtle (0 1px 3px rgba(0,0,0,0.1))
- **Hover:** Slightly raised shadow, border color darker
- **Padding:** 24px minimum
- **Min Height:** 80px

### Badges & Status Indicators

#### Status Badge
```
┌──────────────────┐
│ ⚫ On Track       │  Padding: 4px 8px
└──────────────────┘  Border Radius: 4px
                      Font Size: 12px
Status Colors:
- Green (#059669) = On Track
- Amber (#D97706) = At Risk
- Red (#DC2626) = Critical
- Gray (#6B7280) = Not Started
```

#### Progress Badge
```
┌─────────────────────────────────┐
│ 65% Complete    [████████░░░]  │  Shows percentage
└─────────────────────────────────┘  With visual bar
```

#### Role Badge
```
┌──────────────────┐
│ ⚒ SITE ENGINEER  │  Role name, role-colored
└──────────────────┘  32px height, 24px top padding
```

### Forms & Inputs

#### Text Input
```
┌─────────────────────────────────┐
│ Placeholder text                │  Height: 40px
└─────────────────────────────────┘  Padding: 12px 16px
                                     Border: 1px Neutral 200
                                     Border Radius: 4px
States:
- Default: Neutral 200 border
- Focus: Role accent color border (2px)
- Filled: Neutral 600 text
- Disabled: Neutral 300, 50% opacity
```

#### Form Group
```
Label (12px SemiBold, Neutral 700)
[Input field] - 40px height
Helper text (11px regular, Neutral 500) - optional
Error text (11px regular, #DC2626) - if validation fails
Spacing: 8px between label and input
```

#### Checkbox & Radio
```
☐ Unchecked (border: 2px Neutral 300)
☑ Checked (fill: role accent color)
◯ Radio unchecked
◉ Radio checked (fill: role accent color)

All: 18px × 18px, 4px border radius
Label: 14px, left-aligned, 8px spacing
```

### Tables

#### Table Header
```
┌─────────────┬─────────────┬─────────────┐
│ Column 1    │ Column 2    │ Column 3    │  Height: 44px
├─────────────┼─────────────┼─────────────┤  Padding: 12px 16px
│ Data        │ Data        │ Data        │  Background: Neutral 100
│ Data        │ Data        │ Data        │  Font: 12px SemiBold
│ Data        │ Data        │ Data        │  Borders: Neutral 200
└─────────────┴─────────────┴─────────────┘  Row height: 40px
```

#### Table Styling Rules
- **Row Height:** 40px
- **Padding:** 12px 16px
- **Border:** 1px Neutral 200
- **Striped Rows:** Every other row background Neutral 50
- **Hover:** Background Neutral 100 (light) or Dark 200 (dark)
- **Border Radius:** 4px (table corners only)
- **Headings:** 12px SemiBold, Neutral 700

### Dialogs & Modals

#### Modal Structure
```
┌─────────────────────────────────────────┐
│ Modal Title                    [×]      │  Padding: 24px
├─────────────────────────────────────────┤
│                                         │
│ Modal Content Area                      │  Padding: 24px
│                                         │  Background: White/Dark
│                                         │
├─────────────────────────────────────────┤
│ [Cancel]  [Confirm]                     │  Padding: 16px 24px
└─────────────────────────────────────────┘  Background: Neutral 50
```

#### Modal Styling Rules
- **Min Width:** 400px
- **Max Width:** 600px (or 90% screen)
- **Border Radius:** 8px
- **Shadow:** 0 10px 40px rgba(0,0,0,0.2)
- **Overlay:** rgba(0,0,0,0.5) (60% opacity)
- **Padding:** 24px
- **Buttons:** Right-aligned, 8px gap

---

## SECTION 5: ICON SYSTEM

### Icon Library Standards

```
Metric              Value
─────────────────────────────
Standard Size       24px
Small Size          16px
Large Size          32px
Icon Weight         2px stroke
Border Radius       2px
Fill Style          Outline (not solid)
Viewbox             24×24
```

### Icon Categories & Usage

#### Navigation Icons
```
Home              Dashboard/landing
Projects          Project view
Materials         Inventory
Workforce         Team/attendance
Equipment         Machinery
Reports           Documentation
Settings          Configuration
Admin              System control
```

#### Status Icons
```
✓ Check Mark      Success/complete
⚠ Warning        Alert/caution
⚡ Alert          Critical/urgent
ℹ Info           Information
◯ Pending        Waiting/in progress
```

#### Action Icons
```
+ Add/Create
- Delete/Remove
✎ Edit
👁 View/Preview
⤳ Export
↻ Refresh
⚙ Settings
...  More options
```

#### Construction-Specific Icons
```
🏗 Site/Project
🏢 Building
⚙ Equipment
📦 Materials
👥 Workforce
🛡 Safety
📊 Analytics
📍 Location
```

### Icon Usage Rules

1. **Color:** Match text color (inherit from context)
2. **Alignment:** Center-aligned with text baseline
3. **Spacing:** 8px gap between icon and text
4. **Size:** 24px for toolbar, 16px for inline, 32px for large
5. **No Rotation:** Except for loading spinners (constant rotation)
6. **Accessibility:** Icon + label, not icon alone
7. **Consistency:** Same icon always means same action

---

## SECTION 6: ELEVATION & DEPTH

### Shadow System

```
Elevation   Shadows                                  Use Case
─────────────────────────────────────────────────────────────
None        No shadow                               Flat, minimal
1           0 1px 2px rgba(0,0,0,0.05)            Subtle depth
2           0 1px 3px rgba(0,0,0,0.1),            Cards, small elements
            0 1px 2px rgba(0,0,0,0.06)
3           0 4px 6px rgba(0,0,0,0.1),            Elevated cards
            0 2px 4px rgba(0,0,0,0.06)
4           0 10px 15px rgba(0,0,0,0.1),          Modal, dropdown
            0 4px 6px rgba(0,0,0,0.05)
5           0 20px 25px rgba(0,0,0,0.1),          Floating panel
            0 10px 10px rgba(0,0,0,0.04)
```

### Border Radius

```
Use Case                      Radius
─────────────────────────────────────
Buttons                       4px
Cards                         8px
Modals                        8px
Inputs                        4px
Badge                         4px
Avatar                        50% (circle)
Large components              12px
```

### Z-Index Scale

```
Z-Index   Component
──────────────────────────────
1         Hover states
100       Dropdowns
200       Tooltips
300       Modals (background)
400       Modals (foreground)
500       Toast notifications
1000      Global alerts
```

---

## SECTION 7: RESPONSIVE DESIGN

### Breakpoints

```
Breakpoint    Width         Devices              Column Count
───────────────────────────────────────────────────────────────
Mobile        < 640px       Phones               1 column
Tablet        640–1024px    Tablets              2 columns
Desktop       1024–1440px   Desktop              3–4 columns
Wide          > 1440px      Large monitors       4+ columns
```

### Responsive Spacing

```
Breakpoint    Padding   Margin   Gap
──────────────────────────────────────
Mobile        16px      8px      12px
Tablet        20px      12px     16px
Desktop       24px      16px     16px
Wide          32px      20px     16px
```

### Navigation Responsiveness

- **Mobile:** Bottom navigation or hamburger menu
- **Tablet:** Left sidebar (collapsed if needed)
- **Desktop:** Full left sidebar + top header
- **Wide:** Left sidebar + top header + right panel

---

## SECTION 8: STATE INDICATORS

### Loading States

#### Skeleton/Placeholder
```
┌─────────────────┐
│ ░░░░░░░░░░░░░░░│  Gray bars (shimmer animation)
│ ░░░░░░░░░░░░░░░│  5-8 placeholders
│ ░░░░░░░░░░░░░░░│  Duration: 1.5 seconds
└─────────────────┘
```

#### Loading Spinner
```
       ↻         Animated circle (3 second rotation)
     ↙   ↗       Stroke: 2px, role accent color
       ↖          
```

### Empty States

```
┌─────────────────────────┐
│      (Icon 64px)        │  Image: 64px icon (role colored)
│                         │  Heading: "No items yet"
│   No items yet          │  Subheading: "Try [action]"
│   Try adding one        │  CTA Button: Create/Add
│                         │  
│    [+ Add Item]         │  Padding: 48px
└─────────────────────────┘
```

### Error States

```
┌─────────────────────────┐
│  ⚠ Error                │  Icon: Warning (red)
│  Something went wrong   │  Title: Error type
│  Please try again       │  Message: Helpful text
│                         │  Button: Retry/Dismiss
│   [Retry]  [Dismiss]    │  
└─────────────────────────┘
```

### Success States

```
┌─────────────────────────┐
│  ✓ Success              │  Icon: Checkmark (green)
│  Changes saved          │  Title: "Success"
│  Your work is secure    │  Message: Confirmation
│                         │  Auto-dismiss: 3 seconds
└─────────────────────────┘
```

---

## SECTION 9: NAVIGATION PATTERNS

### Top Header

```
┌─────────────────────────────────────────────────────────┐
│ [Menu] JEPA  [Breadcrumb / Context]   [User] [Logout]  │
│  16px  32px                            40px   40px      │
│ Height: 64px                                             │
│ Background: Role accent (role-specific)                 │
│ Border Bottom: 1px Neutral 200                          │
└─────────────────────────────────────────────────────────┘
```

### Left Sidebar Navigation

```
┌──────────────┐
│ JEPA Logo    │  Collapsed: 64px width (icons only)
├──────────────┤  Expanded: 240px width (icons + text)
│ [Dashboard]  │  
│ [Projects]   │  Active: Role accent color
│ [Materials]  │  Hover: Neutral 100 background
│ [Workforce]  │  Icon size: 24px
│ [Equipment]  │  Font: 14px regular
│ [Reports]    │  Padding: 12px 16px
│ [Admin]      │  
├──────────────┤  Bottom section:
│ [Settings]   │  Separated by 16px margin
│ [Logout]     │
└──────────────┘
```

### Breadcrumb Navigation

```
Home > Projects > Project Name > Project Phase
Font: 13px regular, Neutral 500
Separator: " > " (3px margin)
Last item: Bold, Neutral 700
Clickable items: Role accent on hover
```

---

## SECTION 10: DATA VISUALIZATION

### Cards for Key Metrics

#### KPI Card
```
┌─────────────────┐
│ Icon (32px)     │  
│ 1,234           │  Large number (24px bold)
│ Active Projects │  Label (14px)
│ ↑ 12% vs last   │  Trend indicator (12px, colored)
└─────────────────┘  
Background: Neutral 50 (light) / Dark 150 (dark)
Border: 1px Neutral 200
Padding: 20px
```

#### Progress Bar
```
Progress: 65%
┌─────────────────────────────┐
│████████████████░░░░░░░░░░░ │  Full width: 100%
└─────────────────────────────┘  Height: 8px
Filled: Role accent color       Border radius: 4px
Empty: Neutral 200              Percentage label: 14px

Status-colored versions:
- On Track: Green
- At Risk: Amber  
- Critical: Red
```

#### Status Timeline
```
●──────●──────●──────○────────○
Start  Phase 1 Phase 2 Phase 3 End
(24px circles, 2px connecting line)
Completed: Role accent color
Current: Darker accent
Future: Neutral 300
```

### Charts (Basic Guidelines)

- **Colors:** Use construction color palette (no more than 5 colors per chart)
- **Legend:** Below chart, left-aligned
- **Axes:** Minimal, Neutral 500 text
- **Grid:** Optional, very light (Neutral 100 or Dark 200)
- **Tooltip:** Dark background, white text, 8px padding
- **Animation:** Smooth (300ms), on load only

---

## SECTION 11: ACCESSIBILITY

### Keyboard Navigation

```
Tab               Navigate to next element
Shift+Tab         Navigate to previous element
Enter             Activate button / submit form
Space             Toggle checkbox / radio
Escape            Close modal / cancel action
Arrow Keys        Navigate within lists/tables
Alt+Key           Access menu shortcuts (if labeled)
```

### Focus States

All interactive elements must have visible focus indicator:

```
Focus Ring      2px solid (role accent color)
Offset          2px from element border
Border Radius   Match element border radius
Contrast        Minimum 3:1 ratio
```

### Color Contrast

```
Text Level              Minimum Contrast
────────────────────────────────────
Large text (18px+)      3:1
Normal text             4.5:1
UI components           3:1
```

### ARIA Labels

- All buttons: `aria-label` if icon-only
- All inputs: `<label>` associated with `for` attribute
- Dialogs: `role="dialog"`, `aria-labelledby`
- Forms: `aria-required="true"` for required fields
- Status: `aria-live="polite"` for dynamic updates

---

## SECTION 12: ANIMATION & TRANSITIONS

### Transition Timing

```
Duration        Use Case
──────────────────────────────────────
100ms           Quick feedback (hover, focus)
200ms           State changes (buttons)
300ms           Transitions (slides, fades)
500ms           Complex transitions
1000ms+         Avoid (too slow)
```

### Transition Easing

```
Function                  Use Case
──────────────────────────────────────
ease-out                  Elements entering
ease-in                   Elements exiting
ease-in-out              Smooth, natural motion
cubic-bezier(...)        Custom, precise control
No easing (linear)       Avoid (robotic feel)
```

### Animation Guidelines

1. **Loading:** Rotating spinner (smooth, infinite)
2. **Transitions:** Fade in/out (300ms ease-out)
3. **Errors:** Shake (200ms, 3 cycles)
4. **Success:** Pulse (500ms, 2 cycles)
5. **Hover:** Slight scale or color shift (100ms ease-out)

---

## SECTION 13: CONSTRUCTION-SPECIFIC COMPONENTS

### Project Status Card
```
┌─────────────────────────────────┐
│ Project Name                    │
│ ▰▰▰▰▰░░░░░ 50% Complete        │  Shows:
│                                 │  - Project name
│ Site A | 12/24 Workers          │  - Progress bar
│ Status: On Track                │  - Location/team
│ Next Milestone: Phase 2 (5d)     │  - Current status
│                                 │  - Next milestone
└─────────────────────────────────┘
```

### Equipment Status Panel
```
┌─────────────────────────────────┐
│ Equipment Name      Status       │
│ Crane A            ● Operational │  Equipment type + status
│ Excavator B        ● Operational │  Color-coded status
│ Concrete Mixer     ● Maintenance │  Maintenance notes
│ Dump Truck 1       ○ Not present │  
│                                 │
│ 3 Operational | 1 Maintenance   │
│ 1 Not Present | 0 Issues        │  Summary at bottom
└─────────────────────────────────┘
```

### Material Consumption Gauge
```
┌─────────────────────────────┐
│ Concrete (m³)               │
│                             │
│      350/500 (70%)          │  Material type
│  ▰▰▰▰▰▰▰░░░ Adequate       │  Consumption bar
│                             │  Status: Adequate/Low/Critical
│  Used: 350m³                │  Detail breakdown
│  Available: 150m³           │
│  Unit Price: $45/m³         │
└─────────────────────────────┘
```

### Daily Activity Timeline
```
06:00 - Day Shift Start        ✓
07:30 - Concrete Pour Begins   ✓
10:15 - Equipment Arrives      ✓
12:00 - Lunch Break            ⏳ In Progress
14:00 - Afternoon Tasks        ○ Pending
17:00 - Day Shift End          ○ Pending

Activity color-coded:
✓ Completed (green)
⏳ In Progress (amber)
○ Pending (gray)
```

### Site Heat Map (Occupancy)
```
[Site Layout with zones colored by activity]
● High Activity (role accent)
● Medium Activity (amber)
● Low Activity (neutral)
● Idle (gray)

Shows where work is happening at a glance
```

---

## SECTION 14: DARK MODE CONSIDERATIONS

### Dark Mode Palette (Dashboard Default)

```
Background        #0F1419 (Neutral 50 equivalent)
Surface           #1A1F2E (Card background)
Elevated          #232B3C (Hover state)
Border            #3A4557 (Subtle border)
Text Primary      #E2E8F0 (Main text)
Text Secondary    #CBD5E1 (Secondary text)
```

### Dark Mode Rules

1. **Always dark for dashboards** (user operates 8am-5pm in sun)
2. **Light mode for reports** (often printed)
3. **Text contrast:** Maintain 4.5:1 minimum
4. **Colors:** Slightly more saturated in dark mode
5. **No pure black:** Use #0F1419 instead
6. **No pure white:** Use #F3F4F6 instead

---

## SECTION 15: DESIGN SYSTEM VIOLATIONS & EXCEPTIONS

### Allowed Exceptions

1. **Construction Photos** - May break grid, must be consistent quality
2. **Third-party Integrations** - Noted with branding, clearly marked
3. **Legacy Data** - Documented as deprecated, migrated over time
4. **Accessibility Overrides** - With accessibility team approval

### Prohibited Violations

- ❌ Custom button styles (must use design system)
- ❌ Off-system colors (must use palette)
- ❌ Inconsistent spacing (must use 8px grid)
- ❌ Non-approved fonts (must use Inter/Fira Code)
- ❌ Undocumented components (must add to system first)
- ❌ Emoji icons (must use icon library)

---

## SECTION 16: IMPLEMENTATION CHECKLIST

### Before Any Screen Is Built

- [ ] Follows color system exactly
- [ ] Uses approved typography scale
- [ ] Spacing follows 8px grid
- [ ] Components use design system
- [ ] Icons from approved library only
- [ ] No custom styling (exceptions documented)
- [ ] Accessibility tested (WCAG AA)
- [ ] Reviewed against design system
- [ ] Approved by design lead

### Before Release

- [ ] All screens audited for consistency
- [ ] No design system violations
- [ ] Dark mode tested (if applicable)
- [ ] Responsive tested (all breakpoints)
- [ ] Accessibility verified
- [ ] Performance tested
- [ ] Cross-browser tested

---

## DESIGN SYSTEM APPROVAL

**This design system is ready for team review.**

Before implementation begins, this system must be:
1. ✅ Reviewed by design team
2. ✅ Approved by product team
3. ✅ Committed to by development team
4. ✅ Documented in team resources
5. ✅ Enforced across all future work

**Status:** 📋 **AWAITING STAKEHOLDER APPROVAL**

---

**JEPA Design System v1.0**  
**Prepared:** June 26, 2026  
**Version:** Complete Specification  
**Next Steps:** Visual mockups of application shell (see separate documents)
