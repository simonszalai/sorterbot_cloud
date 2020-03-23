def is_session_id_invalid(sess_name):
    if not 1 <= len(sess_name) <= 31:
        return "Length must be between 1 and 31 characters!"
    try:
        int(sess_name[0])
        return "Session ID cannot start with a number!"
    except ValueError:
        return False