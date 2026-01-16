import boto3
from botocore.exceptions import ClientError
from pathlib import Path
import logging
from typing import Optional
from config import settings

from botocore.config import Config as BotoConfig

logger = logging.getLogger(__name__)


class S3StorageService:
    """Service for uploading and managing videos in AWS S3."""
    
    def __init__(self):
        self.enabled = settings.STORAGE_MODE == "s3"
        
        if self.enabled:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
                config=BotoConfig(signature_version='s3v4')
            )
            self.bucket_name = settings.AWS_S3_BUCKET
            self.cloudfront_domain = settings.AWS_CLOUDFRONT_DOMAIN
            logger.info(f"S3 Storage initialized: bucket={self.bucket_name}, region={settings.AWS_REGION}")
        else:
            logger.info("Using local storage (S3 disabled)")
    
    def upload_video(self, local_path: Path, s3_key: str) -> Optional[str]:
        """
        Upload video to S3 and return the URL.
        
        Args:
            local_path: Path to local video file
            s3_key: S3 object key (path in bucket)
            
        Returns:
            Public URL of the uploaded video (or None if local storage)
        """
        if not self.enabled:
            # Return local URL
            return f"/videos/{local_path.name}"
        
        try:
            # Upload to S3
            self.s3_client.upload_file(
                str(local_path),
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': 'video/mp4',
                    'CacheControl': 'max-age=31536000',  # 1 year cache
                }
            )
            
            # Generate URL
            if self.cloudfront_domain:
                # Use CloudFront CDN URL (faster delivery)
                url = f"https://{self.cloudfront_domain}/{s3_key}"
            else:
                # Use Presigned URL for private buckets (Bucket Owner Enforced)
                url = self.generate_presigned_url(s3_key, expiration=604800) # 7 days validity
            
            logger.info(f"Video uploaded to S3: {s3_key}")
            
            # Optionally delete local file to save space
            local_path.unlink()
            
            return url
            
        except ClientError as e:
            logger.error(f"Failed to upload to S3: {str(e)}")
            raise Exception(f"S3 upload failed: {str(e)}")
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        """
        Generate a presigned URL for private video access.
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Presigned URL
        """
        if not self.enabled:
            return f"/videos/{s3_key}"
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            raise
    
    def delete_video(self, s3_key: str) -> bool:
        """
        Delete video from S3.
        
        Args:
            s3_key: S3 object key
            
        Returns:
            True if deleted successfully
        """
        if not self.enabled:
            # Delete local file
            local_path = settings.VIDEOS_DIR / s3_key
            if local_path.exists():
                local_path.unlink()
            return True
        
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.info(f"Video deleted from S3: {s3_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete from S3: {str(e)}")
            return False
    
    def list_videos(self, prefix: str = "", max_keys: int = 100) -> list[dict]:
        """
        List videos in S3 bucket.
        
        Args:
            prefix: Filter by key prefix
            max_keys: Maximum number of results
            
        Returns:
            List of video objects
        """
        if not self.enabled:
            return []
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            return response.get('Contents', [])
        except ClientError as e:
            logger.error(f"Failed to list S3 objects: {str(e)}")
            return []


# Global instance
s3_service = S3StorageService()