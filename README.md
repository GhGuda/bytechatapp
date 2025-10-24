ByteChatApp

ByteChatApp is a simple chat application built with Django, allowing users to register, chat, and manage profiles. Real-time updates are implemented using AJAX polling.

Features

User authentication: signup, login, logout

Real-time chat between users using AJAX polling

Edit & delete messages

Profile management:

Upload profile image

Update username, email, bio

View other users’ profiles

Floating Send Message button on profile view

Mobile-friendly, responsive UI

Audio notifications for sent and received messages

Screenshots

Profile Page:


Chat Page:


View Profile Page:


(Replace with actual screenshots in docs/screenshots/ folder)

Installation

Clone the repository:

git clone https://github.com/GhGuda/bytechatapp.git
cd bytechatapp


Create a virtual environment:

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows


Install dependencies:

pip install -r requirements.txt


Apply migrations:

python manage.py makemigrations
python manage.py migrate


Create a superuser (optional):

python manage.py createsuperuser


Run the development server:

python manage.py runserver


Open in your browser:

http://127.0.0.1:8000/

Project Structure
ByteBrigade/
│
├── chat/                     # Django app
│   ├── templates/            # HTML templates
│   ├── static/css/           # CSS files
│   ├── static/sounds/        # Audio notifications
│   ├── models.py             # CustomUser & ChatMessage
│   ├── views.py
│   ├── urls.py
│
├── manage.py
└── ByteBrigade/              # Project settings

Models
CustomUser

Extends Django AbstractUser

Fields: profile_img, bio, mobile_number, is_online, last_seen

ChatMessage

Fields: sender, receiver, content, timestamp, edited

How Chat Works

Sending Messages: AJAX sends messages to the server without reloading.

Fetching Messages: Chat body polls the server every 2 seconds using AJAX to fetch new messages.

Editing & Deleting: AJAX updates or removes messages dynamically.

Audio Notifications: Plays sound for sent and received messages.

Usage

Register/login → update your profile

Click a user to start a chat

Edit or delete your messages

View other users’ profiles and send messages using the floating Send Message button

Future Improvements

Real-time chat using WebSockets / Django Channels (optional)

Typing indicators & read receipts

Group chat functionality

Dark mode and theme customization

Push notifications