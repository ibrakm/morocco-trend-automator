#!/usr/bin/env python3
"""
LinkedIn API Service for Publishing Posts
"""

import requests
import json
from typing import Dict, Optional
from config import Config

class LinkedInService:
    """Service for publishing content to LinkedIn"""
    
    def __init__(self):
        self.api_url = Config.LINKEDIN_API_URL
        self.access_token = Config.get_linkedin_token()
        self.person_urn = Config.get_linkedin_urn()
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
    
    def upload_image(self, image_bytes: bytes) -> Optional[str]:
        """
        Upload image to LinkedIn and return asset URN
        """
        try:
            # Step 1: Register upload
            register_url = f"{self.api_url}/assets?action=registerUpload"
            register_payload = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": self.person_urn,
                    "serviceRelationships": [{
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }]
                }
            }
            
            response = requests.post(register_url, headers=self.headers, json=register_payload)
            response.raise_for_status()
            
            register_data = response.json()
            upload_url = register_data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            asset_urn = register_data['value']['asset']
            
            # Step 2: Upload image binary
            upload_headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            upload_response = requests.put(upload_url, headers=upload_headers, data=image_bytes)
            upload_response.raise_for_status()
            
            print(f"✅ Image uploaded: {asset_urn}")
            return asset_urn
            
        except Exception as e:
            print(f"❌ Image Upload Error: {e}")
            return None
    
    def create_post(self, text: str, image_asset_urn: Optional[str] = None) -> Optional[str]:
        """
        Create a LinkedIn post (UGC Post)
        Returns post URN if successful
        """
        try:
            post_url = f"{self.api_url}/ugcPosts"
            
            # Build post payload
            post_payload = {
                "author": self.person_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Add image if provided
            if image_asset_urn:
                post_payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                post_payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                    "status": "READY",
                    "media": image_asset_urn
                }]
            
            response = requests.post(post_url, headers=self.headers, json=post_payload)
            response.raise_for_status()
            
            post_data = response.json()
            post_id = post_data.get('id', 'Unknown')
            
            print(f"✅ Post published: {post_id}")
            return post_id
            
        except Exception as e:
            print(f"❌ Post Creation Error: {e}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text}")
            return None
    
    def publish_post_with_image(self, text: str, image_bytes: bytes) -> Dict:
        """
        Complete workflow: Upload image and create post
        Returns: {success: bool, post_id: str, message: str}
        """
        result = {
            "success": False,
            "post_id": None,
            "message": ""
        }
        
        try:
            # Upload image
            print("📤 Uploading image to LinkedIn...")
            asset_urn = self.upload_image(image_bytes)
            
            if not asset_urn:
                result["message"] = "Failed to upload image"
                return result
            
            # Create post
            print("📝 Creating LinkedIn post...")
            post_id = self.create_post(text, asset_urn)
            
            if not post_id:
                result["message"] = "Failed to create post"
                return result
            
            result["success"] = True
            result["post_id"] = post_id
            result["message"] = "Post published successfully!"
            
            return result
            
        except Exception as e:
            result["message"] = f"Error: {str(e)}"
            return result
    
    def publish_text_only_post(self, text: str) -> Dict:
        """
        Publish text-only post
        Returns: {success: bool, post_id: str, message: str}
        """
        result = {
            "success": False,
            "post_id": None,
            "message": ""
        }
        
        try:
            print("📝 Creating text-only LinkedIn post...")
            post_id = self.create_post(text)
            
            if not post_id:
                result["message"] = "Failed to create post"
                return result
            
            result["success"] = True
            result["post_id"] = post_id
            result["message"] = "Post published successfully!"
            
            return result
            
        except Exception as e:
            result["message"] = f"Error: {str(e)}"
            return result
    
    def get_profile_info(self) -> Optional[Dict]:
        """
        Get basic profile information
        """
        try:
            # Extract person ID from URN
            person_id = self.person_urn.split(':')[-1]
            profile_url = f"{self.api_url}/people/{person_id}"
            
            response = requests.get(profile_url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"❌ Profile Info Error: {e}")
            return None
    
    def format_linkedin_text(self, content: Dict) -> str:
        """
        Format content dictionary into LinkedIn post text
        """
        text = content.get('post_text', '')
        
        # Add hashtags at the end
        hashtags = content.get('hashtags', [])
        if hashtags:
            text += "\n\n" + " ".join([f"#{tag}" for tag in hashtags])
        
        return text

if __name__ == "__main__":
    # Test the service
    print("🧪 Testing LinkedIn Service...\n")
    service = LinkedInService()
    
    print("👤 Fetching profile info...")
    profile = service.get_profile_info()
    
    if profile:
        print(f"✅ Connected to LinkedIn profile")
        print(f"Profile URN: {service.person_urn}")
    else:
        print("⚠️  Could not fetch profile (this is normal if API has restrictions)")
    
    print("\n📝 Testing text formatting...")
    test_content = {
        "post_text": "Exciting developments in Morocco's tech sector!",
        "hashtags": ["Morocco", "Technology", "Innovation"]
    }
    
    formatted_text = service.format_linkedin_text(test_content)
    print("\nFormatted LinkedIn Post:")
    print("="*60)
    print(formatted_text)
    print("="*60)
    
    print("\n✅ LinkedIn service initialized and ready!")
    print("⚠️  Note: Actual posting requires valid access token with write permissions")
