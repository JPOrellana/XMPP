import asyncio
from login import LoginGUI

def main():
    login_gui = LoginGUI()
    login_gui.run()

if __name__ == "__main__":
    asyncio.run(main())
