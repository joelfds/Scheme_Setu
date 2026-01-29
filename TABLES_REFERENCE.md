# 📊 Database Tables Reference - Quick Summary

## Overview
You need **6 tables** to make SchemeSetu personalized and fully functional:

---

## 1️⃣ **user_profiles** (Core User Data)
**What it stores:** User account information

| Field | Type | Purpose |
|-------|------|---------|
| `id` | UUID | User ID (from Supabase Auth) |
| `email` | String | Email address |
| `full_name` | String | User's name |
| `phone` | String | Contact number |
| `age` | Integer | Age (for eligibility) |
| `caste` | String | Caste (SC/ST/OBC/General) |
| `location` | String | State/City/District |
| `annual_income` | Decimal | Income (for eligibility) |
| `family_income` | Decimal | Family income |
| `occupation` | String | Job type |
| `education_level` | String | Education qualification |
| `business_type` | String | If self-employed |
| `farm_size` | Decimal | If farmer |

**Used for:** Profile editing, personalization, eligibility checks

---

## 2️⃣ **user_conversations** (Chat Sessions)
**What it stores:** Each conversation/chat session

| Field | Type | Purpose |
|-------|------|---------|
| `id` | UUID | Conversation ID |
| `user_id` | UUID | Which user |
| `conversation_name` | String | Title (e.g., "Education - Jan 29") |
| `domain` | String | Category (Agriculture/Education/MSME) |
| `language` | String | Language used |
| `created_at` | Timestamp | When started |
| `updated_at` | Timestamp | Last updated |

**Used for:** Saving chat history, showing "Previous conversations"

---

## 3️⃣ **conversation_messages** (Chat Messages)
**What it stores:** Individual messages in conversations

| Field | Type | Purpose |
|-------|------|---------|
| `id` | UUID | Message ID |
| `conversation_id` | UUID | Which conversation |
| `user_id` | UUID | Which user |
| `role` | String | "user" or "assistant" |
| `content` | Text | The actual message |
| `created_at` | Timestamp | When sent |

**Used for:** Loading chat history, replaying conversations

---

## 4️⃣ **user_eligible_schemes** (Matched Schemes)
**What it stores:** Schemes user is eligible for

| Field | Type | Purpose |
|-------|------|---------|
| `id` | UUID | Record ID |
| `user_id` | UUID | Which user |
| `scheme_name` | String | Scheme name |
| `domain` | String | Category |
| `eligibility_reason` | Text | Why eligible |
| `applied` | Boolean | Application status |
| `application_date` | Timestamp | When applied |
| `created_at` | Timestamp | When found eligible |

**Used for:** Showing "Your Eligible Schemes", tracking which ones they applied for

---

## 5️⃣ **user_applications** (Application Tracking)
**What it stores:** Scheme applications submitted

| Field | Type | Purpose |
|-------|------|---------|
| `id` | UUID | Application ID |
| `user_id` | UUID | Which user |
| `scheme_name` | String | Scheme name |
| `domain` | String | Category |
| `status` | String | pending/submitted/approved/rejected |
| `application_link` | String | URL to application |
| `notes` | Text | Any notes/feedback |
| `created_at` | Timestamp | Application date |
| `updated_at` | Timestamp | Last update |

**Used for:** Application dashboard, tracking status

---

## 6️⃣ **user_documents** (Document Management)
**What it stores:** Uploaded verification documents

| Field | Type | Purpose |
|-------|------|---------|
| `id` | UUID | Document ID |
| `user_id` | UUID | Which user |
| `document_type` | String | ID/Certificate/License etc. |
| `storage_path` | String | Path in Supabase Storage |
| `verified` | Boolean | Admin verified |
| `verification_notes` | Text | Admin notes |
| `created_at` | Timestamp | Upload date |

**Used for:** Storing documents, document verification

---

## 🔄 How They Connect

```
user_profiles (1)
    ├── (1-to-many) → user_conversations
    │                     ├── (1-to-many) → conversation_messages
    │                     └── (links to) SCHEME_DB (local JSON)
    ├── (1-to-many) → user_eligible_schemes
    ├── (1-to-many) → user_applications
    └── (1-to-many) → user_documents
```

---

## 💡 Usage Examples

### Example 1: User Signup
```
1. Supabase Auth creates user record with email
2. app inserts row in user_profiles with basic info
3. User later edits profile → profile updated
```

### Example 2: Chat Conversation
```
1. User clicks "New Conversation" → create user_conversations row
2. User sends message → insert into conversation_messages (role=user)
3. Bot responds → insert into conversation_messages (role=assistant)
4. User later opens "Previous conversations" → loads from user_conversations
```

### Example 3: Scheme Matching
```
1. Bot finds user eligible → insert user_eligible_schemes
2. User wants to apply → update user_eligible_schemes (applied=true)
3. Track status → user_applications (status=pending/submitted/approved)
```

### Example 4: Document Upload
```
1. User uploads ID document
2. Insert user_documents (not verified yet)
3. Admin verifies → update verified=true
4. Use for eligibility checks
```

---

## 🔐 Security (Row Level Security)

Each table has RLS policies:
```
✅ Users can only see their OWN data
✅ Users can only update their OWN records
❌ Users cannot see other users' data
❌ Admin operations controlled separately
```

---

## 📌 Quick Checklist

Before running the app:

- [ ] Supabase project created
- [ ] SUPABASE_URL in .env
- [ ] SUPABASE_KEY in .env
- [ ] All 6 tables created
- [ ] RLS enabled on all tables
- [ ] RLS policies applied
- [ ] Storage bucket created
- [ ] `pip install supabase`
- [ ] Running `app_supabase.py`

---

**Once set up, users will have:**
- ✅ Personalized profiles
- ✅ Login/signup
- ✅ Chat history saved
- ✅ Scheme recommendations tracked
- ✅ Application history
- ✅ Document management

🎉 Full personalized experience!
