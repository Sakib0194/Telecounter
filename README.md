# Telecounter
A GUI created with PyQt5 for counting messages in Telegram Groups from users. Requires Python 3.6+
This was created for personal use and to make my life easier

<h4> How to run</h4>

Download the executable from latest release for one click runnable or download source from Release and run Telecounter.py with required library

GUI Design tested only on Windows and Arch Linux.

The GUI logo was taken randomly from google. You are free to change the logo to your desiring but the filename must remain logo.png

<h4>What is a session in the GUI?</h4>

The GUI uses Telethon library. It automatically creates a session file that saves the necessary data to automatically log in again each time you run it. All data are saved locally. All action are done by Telegram API. It is asked to never share the session file/s with anyone. To create a session API ID and API Hash will be required. It is possible to find them on official [Telegram website](https://my.telegram.org/)

<h4>What is KPI ID?</h4>

You can select any number of Telegram user individually to view their message numbers separately from all users. If you want to count total messages from 10 users out of 10k messages, this is the way to go

<h4>What is Multi Session counting?</h4>

The GUI can distribute counting tasks among multiple Telegrams sessions by dividing them equally in parts if available, which will result in faster action and log placement. Especially useful if going for a long counting session. It can increase speed from 2x to indefinite based on the amount of sessions available