import os
from login import login_user
from register import register_user
from cracker import run_cracker
from speed_test import run_speed_test
from database import init_db

def banner():
    os.system("cls" if os.name == "nt" else "clear")

    print(r"""
██╗   ██╗ █████╗ ██╗   ██╗██╗  ████████╗
██║   ██║██╔══██╗██║   ██║██║  ╚══██╔══╝
██║   ██║███████║██║   ██║██║     ██║
██║   ██║██╔══██║██║   ██║██║     ██║
╚██████╔╝██║  ██║╚██████╔╝███████╗██║
 ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝
""")

    print("VAULT CLI BY DHANUS KIRUTHICK")
    print("-" * 45)

def main():
    init_db()
    banner()

    while True:
        print("\n[1] Register")
        print("[2] Login")
        print("[3] Crack (Lab)")
        print("[4] Speed Test")
        print("[5] Exit")

        choice = input("\nSelect option: ")

        if choice == "1":
            register_user()

        elif choice == "2":
            login_user()

        elif choice == "3":
            run_cracker()

        elif choice == "4":
            run_speed_test()

        elif choice == "5":
            print("Exiting Vault CLI...")
            break

        else:
            print("Invalid option")

if __name__ == "__main__":
    main()
