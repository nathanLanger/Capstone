from website import create_app
#pip install -r requirements.txt (if I listed them in a requirements.txt)

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
