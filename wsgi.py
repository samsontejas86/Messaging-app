from app import app

# This is the entry point for Vercel
app = app  # This line is important for Vercel to detect the app

if __name__ == '__main__':
    app.run() 