# Einstein Vision
## Overview

In this project, we developed a Blender-based visualization tool that produces realistic 3D representations of what self-driving cars "see" in their surroundings.  This script takes detection data from autonomous vehicles and generates high-quality representations of objects, their positions, and expected movements in the driving scene.

 The technology converts raw detection data into user-friendly visual displays, making AI decision-making apparent and accessible, bridging the gap between complicated autonomous systems and human perception.

## Features

- **Multi-object visualization**: Renders vehicles, pedestrians, traffic lights, road signs, and other road objects
- **Dynamic lighting effects**: Shows vehicle brake lights and turn indicators based on detected states
- **Motion prediction**: Visualizes the predicted movement of objects with directional arrows
- **Lane detection**: Renders lane markings with appropriate styling (solid/dashed)
- **Traffic signal states**: Displays traffic lights with correct color states and directional arrows
- **Road sign recognition**: Places detected road signs with appropriate text (speed limits, stop signs)
- **Scene organization**: Uses Blender collections to organize scene elements logically

## Requirements

- **Blender 4.0+** 
- Python libraries: `numpy` (used for lane rendering calculations)
- GPU with CUDA support (recommended for faster rendering)

## Input Data Format

The script processes multiple JSON files containing detection data:
- `road_signs_3d.json`: Stop signs and speed limit signs with 3D positions
- `vehicle_detections_with_lights.json`: Vehicle positions, orientations, and light states
- `traffic_lights_3d_scene8.json`: Traffic light positions and states
- `road_objects_3d.json`: Other road objects (trash cans, traffic cones)
- `world_lane_data_s8.json`: Lane marking positions and types
- Pedestrian OBJ files in the specified directory

## Setup and Configuration

1. **Asset Preparation**:
   - Ensure all referenced blend files (vehicles, signs, traffic lights) are available in the specified paths
   - Verify pedestrian OBJ files are correctly named with the pattern `frame_XXXXXX_person_X.obj`

2. **Configuration Variables**:
   - Adjust output paths in the script header:
     ```python
     output_directory = "/path/to/output"
     final_video_path = "/path/to/video.mp4"
     ```
   - Modify render settings as needed:
     ```python
     render_width = 1920
     render_height = 1080
     render_quality = 90
     render_samples = 64
     ```
   - Update frame range settings:
     ```python
     start_frame = 0
     frame_step = 1
     max_frames = 2157
     frame_interval = 10  # Render every 10th frame
     ```

## Usage

### Running in Blender GUI:
1. Open Blender
2. Go to Scripting workspace
3. Open the script file
4. Click the "Run Script" button or press Alt+P

### Running Headless (Command Line):
```bash
blender -b -P combined.py
```

## Output

The script generates:
- Individual rendered frames in JPEG format in the specified output directory


## Extension and Customization

The script is designed to be modular, allowing for:
- Addition of new object types by creating appropriate import functions
- Adjustment of visual styles through material settings
- Modification of scene environment (sky, ground, lighting)
- Customization of camera positioning and movement




