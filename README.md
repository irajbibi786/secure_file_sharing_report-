# Secure File Sharing System

A secure file-sharing portal built for **Task 4** of the Internee.pk Cybersecurity Internship. Ensures encrypted, time-limited file exchanges between Internee.pk and external parties using AWS S3 and Flask.

## Features

- 🔒 **AES-256 encryption at rest** — every file is encrypted automatically via S3 server-side encryption (SSE-S3)
- 🔗 **Signed URLs for upload & download** — files are never public; every transfer uses a unique, time-limited presigned URL (5-minute expiry)
- 🔐 **HTTPS encryption in transit** — all uploads/downloads happen over secure connections
- 👤 **Least-privilege IAM access** — the app's credentials can only `PutObject`, `GetObject`, and `ListBucket` on a single, dedicated bucket
- ⚡ **Direct browser-to-S3 upload** — files go straight from the browser to S3 via a presigned URL, without passing through the server

## Architecture

```
Browser  --(1) request upload URL-->  Flask backend
Browser  <--(2) presigned PUT URL---  Flask backend
Browser  --(3) PUT file directly-->   AWS S3 (encrypted, AES-256)

Browser  --(1) click Download------>  Flask backend
Browser  <--(2) redirect to signed GET URL--  Flask backend
Browser  --(3) fetch file directly-->  AWS S3
```

## Tech Stack

- **Backend:** Python, Flask, boto3
- **Frontend:** HTML, JavaScript (Fetch API)
- **Cloud:** AWS S3 (encrypted storage, presigned URLs), IAM (least-privilege access)

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd secure-fileshare
pip install -r requirements.txt
```

### 2. Configure AWS credentials

Copy `.env.example` to `.env` and fill in your own values:

```bash
cp .env.example .env
```

```
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=ap-southeast-2
S3_BUCKET_NAME=your-bucket-name
FLASK_SECRET_KEY=generate-a-random-string
```

**Never commit your `.env` file** — it's already excluded via `.gitignore`.

### 3. AWS setup required before running

- Create an S3 bucket with public access blocked and default encryption (SSE-S3 / AES-256) enabled.
- Create an IAM user with a policy limited to `s3:PutObject`, `s3:GetObject`, and `s3:ListBucket` on that bucket only.
- Add a CORS configuration on the bucket allowing `PUT`/`GET` from your app's origin, e.g.:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["PUT", "GET"],
    "AllowedOrigins": ["http://127.0.0.1:5000"],
    "ExposeHeaders": []
  }
]
```

### 4. Run the app

```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.

## Project Structure

```
secure-fileshare/
├── app.py                  # Flask backend (routes + presigned URL logic)
├── templates/
│   └── index.html          # Upload/download UI
├── requirements.txt        # Python dependencies
├── .env.example             # Environment variable template
└── .gitignore
```

## Security Notes

- Signed URLs expire after 5 minutes — regenerate a new one if a link goes stale.
- The IAM user used by this app should never be granted broader permissions than `PutObject`/`GetObject`/`ListBucket` on its dedicated bucket.
- Rotate AWS access keys immediately if they are ever exposed (e.g., committed to git, shared in a screenshot, or logged).

## Author

 Zunaira Shahzad — Cybersecurity Intern, Internee.pk
