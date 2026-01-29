# 📊 Database Tables Checklist & Quick Reference

## Complete Table List (6 Tables)

### ✅ TABLE 1: user_profiles
**Purpose:** User account and personal information
```
Stores: id, email, full_name, phone, age, caste, location, 
        annual_income, family_income, occupation, education_level,
        business_type, farm_size
Key usage: Eligibility checks, personalization, profile display
```

### ✅ TABLE 2: user_conversations  
**Purpose:** Track separate chat sessions/conversations
```
Stores: id, user_id, conversation_name, domain, language, timestamps
Key usage: Save conversations, allow multiple chats per user,
           load previous conversations
```

### ✅ TABLE 3: conversation_messages
**Purpose:** Store individual messages in conversations
```
Stores: id, conversation_id, user_id, role (user/assistant), content, timestamp
Key usage: Save message history, load chat transcripts,
           enable conversation persistence
```

### ✅ TABLE 4: user_eligible_schemes
**Purpose:** Track schemes user is eligible for
```
Stores: id, user_id, scheme_name, domain, eligibility_reason,
        applied (true/false), application_date
Key usage: Show "You're eligible for these schemes",
           track applied schemes, dashboard display
```

### ✅ TABLE 5: user_applications
**Purpose:** Track scheme applications and their status
```
Stores: id, user_id, scheme_name, domain, status (pending/submitted/approved/rejected),
        application_link, notes, timestamps
Key usage: Application dashboard, status tracking,
           history of applications
```

### ✅ TABLE 6: user_documents
**Purpose:** Store documents for verification
```
Stores: id, user_id, document_type, storage_path, verified (true/false),
        verification_notes, timestamp
Key usage: Document storage, verification status,
           eligibility validation
```

---

## What Each Table Stores (Examples)

### user_profiles Example
```
user_id:     "uuid-123"
email:       "john@example.com"
full_name:   "John Doe"
age:         35
caste:       "OBC"
location:    "Maharashtra, Pune"
annual_income: 300000
education:   "Bachelor's Degree"
occupation:  "Teacher"
```

### user_conversations Example
```
id:                   "conv-456"
user_id:              "uuid-123"
conversation_name:    "Education Schemes - Jan 29"
domain:               "Education"
language:             "English"
created_at:           "2026-01-29 10:30:00"
```

### conversation_messages Example
```
id:              "msg-789"
conversation_id: "conv-456"
user_id:         "uuid-123"
role:            "user"
content:         "I want to pursue a master's degree"
created_at:      "2026-01-29 10:31:00"

id:              "msg-790"
conversation_id: "conv-456"
user_id:         "uuid-123"
role:            "assistant"
content:         "Great! Based on your income and education..."
created_at:      "2026-01-29 10:31:30"
```

### user_eligible_schemes Example
```
id:                  "scheme-001"
user_id:             "uuid-123"
scheme_name:         "Post-Matric Scholarship (SC/ST)"
domain:              "Education"
eligibility_reason:  "Age 20-35, pursuing Masters, OBC category eligible"
applied:             true
application_date:    "2026-01-28"
```

### user_applications Example
```
id:                "app-001"
user_id:           "uuid-123"
scheme_name:       "PM-KISAN"
domain:            "Agriculture"
status:            "pending"
application_link:  "https://pmkisan.gov.in/apply"
notes:             "Submitted on Jan 28"
```

### user_documents Example
```
id:                  "doc-001"
user_id:             "uuid-123"
document_type:       "Aadhar Card"
storage_path:        "user_documents/uuid-123/aadhar.pdf"
verified:            true
verification_notes:  "Verified by admin on Jan 29"
```

---

## How Tables Connect to Each Other

```
                    ┌──────────────────┐
                    │  auth.users      │ (Supabase Auth)
                    │  (id, email)     │
                    └────────┬─────────┘
                             │ references
                             ▼
                    ┌──────────────────┐
                    │ user_profiles(1) │ ← START HERE
                    │ (all user info)  │
                    └────────┬─────────┘
                             │
            ┌────────────────┼────────────────┬──────────────┐
            │                │                │              │
            ▼                ▼                ▼              ▼
    ┌────────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ user_          │ │ user_        │ │ user_        │ │ user_        │
    │ conversations  │ │ eligible_    │ │ applications │ │ documents    │
    │                │ │ schemes      │ │              │ │              │
    └────────┬───────┘ └──────────────┘ └──────────────┘ └──────────────┘
             │
             ▼
    ┌──────────────────────┐
    │ conversation_messages│
    │ (user & bot messages)│
    └──────────────────────┘
```

---

