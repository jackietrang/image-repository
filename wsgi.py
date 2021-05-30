from app import db
main = db.create_all()

if __name__ == "__main__":
    main.run(debug=False)