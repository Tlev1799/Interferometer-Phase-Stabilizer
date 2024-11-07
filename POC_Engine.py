from engine_controller import EngineController

# Connect to engine.
ec = None
try:
    ec = EngineController()
    ec.connect()
    ec.prepare_engine(1, 0.01, 0.01)
    ec.get_movement_data()

except Exception as e:
    print(f"Error connecting to engine: {e}")
    print("Exiting...")
    exit()

import ipdb; ipdb.set_trace()