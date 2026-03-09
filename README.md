AI Nexus 🤖
AI Nexus is a web application built with Streamlit that allows you to manage multiple LLMs, store your API keys securely in Firebase, and maintain conversation context—even when switching between different models.

🚀 Key Features
Multi-Model Support: Easily define your preferred models (e.g., Gemini, Groq, Llama, Mistral).

Cloud Persistence: Your API keys and model preferences are stored in your personal Firebase database.

Silent History Sync: Maintain the "thread" of your conversation across different models with a single click.

Streamlined UI: A clean interface to switch models on the fly.

🛠️ Step-by-Step Installation
1. Prerequisites
Python 3.10 or higher.

A Firebase account.

2. Firebase Setup (Required)
Go to the Firebase Console and create a new Project.

Enable Authentication (Email/Password provider).

Create a Cloud Firestore Database (Start in Test Mode).

Go to Project Settings > Service Accounts.

Click Generate new private key. This will download a .json file—keep this safe and upload it to the app when prompted.

Go to Project Settings > General to find your Web API Key. You will need this to log in to the app.

3. Local Setup
Clone the repository:

Bash
git clone https://github.com/your-username/ai-nexus.git
cd ai-nexus
Install the required dependencies:

Bash
pip install -r requirements.txt
Run the application:

Bash
streamlit run main.py
4. How to use it
Once the browser opens, enter your Firebase Web API Key.

Upload the serviceAccountKey.json file you generated earlier.

Sign up/Login to your account.

In the sidebar, add your models (one per line) and their respective API keys.

Save your settings and start chatting!

⚠️ Important Note on API Credits
This app acts as a bridge. While the application is free, most high-tier models (Gemini, GPT-4, Claude) require you to have paid credits or an active billing account with the specific model provider to use their API keys.
