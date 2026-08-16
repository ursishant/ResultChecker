# UGC NET Answer Checker

A production-ready web application for analyzing UGC NET response sheets against official answer keys, and checking official result statuses.

## Features

- **Answer Analysis**: Upload your response sheet and official answer key to get a detailed question-wise analysis (Correct, Incorrect, Unattempted, Missing, Estimated Score).
- **Format Agnostic**: Detects and processes NTA/DigiALM format dynamically mapping chosen options to actual Option IDs.
- **Official Result Status**: Search and view the official result declared status of 87+ UGC NET courses.
- **Privacy First**: Files are processed in memory and deleted immediately. No personal data is stored.
- **Export**: Download your analysis in CSV and multi-sheet Excel formats.

## Local Development Setup

### 1. Install Dependencies

Ensure you have Python 3.9+ installed.

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`.

## Deployment Guide (Render)

This project is configured to be deployed effortlessly on [Render](https://render.com).

### Step 1
Create a GitHub account if you don't have one, and create a new repository (e.g., `ugc-net-answer-checker`).

### Step 2
Upload all project files to the `main` branch of your new repository.

### Step 3
Log in to Render and click **New → Web Service**.

### Step 4
Connect your GitHub account and select your `ugc-net-answer-checker` repository.

### Step 5
Configure the Web Service with the following settings:
- **Runtime**: `Python`
- **Branch**: `main`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT`
- **Plan**: Free (or as preferred)

### Step 6
Click **Deploy**. Render will automatically build and deploy your application.

### Custom Domain
Once deployed, you can connect a custom domain (e.g., `answerchecker.example.com`) by going to your Web Service settings in Render, scrolling down to **Custom Domains**, and following the DNS setup instructions provided.

## Data Privacy

Your uploaded PDFs are processed temporarily to generate your analysis. They are not permanently stored on the server. The calculated score is an estimate and does not replace the official NTA result.
