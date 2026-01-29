# 🏗️ SchemeSetu Supabase Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     SCHEMESETU APP                          │
│                   (Streamlit Frontend)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  AUTHENTICATION LAYER                       │
│  (Supabase Auth - Email/Password, Session Management)      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   SUPABASE CLIENT                           │
│    (Python SDK - Handles API calls to Supabase)            │
└──────┬──────────────┬──────────────┬───────────────────────┘
       │              │              │
       ▼              ▼              ▼
    ┌──────┐    ┌──────────┐   ┌────────────┐
    │ Auth │    │ Database │   │  Storage   │
    └──────┘    └──────────┘   └────────────┘
```

---

## Data Flow Diagram

### User Registration & Login
```
User Input (Email/Password)
        ↓
   Supabase Auth
        ↓
Create User Record
        ↓
Insert user_profiles row
        ↓
Set Session Token
        ↓
Redirect to Main App ✅
```

### Conversation & Chat
```
User types message
        ↓
Insert conversation_messages (role=user)
        ↓
Call Gemini API (LLM)
        ↓
Get response
        ↓
Insert conversation_messages (role=assistant)
        ↓
Save to Supabase
        ↓
Display in UI ✅
```

### Scheme Matching
```
User answers questions
        ↓
Bot analyzes answers
        ↓
Check eligibility against user_profiles
        ↓
Match with SCHEME_DB (local JSON)
        ↓
Insert user_eligible_schemes
        ↓
Display "You're Eligible! 🎉"
        ↓
User clicks "Apply"
        ↓
Insert user_applications (status=pending)
        ↓
Track in Dashboard ✅
```

### Document Upload
```
User uploads document
        ↓
Supabase Storage saves file
        ↓
Insert user_documents (verified=false)
        ↓
Admin reviews
        ↓
Update verified=true
        ↓
Use for eligibility ✅
```

---

## Database Schema Diagram

```
┌────────────────────────┐
│   auth.users           │ ← Supabase Auth
│  (id, email)           │
└────────────┬───────────┘
             │
             │ (references id)
             ▼
┌────────────────────────────────┐
│   user_profiles (1)            │ ← User details
│   id, email, full_name         │
│   age, income, location, etc.  │
└────────────┬────────────────────┘
             │
    ┌────────┴────────┬──────────┬──────────┐
    │                 │          │          │
    ▼                 ▼          ▼          ▼
┌──────────────┐ ┌──────────────┐ ┌───────────────┐ ┌──────────────┐
│ user_        │ │ user_        │ │ user_         │ │ user_        │
│conversations │ │ eligible_    │ │ applications  │ │ documents    │
│              │ │ schemes      │ │               │ │              │
│ id           │ │ id           │ │ id            │ │ id           │
│ domain       │ │ scheme_name  │ │ scheme_name   │ │ document_    │
│ language     │ │ eligibility_ │ │ status        │ │ type         │
│              │ │ reason       │ │ notes         │ │ storage_path │
└────────┬─────┘ └──────────────┘ └───────────────┘ └──────────────┘
         │
         │ (references)
         ▼
┌──────────────────────┐
│ conversation_        │
│ messages             │
│                      │
│ id                   │
│ conversation_id      │
│ role (user/assist.)  │
│ content              │
└──────────────────────┘
```

---

## Table Relationships (ER Diagram)

```
user_profiles (PK: id)
    ├─ 1:N → user_conversations (FK: user_id)
    │           ├─ 1:N → conversation_messages (FK: conversation_id)
    │           └─ Stores: domain, language, created_at
    │
    ├─ 1:N → user_eligible_schemes (FK: user_id)
    │           └─ Stores: scheme_name, eligibility_reason, applied
    │
    ├─ 1:N → user_applications (FK: user_id)
    │           └─ Stores: scheme_name, status, application_link
    │
    └─ 1:N → user_documents (FK: user_id)
                └─ Stores: document_type, storage_path, verified
```

---

## Security Architecture

```
┌─────────────────────────────────────┐
│   User Authentication               │
│  Email + Password → Supabase Auth   │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│    JWT Session Token                │
│  (Valid only for this user)         │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Row Level Security (RLS)           │
│  Each user can only access:         │
│  - Their own profiles               │
│  - Their own conversations          │
│  - Their own messages               │
│  - Their own eligible schemes       │
│  - Their own applications           │
│  - Their own documents              │
└─────────────────────────────────────┘
```

---

## API Flow (Frontend → Supabase)

```
Streamlit Frontend
        ↓
  ┌─────────────────────┐
  │ Supabase Python SDK │
  └─────────┬───────────┘
            │
    ┌───────┴────────────┬──────────────┬──────────────┐
    │                    │              │              │
    ▼                    ▼              ▼              ▼
  POST                 POST              GET          PUT
  /auth                /rest/v1/       /rest/v1/   /rest/v1/
  /sign                (INSERT)        (SELECT)    (UPDATE)
  
