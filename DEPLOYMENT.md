# Deployment Guide for Render

This guide will walk you through deploying your Incident Tracker application to Render.

## Prerequisites

1. A GitHub account
2. Your code pushed to a GitHub repository
3. A Render account (sign up at https://render.com - free tier available)

## Step-by-Step Deployment

### Step 1: Push Your Code to GitHub

If you haven't already, push your code to GitHub:

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Create a PostgreSQL Database on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `incident-tracker-db` (or your choice)
   - **Database**: `incident_tracker` (or your choice)
   - **User**: Leave default or customize
   - **Region**: Choose closest to you
   - **PostgreSQL Version**: 15 or 16 (recommended)
   - **Plan**: Free (for testing/development)
4. Click **"Create Database"**
5. **Important**: Copy the **Internal Database URL** - you'll need this later
   - **⚠️ SECURITY WARNING**: Never commit database URLs or passwords to Git!

### Step 3: Create the Web Service

1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub account if not already connected
3. Select your repository: `incident_tracker` (or your repo name)
4. Configure the service:

   **Basic Settings:**
   - **Name**: `incident-tracker` (or your choice)
   - **Environment**: `Python 3`
   - **Region**: Same as your database
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty (or `.` if needed)

   **Build & Deploy:**
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && flask db upgrade
     ```
   - **Start Command**: 
     ```bash
     gunicorn wsgi:app
     ```

   **Advanced Settings (optional):**
   - **Auto-Deploy**: `Yes` (deploys on every push to main)

### Step 4: Configure Environment Variables

In your Web Service settings, go to **"Environment"** tab and add:

1. **SECRET_KEY**
   - Generate a secure key:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
   - Copy the output and paste as the value

2. **FLASK_ENV**: `production`

3. **DATABASE_URL**: 
   - Go to your PostgreSQL database dashboard
   - Copy the **Internal Database URL**
   - Paste it here
   - **Note**: Render automatically converts `postgres://` to `postgresql://` in our config

4. **MAIL_SERVER** (optional): `smtp.gmail.com`
   - Only if you want email notifications to work

5. **MAIL_PORT** (optional): `587`

6. **MAIL_USE_TLS** (optional): `True`

7. **MAIL_USERNAME** (optional): Your Gmail address
   - Only if using Gmail for emails

8. **MAIL_PASSWORD** (optional): Your Gmail App Password
   - **Important**: Use an App Password, not your regular Gmail password
   - Generate at: https://myaccount.google.com/apppasswords

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will start building your application
3. Watch the build logs - it should:
   - Install dependencies
   - Run database migrations
   - Start the web service

### Step 6: Seed Your Database (Optional)

After deployment, you may want to seed the database with sample data:

1. Go to your Web Service dashboard
2. Click **"Shell"** tab
3. Run:
   ```bash
   python seed.py
   ```
   - **Note**: You may need to update `seed.py` to use the production database

### Step 7: Access Your Application

Once deployed, your app will be available at:
```
https://incident-tracker.onrender.com
```
(Your URL will be different based on your service name)

## Troubleshooting

### Build Fails

**Issue**: Build command fails
- Check the build logs for specific errors
- Ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility

**Issue**: Database connection fails
- Verify `DATABASE_URL` is set correctly
- Check that the database is in the same region as your web service
- Ensure you're using the **Internal Database URL** (not External)

### Application Won't Start

**Issue**: Application crashes on startup
- Check the logs in Render dashboard
- Verify `SECRET_KEY` is set
- Ensure `DATABASE_URL` is correct
- Check that migrations ran successfully

**Issue**: 502 Bad Gateway
- Application might be starting slowly
- Check if gunicorn is running: Look for "Listening at: http://0.0.0.0:XXXX"
- Free tier services "spin down" after 15 minutes of inactivity - first request will be slow

### Database Issues

**Issue**: Tables don't exist
- Run migrations manually in Shell:
  ```bash
  flask db upgrade
  ```

**Issue**: Can't connect to database
- Verify `DATABASE_URL` environment variable
- Check database is running (green status in dashboard)
- Ensure web service and database are in same region

### Email Not Working

- Verify all `MAIL_*` environment variables are set
- For Gmail, use App Password (not regular password)
- Check Render logs for email errors

## Free Tier Limitations

- **Spinning Down**: Free services spin down after 15 minutes of inactivity
- **Build Time**: Limited build minutes per month
- **Database**: Free PostgreSQL has 90-day data retention limit
- **Bandwidth**: Limited bandwidth

## Upgrading to Paid Tier

If you need:
- Always-on services (no spin-down)
- More resources
- Better performance
- Production-grade reliability

Consider upgrading to a paid plan.

## Security Notes

- ✅ Never commit `SECRET_KEY` to Git
- ✅ Use environment variables for all secrets
- ✅ Enable HTTPS (automatic on Render)
- ✅ Keep dependencies updated
- ✅ Use strong passwords for database

## Next Steps

After deployment:
1. Test all functionality
2. Create an admin user
3. Seed sample data if needed
4. Configure custom domain (optional, paid feature)
5. Set up monitoring (optional)

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- Your app logs: Available in Render dashboard

