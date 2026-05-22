from datetime import datetime

def log_event(action , username , status):

    #santize username for log
    username = username.replace("\n","").replace("\r","")

    #timestamp for log
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #log format
    log_line = f"[{timestamp}] ACTION={action} USER={username} STATUS={status}\n"

    #append log safetly
    with open("audit.log" , "a") as log_file:
        log_file.write(log_line)

        log_event("LOGIN", "dk", "FAILED")