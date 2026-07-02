# Push SnapFlow to GitHub - Step by Step

## ✅ You've created the repository! Now follow these steps:

### Step 1: Get Your Repository URL

After creating your repository on GitHub, you should see a URL like:
```
https://github.com/YOUR_USERNAME/snapflow.git
```

Copy this URL - you'll need it in Step 3.

### Step 2: Open PowerShell in the SnapFlow Directory

1. Open File Explorer
2. Navigate to: `C:\Users\USER\OneDrive\Music\st 1\snapflow`
3. In the address bar, type `powershell` and press Enter

### Step 3: Run These Commands

Copy and paste these commands one by one:

```powershell
# 1. Initialize git repository
git init

# 2. Add all files
git add .

# 3. Commit the files
git commit -m "Initial commit: SnapFlow v1.0.0 - Lightning-fast database snapshot manager"

# 4. Rename branch to main
git branch -M main

# 5. Add your GitHub repository (REPLACE WITH YOUR URL!)
git remote add origin https://github.com/YOUR_USERNAME/snapflow.git

# 6. Push to GitHub
git push -u origin main
```

**IMPORTANT**: In step 5, replace `YOUR_USERNAME` with your actual GitHub username!

### Step 4: Authenticate

When you run `git push`, GitHub will ask you to authenticate:

**Option A: GitHub Desktop (Easiest)**
- Install GitHub Desktop: https://desktop.github.com/
- Sign in with your GitHub account
- Then run the commands above

**Option B: Personal Access Token**
- Username: Your GitHub username
- Password: Use a Personal Access Token (NOT your GitHub password)
- Create token at: https://github.com/settings/tokens
  - Click "Generate new token (classic)"
  - Select scopes: `repo` (full control)
  - Copy the token and use it as password

**Option C: GitHub CLI**
```powershell
# Install GitHub CLI first: https://cli.github.com/
gh auth login
```

### Troubleshooting

**Error: "git is not recognized"**
- Install Git: https://git-scm.com/download/win
- Restart PowerShell after installation

**Error: "Authentication failed"**
- Use a Personal Access Token instead of password
- Create at: https://github.com/settings/tokens

**Error: "remote origin already exists"**
```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/snapflow.git
git push -u origin main
```

### Verify Success

After pushing, visit:
```
https://github.com/YOUR_USERNAME/snapflow
```

You should see all your files there! 🎉
