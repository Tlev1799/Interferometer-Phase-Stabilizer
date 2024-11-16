# UTEM System Stabilizer

## Requirements

### Python Libraries
Install the following Python libraries by running these commands:

- Camera interface:  
  ```bash
  pip install pyflycap2
  ```

- Stage interface:  
  ```bash
  pip install newportxps
  ```

### Standard Libraries
Ensure the following libraries are installed:  
- `numpy`
- `matplotlib`
- `opencv-python`

---

## How to Run

1. After installing the necessary libraries, open and run `_stabilizer.py` from the `UTEM System` folder on a computer connected to the stage and camera.  

   - **Camera Configuration:**  
     Update the serial number, width, and height parameters in the `UTEM System\camera_controller.py` file to match your camera.

   - **Stage Configuration:**  
     If the default IP is incorrect, add the `host` parameter when creating the object in `main`.  
     Additionally, update the group name if required in `UTEM System\stage_controller.py`.

---

## Plotting Results

1. Before running the stabilizer, update the path to save the text files in the `_stabilizer.py` file (inside the `finally` statement).
2. After the program finishes, run the `_plot_graphs.py` file in the `UTEM System` folder.  
   Ensure you also update the file paths in `_plot_graphs.py` before running.

---

## Optimization Parameters

You can modify the following parameters in `_stabilizer.py` to optimize the system:

- **`g_deviation`:**  
  Specifies the pixel range (`±g_deviation`) to search for constructive interference from the last known coordinate.

- **`g_min_distance_fix`:**  
  The minimum number of pixels considered an error to be fixed. Smaller deviations are ignored.

- **`g_max_distance_fix`:**  
  The maximum number of pixels considered an error to be fixed. Larger deviations are ignored as measurement mistakes.

- **`g_step_size`:**  
  If the calculated correction distance is `X` nm, the actual movement will be `g_step_size * X` nm. This ensures convergence to the optimal solution.

---
