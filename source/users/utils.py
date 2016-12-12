def username_display(user):
    if user.first_name:
        return user.get_full_name()
    else:
        return user.email
