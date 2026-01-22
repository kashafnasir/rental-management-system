from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Ensure upload directory exists
    upload_dir = os.path.join('app', 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    print(" RENTAL MANAGEMENT SYSTEM STARTING...")
   
    print(f"Server running on: http://localhost:5000")
    print(f" Default Login: admin@rental.com")
    print(f" Default Password: admin123")
   
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=True
    )