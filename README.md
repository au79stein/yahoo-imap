# yahoo-imap

Download yahoo email and save with attachments.
You will be able to select folders to download, or INBOX.
You can also control the size of the batches to download, or ALL.


## How to use
in order to access yahoo mail, you will need to set up a one-time application password.  this is not your regular user password!
this can be done by logging into yahoo and going [here](https://login.yahoo.com/account/security).

when this code is invoked you will be required to enter your yahoo email address and app password:

```
    # Get credentials
    print("Yahoo Email Retriever")
    print("Note: You'll need to use an App Password, not your regular Yahoo password")
    print("Generate one at: https://login.yahoo.com/account/security")
    print()

    username = input("Enter your Yahoo email address: ")
    password = getpass.getpass("Enter your App Password: ")
```


```
MacBook-Pro:yahoo_emails_20250729_151324 richgoldstein$ cat email_summary.json | jq -r '.emails[] | "\(.id)\t\(.subject)\t\(.attachment_count)\t\(.date)"'
1	Re: test	0	Fri, 30 Aug 2024 22:22:42 -0400
4	Meet your contest winners!	0	Thu, 19 Sep 2024 20:09:49 +0000
5	Flickr in Focus 🍂 September.	0	Thu, 26 Sep 2024 17:30:31 +0000
6	It’s almost spooky season…	0	Fri, 27 Sep 2024 19:29:02 +0000
8	MyFlickrYear is on the horizon…	0	Tue, 15 Oct 2024 18:02:02 +0000
9	Own a piece of Flickr history.	0	Mon, 21 Oct 2024 19:16:13 +0000
11	Time to stock up on film: Polaroid Week 2024 is almost here!	0	Fri, 25 Oct 2024 19:40:26 +0000
14	Flickr in Focus 👻 October	0	Wed, 30 Oct 2024 17:02:51 +0000
17	A(n) historic 30-year Flickr account could be yours!	0	Fri, 08 Nov 2024 17:24:37 +0000
18	Flickr in Focus 🍂 November	0	Tue, 26 Nov 2024 18:04:37 +0000
19	It’s almost time…for Your Best Shot!	0	Fri, 29 Nov 2024 19:42:01 +0000
20	Doctor’s orders: It’s time for Your Best Shot! 	0	Sun, 01 Dec 2024 18:39:29 +0000
21	It’s here, it’s here: MyFlickrYear!	0	Tue, 03 Dec 2024 19:46:08 +0000
22	Support one of the world’s largest collections of photography.	0	Mon, 09 Dec 2024 18:51:14 +0000
23	Don’t miss MyFlickrYear!	0	Tue, 10 Dec 2024 19:06:35 +0000
24	WARNING: INSPIRATION INSIDE	0	Tue, 17 Dec 2024 18:25:45 +0000
27	Flickr in Focus ☃️ December	0	Thu, 19 Dec 2024 18:02:08 +0000
28	Don’t miss MyFlickrYear!	0	Tue, 31 Dec 2024 17:34:15 +0000
29	The 2024 Flickr Year in Review is here!	0	Thu, 16 Jan 2025 19:34:00 +0000
31	FLICKR CONFIRMS THE EXISTENCE OF TIME TRAVEL	0	Thu, 23 Jan 2025 18:49:48 +0000
32	Flickr in Focus 📅 January	0	Wed, 29 Jan 2025 18:01:39 +0000
33	WINNERS ANNOUNCED: Your Best Shot 2024.	0	Thu, 30 Jan 2025 20:55:21 +0000
34	21 days of creativity for Flickr’s 21st birthday.	0	Mon, 03 Feb 2025 21:02:51 +0000
35	Sign in to your Google Account	0	Sat, 08 Feb 2025 16:27:01 GMT
36	It’s our birthday!	0	Mon, 10 Feb 2025 19:04:08 +0000
37	Flickr groups: You in?	0	Tue, 18 Feb 2025 19:09:09 +0000
38	Sign in to your Google Account	0	Wed, 19 Feb 2025 20:02:16 GMT
39	Does “niche” rhyme with “sheesh” or “itch”?	0	Wed, 19 Feb 2025 22:32:34 +0000
40	Flickr in Focus 💝 February	0	Wed, 26 Feb 2025 18:03:44 +0000
41	Want $5,000+ to support your photography? 	0	Mon, 17 Mar 2025 19:09:26 +0000
42	Important updates to our Terms of Service	0	18 Mar 2025 01:50:48 -0000
44	Flickr in Focus 🍀 March	0	Thu, 27 Mar 2025 17:03:52 +0000
45	Introducing Flickr’s Photographer of the Month	0	Wed, 02 Apr 2025 18:45:16 +0000
46	‘RoidWeek 2025 is just around the corner.	0	Sun, 20 Apr 2025 16:05:26 +0000
47	Flickr in Focus 🌼 April	0	Tue, 29 Apr 2025 17:00:42 +0000
48	Introducing: Flickr’s Monthly Photo Challenge!	0	Thu, 01 May 2025 21:48:53 +0000
49	Introducing “The Many Faces of Mom” Photo Contest.	0	Mon, 05 May 2025 20:20:30 +0000
51	“Mom” means more on Flickr.	0	Fri, 09 May 2025 17:30:45 +0000
52	[Announcement] Find the right gear with Camera Finder.	0	Tue, 13 May 2025 18:06:10 +0000
53	“Many Faces of Mom” contest submissions close soon!	0	Fri, 16 May 2025 17:49:02 +0000
54	Flickr in Focus 🌦️ May	0	Thu, 29 May 2025 17:05:50 +0000
57	As a Pro, you’re our priority.	0	Thu, 05 Jun 2025 17:30:16 +0000
58	“The Many Faces of Mom” winners announced!	0	Mon, 09 Jun 2025 19:00:48 +0000
59	[Flickr Fundamentals] Group admin essentials.	0	Tue, 10 Jun 2025 16:15:36 +0000
61	Changes to your Yahoo Mail Storage are coming soon	0	25 Jun 2025 08:58:54 -0000
62	Flickr in Focus 🌈 June	0	Thu, 26 Jun 2025 17:01:02 +0000
63	Unexpected sign-in attempt	0	Thu, 17 Jul 2025 01:49:22 +0000 (UTC)
64	Passkey created for your Yahoo account	0	Thu, 17 Jul 2025 01:49:35 +0000 (UTC)
67	[Flickr Fundamentals] Make the most of Flickr search	0	Wed, 23 Jul 2025 18:38:46 +0000
68	An app password was generated for your Yahoo account	0	Tue, 29 Jul 2025 20:01:01 +0000 (UTC)
69	Your app password was used to sign in to a third-party app	0	Tue, 29 Jul 2025 20:04:56 +0000 (UTC)
70	Your app password was deleted	0	Tue, 29 Jul 2025 21:09:08 +0000 (UTC)
71	An app password was generated for your Yahoo account	0	Tue, 29 Jul 2025 21:10:25 +0000 (UTC)
```

## read attachments

```
MacBook-Pro:yahoo_emails_20250729_151324 richgoldstein$ cat email_0002_2.json | jq -r '.content.attachments'
[
  {
    "filename": "Invoice-FLICKR-XXXXXXXX.pdf",
    "content_type": "application/pdf",
    "size": 29074,
    "saved_path": "yahoo_emails_20250729_151324/attachments/Invoice-FLICKR-XXXXXXXX.pdf"
  },
  {
    "filename": "Receipt-XXXX-XXXX.pdf",
    "content_type": "application/pdf",
    "size": 29831,
    "saved_path": "yahoo_emails_20250729_151324/attachments/Receipt-XXXX-XXXX.pdf"
  }
]
MacBook-Pro:yahoo_emails_20250729_151324 richgoldstein$
```
