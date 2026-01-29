# 🚀 Quick Start - Supabase Integration for SchemeSetu

## In 5 Minutes ⏱️

### 1. Create Supabase Project (2 min)
```
1. Go to supabase.com
2. Click "Start your project"
3. Sign in with GitHub
4. Create project: "scheme-setu"
5. Wait for deployment
```

### 2. Get Credentials (1 min)
```
Settings → API
Copy:
- Project URL: https://YOUR_PROJECT_ID.supabase.co
- Anon Key: paste in .env
```

### 3. Create Tables (1 min)
- Go to SQL Editor in Supabase
- Copy-paste SQL from `SUPABASE_COMPLETE_SETUP.md`
- Run each query
- All tables created ✅

### 4. Update .env (1 min)
```
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_KEY=your_anon_key_here
GOOGLE_API_KEY=your_existing_key
```

---

## 📊 What Tables You Need

**6 Essential Tables:**

1. **user_profiles** - User account info (name, income, location, caste, etc.)
2. **user_conversations** - Chat sessions (one conversation = one chat thread)
3. **conversation_messages** - Messages in conversations (user & bot)
4. **user_eligible_schemes** - Schemes user is eligible for (with reasons)
5. **user_applications** - Track application status
6. **user_documents** - Store uploaded documents for verification

---

## 🔐 Security Built-In

✅ RLS (Row Level Security) - Each user sees only their data
✅ Authentication - Supabase Auth handles passwords
✅ Encryption - Data encrypted in transit and at rest
✅ No sharing - Users can't see other users' data

---

## 💾 How Data is Saved

| Action | Where It's Saved |
|--------|------------------|
| User signs up | auth.users + user_profiles |
| User edits profile | user_profiles |
| User chats | conversation_messages |
| Scheme found eligible | user_eligible_schemes |
| User applies | user_applications |
| User uploads doc | user_documents + Storage |

---

## ✨ New Features You Get

✅ **Login/Signup** - Personalized for each user
✅ **Profile Page** - Edit income, location, age, caste
✅ **Chat History** - Save conversations, load later
✅ **Multiple Chats** - Create multiple conversations
✅ **Scheme Tracking** - See all eligible schemes
✅ **Application Dashboard** - Track which schemes applied
✅ **Document Upload** - Verify with documents
✅ **Data Persistence** - Everything saved to cloud

---

## 🎯 File Guide

| File | Purpose |
|------|---------|
| `app_supabase.py` | New app with Supabase (ready to use) |
| `SUPABASE_COMPLETE_SETUP.md` | Detailed SQL setup instructions |
| `TABLES_REFERENCE.md` | Database table documentation |
| `ARCHITECTURE.md` | System design & data flow |

---

## 🧪 Test It

```bash
# Install Supabase SDK
pip install supabase

# Run new app
python -m streamlit run app_supabase.py

# Try:
# 1. Sign up with email
# 2. Edit profile (add income, location, etc.)
# 3. Start conversation
# 4. Chat about schemes
# 5. Check conversation history
```

---

## ⚠️ Important

1. **Keep .env file safe** - Never commit to GitHub
2. **Use Anon Key** in frontend (has limited permissions)
3. **Backup credentials** - Store SUPABASE_URL and KEY safely
4. **Enable RLS** - Already included in SQL queries

---

## 🆘 Common Issues

| Problem | Solution |
|---------|----------|
| "SUPABASE_URL not found" | Check .env file in project root |
| "Table doesn't exist" | Run SQL queries in Supabase editor |
| "User already exists" | Use different email or reset |
| "RLS policy violation" | Check RLS policies are created |

---

## 📈 What Happens When?

```
User Action → Database Updated → App Shows Result

Sign up → user_profiles created → "Welcome!" page
Edit profile → user_profiles updated → "Saved ✅"
Send message → conversation_messages saved → Shows in chat
Find eligible → user_eligible_schemes saved → "You're eligible! 🎉"
Click apply → user_applications saved → "Applied ✅"
```

---

## 🎓 Learn More

- [Supabase Docs](https://supabase.com/docs)
- [Supabase Python SDK](https://github.com/supabase/supabase-py)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)

---

## ✅ Ready?

1. Create Supabase project
2. Create 6 tables (copy SQL)
3. Add credentials to .env
4. Install: `pip install supabase`
5. Run: `python -m streamlit run app_supabase.py`
6. Sign up and try it!

**That's it! You now have a fully personalized SchemeSetu! 🎉**

---

## 🔄 Next Steps (Optional)

- Add profile picture upload
- Send verification emails on signup
- Create admin dashboard for analytics
- Add scheme comparison feature
- Send notifications on application updates

Good luck! 🚀
