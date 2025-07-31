#!/usr/bin/env python3

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
    
    def get_email_content(self, msg):
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
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        content['attachments'].append({
                            'filename': self.decode_mime_words(filename),
                            'content_type': content_type,
                            'size': len(part.get_payload(decode=True) or b'')
                        })
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
    
    def retrieve_emails(self, folder="INBOX", limit=None, save_to_file=True, output_dir="emails"):
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
                        'content': self.get_email_content(msg)
                    }
                    
                    emails.append(email_data)
                    
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
            
            # Save summary file
            if save_to_file:
                summary_file = os.path.join(output_dir, "email_summary.json")
                summary = {
                    'total_emails': len(emails),
                    'folder': folder,
                    'retrieved_at': datetime.now().isoformat(),
                    'emails': [
                        {
                            'id': email_data['id'],
                            'subject': email_data['subject'][:100],
                            'from': email_data['from'],
                            'date': email_data['date']
                        }
                        for email_data in emails
                    ]
                }
                with open(summary_file, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, indent=2, ensure_ascii=False)
                
                print(f"Emails saved to {output_dir} directory")
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
        
        # Retrieve emails
        emails = retriever.retrieve_emails(
            folder=selected_folder,
            limit=limit,
            save_to_file=True,
            output_dir=f"yahoo_emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        print(f"\nRetrieved {len(emails)} emails successfully!")
        
    finally:
        retriever.disconnect()

if __name__ == "__main__":
    main()
