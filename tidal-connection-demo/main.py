import tidalapi

session = tidalapi.Session()
login, future = session.login_oauth()

print("Open the URL to log in", login.verification_uri_complete)

print(future.result())
print(session.check_login())
