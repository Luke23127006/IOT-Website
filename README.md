# How to Run the Project

Follow these steps to set up and run the application:

## 1. Create a `.env` File

Obtain the required `.env` file content from the project owner and place it in the project root directory.

## 2. Install Dependencies

Install all required packages using:

```bash
pip install -r requirements.txt
```

## 3. Start the Application

Run the following command in your terminal:

```bash
python main.py
```

## 4. Access the Application

After starting, you should see output similar to:

```
 * Serving Flask app 'app'
 * Debug mode: on
    WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
    Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 134-328-739
```

Hold `Ctrl` and click [http://127.0.0.1:5000](http://127.0.0.1:5000) to open the app in your browser.

---

**Note:** This setup is for development only. For production, use a proper WSGI server.
