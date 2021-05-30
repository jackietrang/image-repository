VALID_FILE_TYPES = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    status = '.' in filename and filename.rsplit('.', 1)[1].lower() in VALID_FILE_TYPES
    if status == False:
        raise ValueError
    return True