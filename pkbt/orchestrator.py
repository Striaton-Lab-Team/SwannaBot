import subprocess
from typing import Callable
from pkbt.emulator import EmulatorProc
from pkbt.mgba_connection import MGBAConnection

class Orchestrator:

    def __init__(self, emu: EmulatorProc, client: MGBAConnection) -> None:
        self.emu = emu
        self.client = client

    def perform_task(self, task):
        return task(self.emu, self.client)

    def exit(self) -> None:
        try:
            self.client.disconnect()
            self.emu.process.terminate()
        except Exception as e:
            print(f"Error exiting orchestrator: {e}")

    def is_healthy(self) -> bool:
        """Check if both the emulator process and client connection are healthy."""
        emulator_alive = self.emu.is_alive()
        client_connected = self.client.connected
        return emulator_alive and client_connected

if __name__ == "__main__":

    from pkbt.mgba_connection import MGBAConnection
    from pkbt.emulator import EmulatorProc
    from pkbt.config import (
        POKEMON_RED_GB_ROM,
        POKEMON_TRANSPORTER_GBA,
        SERVER_SCRIPT,
        MGBA_DEV,
        INPUT_DISPLAY_SCRIPT
    )
    import time
    from pkbt.input.key_event import KeyEvent
    from pkbt.input.key_event_type import KeyEventType
    from pkbt.input.key_type import KeyType
    from pkbt.state_manager import initialize_state_manager

    emu = EmulatorProc(
        MGBA_DEV,
        [
            POKEMON_TRANSPORTER_GBA,
            POKEMON_RED_GB_ROM
        ],
        [SERVER_SCRIPT, INPUT_DISPLAY_SCRIPT]
    )

    client1 = MGBAConnection('localhost', 8888)
    client2 = MGBAConnection('localhost', 8889)

    print("Starting emulator...")
    initialize_state_manager()
    emu.start()

    # Give both Lua scripts time to start their servers.
    time.sleep(10)

    print("Connecting to player 1...")
    client1.connect()

    print("Connecting to player 2...")
    client2.connect()

    print("Pressing A on player 1...")
    client1.execute_event(
        KeyEvent(KeyEventType.PUSH, KeyType.A)
    )

    time.sleep(1)

    print("Pressing A on player 2...")
    client2.execute_event(
        KeyEvent(KeyEventType.PUSH, KeyType.A)
    )
    
    time.sleep(3)
    
    print("Pressing A on player 1...")
    client1.execute_event(
        KeyEvent(KeyEventType.PUSH, KeyType.A)
    )

    time.sleep(1)

    print("Pressing A on player 2...")
    client2.execute_event(
        KeyEvent(KeyEventType.PUSH, KeyType.A)
    )

    time.sleep(1000)

    print("Cleaning up...")
    client1.disconnect()
    client2.disconnect()
    emu.stop()