User Signs Up       Insert Profile   Query Chats   Update Profile
    ↓                    ↓              ↓              ↓
Verify Email        User Created   Load History   Profile Updated
    ↓                    ↓              ↓              ↓
Session Token     Save Success    Display Chat   Show "Saved" ✅
```

---

## Data Storage Locations

```
├── Supabase PostgreSQL Database (Remote)
│   ├── user_profiles
│   ├── user_conversations
│   ├── conversation_messages
│   ├── user_eligible_schemes
│   ├── user_applications
│   └── user_documents (metadata only)
│
├── Supabase Storage (Remote)
│   └── user_documents/ (actual files)
│       ├── user1/
│       │   ├── aadhar.pdf
│       │   └── certificate.jpg
│       ├── user2/
│       │   └── license.jpg
│       └── ...
│
├── Streamlit Session (Local Memory)
│   ├── st.session_state.user (current user)
│   ├── st.session_state.messages (chat history - backup)
│   └── st.session_state.current_conversation
│
└── Schemes Database (Local)
    └── schemes.json (uploaded schemes)
```

---

## User Journey with Data

```
STEP 1: Signup
┌─────────────┐
│  User Signup│  → Supabase Auth creates user
│  Email/Pass │  → app_supabase.py inserts user_profiles row
└──────┬──────┘  → Show Main App
       │
       ▼
STEP 2: Edit Profile
┌──────────────┐
│Edit Profile  │  → User fills: income, age, location, caste
│Form          │  → UPDATE user_profiles with details
└──────┬───────┘  → Show "Profile Saved ✅"
       │
       ▼
STEP 3: Start Conversation
┌──────────────────┐
│Click "New Conv." │  → INSERT user_conversations
│or Quick Button   │  → Set domain, language
└──────┬───────────┘  → Ready for chat
       │
       ▼
STEP 4: Chat & Ask Schemes
┌──────────────────┐
│ Type message     │  → INSERT conversation_messages (role=user)
│                  │  → Call Gemini API
│ Get response     │  → INSERT conversation_messages (role=assistant)
└──────┬───────────┘  → Display in chat
       │
       ▼
STEP 5: Check Eligibility
┌──────────────────┐
│ Bot matches      │  → Use user_profiles data
│ schemes          │  → Match against schemes.json
│ "You're eligible"│  → INSERT user_eligible_schemes
└──────┬───────────┘  → Show "Apply Now 🎉"
       │
       ▼
STEP 6: Apply
┌──────────────────┐
│ Click "Apply"    │  → INSERT user_applications (status=pending)
│ Share link       │  → UPDATE user_eligible_schemes (applied=true)
└──────┬───────────┘  → Show "Application Submitted ✅"
       │
       ▼
STEP 7: Track Progress
┌──────────────────┐
│ Dashboard shows: │  → SELECT user_eligible_schemes
│ - Eligible ones  │  → SELECT user_applications
│ - Applied ones   │  → Filter by status
│ - Status updates │  → Display timeline
└──────────────────┘
```

---

## Key Features by Table

| Feature | Tables Used |
|---------|-------------|
| Login/Signup | auth.users |
| Profile Management | user_profiles |
| Chat History | user_conversations, conversation_messages |
| Scheme Recommendations | user_profiles, (matches with schemes.json) |
| Eligibility Tracking | user_eligible_schemes |
| Application Management | user_applications |
| Document Verification | user_documents, Supabase Storage |
| Multi-conversation | user_conversations, conversation_messages |
| Personalization | user_profiles (all other tables depend on this) |

---

## Performance Optimization

```
Indexing (automatic on FK):
- user_conversations.user_id
- conversation_messages.conversation_id
- user_eligible_schemes.user_id
- user_applications.user_id
- user_documents.user_id

RLS Policies (automatic filtering):
- Users only see their own data
- No cross-user data leakage
- Reduced data transfer
```

---

## Deployment Checklist

- [ ] Supabase project created
- [ ] All 6 tables created with correct schema
- [ ] RLS enabled on all tables
- [ ] RLS policies created and tested
- [ ] Storage bucket created
- [ ] .env configured with SUPABASE_URL and KEY
- [ ] `pip install supabase`
- [ ] Test signup/login flow
- [ ] Test conversation saving
- [ ] Test scheme matching
- [ ] Test document upload (if implemented)

---

**This architecture ensures:**
✅ Scalability - Can handle millions of users
✅ Security - Data isolation per user
✅ Reliability - Cloud-based infrastructure
✅ Personalization - Full user data tracking
✅ Performance - Optimized queries and indexing