## Quick Reference: What to Query

| Need This | Query This Table | Example |
|-----------|------------------|---------|
| User's name/email | user_profiles | SELECT full_name FROM user_profiles WHERE id = 'user-id' |
| User's income | user_profiles | SELECT annual_income FROM user_profiles WHERE id = 'user-id' |
| All chats | user_conversations | SELECT * FROM user_conversations WHERE user_id = 'user-id' |
| Chat messages | conversation_messages | SELECT * FROM conversation_messages WHERE conversation_id = 'conv-id' |
| Eligible schemes | user_eligible_schemes | SELECT * FROM user_eligible_schemes WHERE user_id = 'user-id' |
| Applications | user_applications | SELECT * FROM user_applications WHERE user_id = 'user-id' |
| Documents | user_documents | SELECT * FROM user_documents WHERE user_id = 'user-id' |

---

## Setup Priority

```
PRIORITY 1 (Essential):
☐ user_profiles - Core user data
☐ auth.users - Authentication (auto-created)

PRIORITY 2 (Conversations):
☐ user_conversations - Chat sessions
☐ conversation_messages - Messages

PRIORITY 3 (Schemes):
☐ user_eligible_schemes - Eligibility tracking
☐ user_applications - Application tracking

PRIORITY 4 (Optional but useful):
☐ user_documents - Document storage
```

---

## Data Storage Size Estimates

```
Per User Estimates:
- user_profiles row: ~500 bytes
- 1 conversation: ~300 bytes
- 1 message: ~500 bytes (average)
- Per eligible scheme: ~200 bytes
- Per application: ~300 bytes
- 1 document metadata: ~400 bytes

Example: 1 user with:
- 5 conversations
- 50 messages total
- 10 eligible schemes
- 3 applications
- 2 documents
≈ 40 KB total
```

---

## Field Types Reference

```
UUID - Unique identifier (primary key)
VARCHAR - Text field (limited length)
TEXT - Long text field
INTEGER - Whole number
DECIMAL - Number with decimals (for money)
BOOLEAN - True/False
TIMESTAMP - Date and time
```

---

## Security Permissions

```
Each table has Row Level Security (RLS):

user_profiles:
  SELECT: user_id = current_user ✅
  INSERT: user_id = current_user ✅
  UPDATE: user_id = current_user ✅
  
conversation_messages:
  SELECT: user_id = current_user ✅
  INSERT: user_id = current_user ✅
  
All other tables:
  Same pattern - Users can only access their own data
```

---

## Common Queries You'll Use

```sql
-- Get user profile
SELECT * FROM user_profiles WHERE id = 'user-id';

-- Get all conversations
SELECT * FROM user_conversations WHERE user_id = 'user-id';

-- Get messages in a conversation
SELECT * FROM conversation_messages 
WHERE conversation_id = 'conv-id' 
ORDER BY created_at;

-- Get eligible schemes
SELECT * FROM user_eligible_schemes 
WHERE user_id = 'user-id' AND applied = false;

-- Get applications
SELECT * FROM user_applications 
WHERE user_id = 'user-id';

-- Update profile
UPDATE user_profiles 
SET annual_income = 500000 
WHERE id = 'user-id';

-- Create new conversation
INSERT INTO user_conversations 
(id, user_id, domain, language, conversation_name)
VALUES ('uuid', 'user-id', 'Agriculture', 'English', 'Farm Schemes');
```

---

## Indexes (Automatic)

```
Supabase automatically indexes:
- Primary keys (UUID)
- Foreign keys (user_id, conversation_id, etc.)

For performance, these are already optimized.
```

---

## Backup & Recovery

```
Supabase automatically:
✅ Backs up data every day
✅ Keeps 30 days of backups
✅ Can restore to any point in time
✅ 99.99% uptime guarantee
✅ Data replicated across regions
```

---

## Final Checklist

Before using the app:

- [ ] Created 6 tables
- [ ] Applied RLS on all
- [ ] Created policies
- [ ] Added to .env
- [ ] pip install supabase
- [ ] Tested signup
- [ ] Tested conversation save
- [ ] Tested profile update
- [ ] Ready to deploy! 🚀

---

## Visual: Table Size Impact

```
Small usage (< 100 users):
Tables: ~5 MB
Cost: FREE tier (Supabase has generous free tier)

Medium usage (1,000 users):
Tables: ~50 MB
Cost: ~$100/month

Large usage (10,000 users):
Tables: ~500 MB
Cost: ~$500/month
```

---

**All 6 tables are ready in `SUPABASE_COMPLETE_SETUP.md`**
**Just copy, paste, and run SQL! ✅**
