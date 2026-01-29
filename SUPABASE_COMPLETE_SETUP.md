# SchemeSetu Supabase Integration - Complete Setup Guide

## 📋 Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up with GitHub or Google
4. Create new project with these details:
   - **Project Name**: `scheme-setu`
   - **Database Password**: Save it securely
   - **Region**: Choose closest to you
5. Wait for deployment (2-3 minutes)

---

## 🔑 Step 2: Get Your Credentials

1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL**: `https://YOUR_PROJECT_ID.supabase.co`
   - **Anon Key** (Public): Use this for frontend
   - **Service Role Key**: KEEP SECRET (only use in backend)

---

## 📊 Step 3: Create Database Tables

Go to **SQL Editor** in Supabase and run these queries:

### Table 1: user_profiles
```sql
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email VARCHAR UNIQUE NOT NULL,
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

ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile" ON user_profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON user_profiles
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON user_profiles
  FOR INSERT WITH CHECK (auth.uid() = id);
```

### Table 2: user_conversations
```sql
CREATE TABLE user_conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  conversation_name VARCHAR DEFAULT 'Untitled',
  domain VARCHAR NOT NULL,
  language VARCHAR DEFAULT 'English',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE user_conversations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own conversations" ON user_conversations
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own conversations" ON user_conversations
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own conversations" ON user_conversations
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own conversations" ON user_conversations
  FOR DELETE USING (auth.uid() = user_id);
```

### Table 3: conversation_messages
```sql
CREATE TABLE conversation_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL REFERENCES user_conversations(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  role VARCHAR NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own messages" ON conversation_messages
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own messages" ON conversation_messages
  FOR INSERT WITH CHECK (auth.uid() = user_id);
```

### Table 4: user_eligible_schemes
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

ALTER TABLE user_eligible_schemes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own schemes" ON user_eligible_schemes
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own schemes" ON user_eligible_schemes
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own schemes" ON user_eligible_schemes
  FOR UPDATE USING (auth.uid() = user_id);
```

### Table 5: user_applications
```sql
CREATE TABLE user_applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  scheme_name VARCHAR NOT NULL,
  domain VARCHAR NOT NULL,
  status VARCHAR DEFAULT 'pending' CHECK (status IN ('pending', 'submitted', 'approved', 'rejected')),
  application_link VARCHAR,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE user_applications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own applications" ON user_applications
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own applications" ON user_applications
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own applications" ON user_applications
  FOR UPDATE USING (auth.uid() = user_id);
```

### Table 6: user_documents
```sql
CREATE TABLE user_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  document_type VARCHAR NOT NULL,
  storage_path VARCHAR NOT NULL,
  verified BOOLEAN DEFAULT FALSE,
  verification_notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE user_documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own documents" ON user_documents
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own documents" ON user_documents
  FOR INSERT WITH CHECK (auth.uid() = user_id);
```

---

## 💾 Step 4: Create Storage Bucket

1. Go to **Storage** in Supabase
2. Click **Create a new bucket**
3. **Bucket name**: `user_documents`
4. **Public bucket**: OFF (keep private for security)
5. Click **Create**

---

## 📝 Step 5: Update .env File

Add these to your `.env` file:

```
GOOGLE_API_KEY=your_google_api_key_here
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_KEY=your_anon_key_here
```

⚠️ **NEVER share these keys publicly!**

---

## 📦 Step 6: Install Required Package

```bash
pip install supabase
```

---

## 🚀 Step 7: Run the App

```bash
# Replace current app.py with app_supabase.py
python -m streamlit run app_supabase.py
```

---

## ✨ Features Now Available

✅ **User Authentication**
- Secure signup/login with email
- Password reset
- Session management

✅ **User Profiles**
- Store personal details (age, income, location, caste, etc.)
- Edit profile anytime
- All data encrypted in Supabase

✅ **Conversation Management**
- Multiple conversations per user
- Load previous conversations
- Clear conversation history

✅ **Personalized Experience**
- Remember user details
- Smart scheme recommendations
- Track eligible schemes
- Application history

✅ **Data Privacy**
- Row-level security (RLS)
- Only users can access their own data
- No sharing between users

---

## 🔒 Security Best Practices

1. **Never commit .env to Git**
   ```
   # Add to .gitignore
   .env
   .env.local
   ```

2. **Use Anon Key in Frontend**
   - The Anon Key has limited permissions
   - RLS policies enforce user-level access control

3. **Service Role Key in Backend Only**
   - Never expose in Streamlit/frontend
   - Only use in server-side operations

4. **Enable RLS on All Tables**
   - Already done in the SQL queries above

---

## 📊 Database Schema Summary

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| **user_profiles** | User account info | id, email, full_name, age, income, location, caste |
| **user_conversations** | Chat sessions | id, user_id, domain, language, created_at |
| **conversation_messages** | Chat messages | id, conversation_id, role, content |
| **user_eligible_schemes** | Matched schemes | id, user_id, scheme_name, eligibility_reason |
| **user_applications** | Application tracking | id, user_id, scheme_name, status |
| **user_documents** | Document storage | id, user_id, document_type, storage_path |

---

## 🆘 Troubleshooting

### Error: "SUPABASE_URL not found"
- Check .env file exists in project root
- Verify variable names match exactly
- Restart Streamlit app

### Error: "User already exists"
- Email already registered
- Use different email or reset password

### Error: "RLS policy violation"
- Check user_id matches auth.uid()
- Verify RLS policies are created
- Enable RLS on tables

### Messages not saving
- Check conversation_messages table RLS
- Verify user_id is correct
- Check Supabase API is accessible

---

## 🎯 Next Steps

1. Set up authentication email verification
2. Add profile completion flow on first signup
3. Implement document upload to storage
4. Add scheme application tracking dashboard
5. Create admin panel for analytics

---

**Need help?** Check [Supabase Docs](https://supabase.com/docs)
