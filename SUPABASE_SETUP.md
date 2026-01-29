# Supabase Setup Guide for SchemeSetu

## Database Schema - Tables You'll Need

### 1. **users** (Auto-created by Supabase Auth)
- Built-in table by Supabase for authentication
- Stores: id, email, created_at, updated_at

### 2. **user_profiles**
**Purpose:** Store personalized user information
```sql
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email VARCHAR UNIQUE,
  full_name VARCHAR,
  phone VARCHAR,
  age INT,
  caste VARCHAR,
  location VARCHAR,
  annual_income DECIMAL,
  family_income DECIMAL,
  occupation VARCHAR,
  education_level VARCHAR,
  business_type VARCHAR,
  farm_size DECIMAL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### 3. **user_conversations**
**Purpose:** Store all chat conversations per user
```sql
CREATE TABLE user_conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  conversation_name VARCHAR DEFAULT 'Untitled Conversation',
  domain VARCHAR NOT NULL,
  language VARCHAR DEFAULT 'English',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### 4. **conversation_messages**
**Purpose:** Store individual messages in conversations
```sql
CREATE TABLE conversation_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL REFERENCES user_conversations(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  role VARCHAR NOT NULL, -- 'user' or 'assistant'
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 5. **user_eligible_schemes**
**Purpose:** Track schemes user is eligible for
```sql
CREATE TABLE user_eligible_schemes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  scheme_name VARCHAR NOT NULL,
  domain VARCHAR NOT NULL,
  eligibility_reason TEXT,
  applied BOOLEAN DEFAULT FALSE,
  application_date TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 6. **user_documents**
**Purpose:** Store uploaded documents for verification
```sql
CREATE TABLE user_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  document_type VARCHAR NOT NULL, -- 'id', 'certificate', etc.
  storage_path VARCHAR NOT NULL, -- Path in Supabase Storage
  verified BOOLEAN DEFAULT FALSE,
  verification_notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 7. **user_applications**
**Purpose:** Track scheme applications
```sql
CREATE TABLE user_applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  scheme_name VARCHAR NOT NULL,
  domain VARCHAR NOT NULL,
  status VARCHAR DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'submitted'
  application_link VARCHAR,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## Supabase Setup Steps

### Step 1: Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Get your credentials:
   - **Project URL**: `https://YOUR_PROJECT_ID.supabase.co`
   - **Anon Key**: Public API key
   - **Service Role Key**: Secret key (keep private)

### Step 2: Add to .env file
```
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_KEY=YOUR_ANON_KEY
```

### Step 3: Create Tables in Supabase SQL Editor
Copy and run each table creation SQL in Supabase dashboard

### Step 4: Enable Storage
1. Go to Storage in Supabase dashboard
2. Create new bucket: `user_documents`
3. Set public access policy if needed

### Step 5: Set Row Level Security (RLS)
Enable RLS on tables and add policies so users can only access their own data

## Features This Enables

✅ **User Authentication** - Login/Signup with email
✅ **User Profiles** - Store personal info (income, location, caste, etc.)
✅ **Conversation History** - Save all chats per user
✅ **Application Tracking** - Track which schemes user applied for
✅ **Document Storage** - Upload and store verification documents
✅ **Personalized Experience** - Customize based on user profile
✅ **Multi-session Support** - Switch between conversations
✅ **Data Analytics** - Track user journey and scheme matching

## Install Required Package
```bash
pip install supabase
```
