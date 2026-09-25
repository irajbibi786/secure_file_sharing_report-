import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

AWS_REGION = os.environ["AWS_REGION"]
BUCKET_NAME = os.environ["S3_BUCKET_NAME"]

# endpoint_url is set explicitly (instead of relying on auto-detection) to avoid
# 307 Temporary Redirect responses that can happen right after a bucket is
# created in a non-us-east-1 region.
s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    endpoint_url=f"https://s3.{AWS_REGION}.amazonaws.com",
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    config=Config(signature_version="s3v4", s3={"addressing_style": "virtual"}),
)

# Signed URLs expire after 5 minutes for security
URL_EXPIRATION_SECONDS = 300


@app.route("/")
def index():
    """Show upload form and list of files currently in the bucket."""
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        files = [obj["Key"] for obj in response.get("Contents", [])]
    except ClientError as e:
        flash(f"Could not list files: {e}")
        files = []
    return render_template("index.html", files=files)


@app.route("/generate-upload-url")
def generate_upload_url():
    """
    Returns a presigned PUT URL the browser can upload directly to.
    The ServerSideEncryption param forces S3 to AES-256 encrypt the file
    at rest, and the browser must send a matching header (see index.html).
    """
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"error": "filename is required"}), 400

    try:
        url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": filename,
                "ServerSideEncryption": "AES256",
            },
            ExpiresIn=URL_EXPIRATION_SECONDS,
        )
        return jsonify({"url": url})
    except ClientError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download/<path:filename>")
def download(filename):
    """Redirects the user to a time-limited presigned GET URL for the file."""
    try:
        signed_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": filename},
            ExpiresIn=URL_EXPIRATION_SECONDS,
        )
        return redirect(signed_url)
    except ClientError as e:
        flash(f"Could not generate download link: {e}")
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
