#!/usr/bin/env python3

'''
lsvhbavjzyyjtzcn
'''

import imaplib
import email
import os
import json
from datetime import datetime
from email.header import decode_header
import getpass

class YahooEmailRetriever:
    def __init__(self):
        self.imap_server = "imap.mail.yahoo.com"
        self.imap_port = 993
        self.connection = None
    
    def connect(self, username, password):
        """Connect to Yahoo IMAP server"""
        try:
            self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.connection.login(username, password)
            print("Successfully connected to Yahoo IMAP server")
            return True
        except imaplib.IMAP4.error as e:
            print(f"IMAP Error: {e}")
            return False
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def list_folders(self):
        """List all available folders/mailboxes"""
        if not self.connection:
            print("Not connected to server")
            return []
        
        try:
            status, folders = self.connection.list()
            folder_list = []
            if status == 'OK':
                for folder in folders:
                    folder_name = folder.decode().split('"')[-2]
                    folder_list.append(folder_name)
            return folder_list
        except Exception as e:
            print(f"Error listing folders: {e}")
            return []
    
    def decode_mime_words(self, s):
        """Decode MIME encoded words in headers"""
        if s is None:
            return ""
        
        decoded_parts = []
        parts = decode_header(s)
        for part, encoding in parts:
            if isinstance(part, bytes):
                if encoding:
                    try:
                        decoded_parts.append(part.decode(encoding))
                    except (UnicodeDecodeError, LookupError):
                        decoded_parts.append(part.decode('utf-8', errors='ignore'))
                else:
                    decoded_parts.append(part.decode('utf-8', errors='ignore'))
            else:
                decoded_parts.append(str(part))
        return ''.join(decoded_parts)
    
    def get_email_content(self, msg, email_id=None, attachments_dir=None):
        """Extract email content from message object"""
        content = {
            'text': '',
            'html': '',
            'attachments': []
        }
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Skip multipart containers
                if content_type.startswith('multipart/'):
                    continue
                
                # Handle attachments
                if "attachment" in content_disposition or part.get_filename():
                    filename = part.get_filename()
                    if filename:
                        decoded_filename = self.decode_mime_words(filename)
                        attachment_data = part.get_payload(decode=True)
                        
                        attachment_info = {
                            'filename': decoded_filename,
                            'content_type': content_type,
                            'size': len(attachment_data) if attachment_data else 0,
                            'saved_path': None
                        }
                        
                        # Save attachment to file if directory provided
                        if attachments_dir and attachment_data:
                            try:
                                # Create safe filename
                                safe_filename = "".join(c for c in decoded_filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
                                if not safe_filename:
                                    safe_filename = f"attachment_{len(content['attachments'])}"
                                
                                # Add email ID to prevent conflicts
                                if email_id:
                                    name, ext = os.path.splitext(safe_filename)
                                    safe_filename = f"{name}_{email_id}{ext}"
                                
                                attachment_path = os.path.join(attachments_dir, safe_filename)
                                
                                # Handle duplicate filenames
                                counter = 1
                                original_path = attachment_path
                                while os.path.exists(attachment_path):
                                    name, ext = os.path.splitext(original_path)
                                    attachment_path = f"{name}_{counter}{ext}"
                                    counter += 1
                                
                                with open(attachment_path, 'wb') as f:
                                    f.write(attachment_data)
                                
                                attachment_info['saved_path'] = attachment_path
                                print(f"  Saved attachment: {decoded_filename} ({len(attachment_data)} bytes)")
                                
                            except Exception as e:
                                print(f"  Error saving attachment {decoded_filename}: {e}")
                        
                        content['attachments'].append(attachment_info)
                    continue
                
                # Get email body
                try:
                    body = part.get_payload(decode=True)
                    if body:
                        charset = part.get_content_charset() or 'utf-8'
                        body_text = body.decode(charset, errors='ignore')
                        
                        if content_type == "text/plain":
                            content['text'] = body_text
                        elif content_type == "text/html":
                            content['html'] = body_text
                except Exception as e:
                    print(f"Error decoding email part: {e}")
        else:
            # Single part message
            try:
                body = msg.get_payload(decode=True)
                if body:
                    charset = msg.get_content_charset() or 'utf-8'
                    content['text'] = body.decode(charset, errors='ignore')
            except Exception as e:
                print(f"Error decoding single part message: {e}")
        
        return content
    
    def retrieve_emails(self, folder="INBOX", limit=None, save_to_file=True, output_dir="emails", save_attachments=True):
        """Retrieve emails from specified folder"""
        if not self.connection:
            print("Not connected to server")
            return []
        
        try:
            # Select folder
            status, messages = self.connection.select(folder)
            if status != 'OK':
                print(f"Error selecting folder {folder}")
                return []
            
            # Get message count
            num_messages = int(messages[0])
            print(f"Found {num_messages} messages in {folder}")
            
            # Determine range of messages to fetch
            if limit and limit < num_messages:
                start = num_messages - limit + 1
                message_range = f"{start}:{num_messages}"
            else:
                message_range = "1:*"
            
            # Search for all messages
            status, message_ids = self.connection.search(None, "ALL")
            if status != 'OK':
                print("Error searching for messages")
                return []
            
            message_ids = message_ids[0].split()
            if limit:
                message_ids = message_ids[-limit:]  # Get most recent messages
            
            emails = []
            
            # Create output directory if saving to files
            if save_to_file:
                os.makedirs(output_dir, exist_ok=True)
                
                # Create attachments directory if saving attachments
                attachments_dir = None
                if save_attachments:
                    attachments_dir = os.path.join(output_dir, "attachments")
                    os.makedirs(attachments_dir, exist_ok=True)
            
            print(f"Retrieving {len(message_ids)} messages...")
            
            for i, msg_id in enumerate(message_ids, 1):
                try:
                    # Fetch message
                    status, msg_data = self.connection.fetch(msg_id, "(RFC822)")
                    if status != 'OK':
                        print(f"Error fetching message {i}")
                        continue
                    
                    # Parse email
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    # Extract email information
                    email_data = {
                        'id': msg_id.decode(),
                        'subject': self.decode_mime_words(msg.get("Subject", "")),
                        'from': self.decode_mime_words(msg.get("From", "")),
                        'to': self.decode_mime_words(msg.get("To", "")),
                        'cc': self.decode_mime_words(msg.get("Cc", "")),
                        'date': msg.get("Date", ""),
                        'message_id': msg.get("Message-ID", ""),
                        'content': self.get_email_content(
                            msg, 
                            email_id=msg_id.decode(),
                            attachments_dir=attachments_dir if save_attachments else None
                        )
                    }
                    
                    emails.append(email_data)
                    
                    # Show attachment info
                    if email_data['content']['attachments']:
                        print(f"  Message {i} has {len(email_data['content']['attachments'])} attachment(s)")
                    
                    # Save individual email to file
                    if save_to_file:
                        filename = f"email_{i:04d}_{msg_id.decode()}.json"
                        filepath = os.path.join(output_dir, filename)
                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(email_data, f, indent=2, ensure_ascii=False)
                    
                    if i % 10 == 0:
                        print(f"Processed {i}/{len(message_ids)} messages")
                
                except Exception as e:
                    print(f"Error processing message {i}: {e}")
                    continue
            
            print(f"Successfully retrieved {len(emails)} emails")
            
            # Count total attachments
            total_attachments = sum(len(email_data['content']['attachments']) for email_data in emails)
            if total_attachments > 0:
                print(f"Downloaded {total_attachments} attachments")
            
            # Save summary file
            if save_to_file:
                summary_file = os.path.join(output_dir, "email_summary.json")
                summary = {
                    'total_emails': len(emails),
                    'total_attachments': total_attachments,
                    'folder': folder,
                    'retrieved_at': datetime.now().isoformat(),
                    'attachments_saved': save_attachments,
                    'emails': [
                        {
                            'id': email_data['id'],
                            'subject': email_data['subject'][:100],
                            'from': email_data['from'],
                            'date': email_data['date'],
                            'attachment_count': len(email_data['content']['attachments'])
                        }
                        for email_data in emails
                    ]
                }
                with open(summary_file, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, indent=2, ensure_ascii=False)
                
                print(f"Emails saved to {output_dir} directory")
                if save_attachments and total_attachments > 0:
                    print(f"Attachments saved to {os.path.join(output_dir, 'attachments')} directory")
                print(f"Summary saved to {summary_file}")
            
            return emails
            
        except Exception as e:
            print(f"Error retrieving emails: {e}")
            return []
    
    def disconnect(self):
        """Close connection to IMAP server"""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
                print("Disconnected from Yahoo IMAP server")
            except:
                pass

def main():
    retriever = YahooEmailRetriever()
    
    # Get credentials
    print("Yahoo Email Retriever")
    print("Note: You'll need to use an App Password, not your regular Yahoo password")
    print("Generate one at: https://login.yahoo.com/account/security")
    print()
    
    username = input("Enter your Yahoo email address: ")
    password = getpass.getpass("Enter your App Password: ")
    
    # Connect to Yahoo
    if not retriever.connect(username, password):
        return
    
    try:
        # List available folders
        print("\nAvailable folders:")
        folders = retriever.list_folders()
        for i, folder in enumerate(folders, 1):
            print(f"{i}. {folder}")
        
        # Select folder
        folder_choice = input(f"\nSelect folder (1-{len(folders)}) or press Enter for INBOX: ").strip()
        if folder_choice.isdigit() and 1 <= int(folder_choice) <= len(folders):
            selected_folder = folders[int(folder_choice) - 1]
        else:
            selected_folder = "INBOX"
        
        print(f"Selected folder: {selected_folder}")
        
        # Ask for limit
        limit_input = input("Enter number of emails to retrieve (or press Enter for all): ").strip()
        limit = int(limit_input) if limit_input.isdigit() else None
        
        # Ask for attachment download preference
        download_attachments = input("Download attachments? (y/n, default=y): ").strip().lower()
        save_attachments = download_attachments != 'n'
        
        # Retrieve emails
        emails = retriever.retrieve_emails(
            folder=selected_folder,
            limit=limit,
            save_to_file=True,
            output_dir=f"yahoo_emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            save_attachments=save_attachments
        )
        
        print(f"\nRetrieved {len(emails)} emails successfully!")
        
    finally:
        retriever.disconnect()

if __name__ == "__main__":
    main()
