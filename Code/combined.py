import bpy

if "Cube" in bpy.data.objects:
    bpy.data.objects["Cube"].select_set(True)
    bpy.ops.object.delete()
    print(" Default Cube removed.")
import json
from mathutils import Vector, Euler, Matrix
import math
import os
import glob  # Added for pedestrian file pattern matching
import numpy as np  # Added for lane rendering

# User-configurable settings
# Render settings
output_directory = r"/home/neel/Desktop/cv_1/Einstein Vision/s8_final"  # Directory for rendered frames
final_video_path = r"/home/neel/Desktop/cv_1/Einstein Vision/final_render.mp4"  # Path for final video
frame_interval = 10 # Render every 10th frame
render_width = 1920  # Width of render in pixels
render_height = 1080  # Height of render in pixels
render_quality = 90  # JPEG quality for frames (0-100)
render_samples = 64  # Samples for Cycles renderer

# Road signs
json_file_path = r"/home/neel/Desktop/cv_1/Einstein Vision/depth_blender/scene8/road_signs_3d.json"
stop_sign_blend_file = r"/home/neel/Desktop/cv_1/Einstein Vision/blender_assets/Assets/StopSign.blend"
speed_limit_sign_blend_file = r"/home/neel/Desktop/cv_1/Einstein Vision/blender_assets/Assets/SpeedLimitSign.blend"
speed_breaker_blend_file = r"/home/neel/Desktop/cv_1/Einstein Vision/blender_assets/Assets/speed_breaker.blend"
# Multi-object data paths
vehicle_json_file_path = r"/home/neel/Desktop/cv_1/Einstein Vision/depth_blender/scene8/vehicle_detections_with_lights.json"
traffic_light_json_file_path = r"/home/neel/Desktop/cv_1/Einstein Vision/depth_blender/scene8/traffic_lights_3d_scene8.json"
road_objects_json_file_path = r"/home/neel/Desktop/cv_1/Einstein Vision/depth_blender/scene8/road_objects_3d.json"
lane_json_file_path = r"/home/neel/Desktop/cv_1/Einstein Vision/depth_blender/scene8/world_lane_data_s8.json"

# Pedestrian configuration
human_pose_folder = r"/home/neel/Desktop/cv_1/Einstein Vision/depth_blender/scene8/pedestrian_osx"

# Camera parameters
fx = 1594.7  # focal length x
fy = 1607.7  # focal length y
cx = 655.2961  # principal point x
cy = 414.3627  # principal point y

# Animation settings
start_frame = 2040  # Start with frame 10 instead of 1
frame_step = 1  # Number of Blender frames between each JSON frame
max_frames = 2157

# Pedestrian position offset
pedestrian_position_offset = (-20.0, 3.5, 0.0)

# Define paths to different vehicle blend files
vehicle_blend_files = {
    "sedan": r"/home/neel/Desktop/cv_1/Einstein Vision/blender_assets/Assets/Vehicles/SedanAndHatchback.blend",
    "suv": r"/home/neel/Desktop/cv_1/Einstein Vision/blender_assets/Assets/Vehicles/SUV.blend", 
    "truck": r"/home/neel/Desktop/cv_1/Einstein Vision/blender_assets/Assets/Vehicles/Truck.blend",
    "motorcycle": r"/home/neel/Desktop/cv_1/Einstein Vision/blender_assets/Assets/Vehicles/Motorcycle.blend",
    "bicycle": r"/home/neel/Desktop/cv_1/Einstein Vision/blender_assets/Assets/Vehicles/Bicycle.blend",
    "pickup_truck": r"/home/neel/Desktop/cv_1/Einstein Vision/blender_assets/Assets/Vehicles/PickupTruck.blend",
}

# Traffic light model blend files
traffic_light_blend_files = {
    "red": "/home/neel/Desktop/cv_1/Einstein Vision/blender_assets/Assets/TrafficSignalred.blend",
    "yellow": "/home/neel/Desktop/cv_1/Einstein Vision/blender_assets/Assets/TrafficSignalyellow.blend",
    "green": "/home/neel/Desktop/cv_1/Einstein Vision/blender_assets/Assets/TrafficSignalgreen.blend"
}

# Road objects blend files
trash_can_blend_file = r"/home/neel/Desktop/cv_1/Einstein Vision/blender_assets/Assets/Dustbin.blend" 
traffic_cone_blend_file = r"/home/neel/Desktop/cv_1/Einstein Vision/blender_assets/Assets/TrafficConeAndCylinder.blend"

# Path to arrow blend file
arrow_blend_file = "/home/neel/Desktop/cv_1/Einstein Vision/blender_assets/Assets/Vehicles/arrow.blend"

# Define height offsets for different colored spheres
sphere_heights = {
    "green": 5.2,  # Green sphere at 5.25m 
    "yellow": 5.6, # Yellow sphere at 6.25m
    "red": 6     # Red sphere at 7.25m
}

# Define arrow rotation for each direction (in radians)
arrow_rotations = {
    "up": Euler((0, 0, math.radians(90)), 'XYZ'),
    "down": Euler((0, math.radians(180), math.radians(90)), 'XYZ'),
    "left": Euler((0, math.radians(90), math.radians(90)), 'XYZ'),
    "right": Euler((0, math.radians(270), math.radians(90)), 'XYZ')
}

# Height offset for the arrow above the traffic light
arrow_height_offset = 1.5

# Arrow settings for motion visualization
arrow_size = 1.0  # Scale of the arrow
arrow_height = 1.5  # Height above the vehicle
arrow_color = (1, 0, 0)  # Red color for arrows

# Light settings
light_scale = 0.03  # Size of the light indicators
brake_light_color = (1, 0, 0, 1)  # Red for brake lights
left_indicator_color = (1, 0.5, 0, 1)  # Amber for left indicator
right_indicator_color = (1, 0.5, 0, 1)  # Amber for right indicator
light_emission_strength = 1.0  # Emission strength for the light materials

# Vehicle-specific light offset settings
light_offset_settings = {
    "sedan": {"rear_offset": -0.5, "side_offset": 2, "height_offset": 0.6, "scale_factor": 1.2},
    "suv": {"rear_offset": -0.5, "side_offset": 2, "height_offset": 0.6, "scale_factor": 1.2},
    "truck": {"rear_offset": 0.46, "side_offset": 0.42, "height_offset": 0.45, "scale_factor": 1.5},
    "pickup_truck": {"rear_offset": 0.47, "side_offset": 0.45, "height_offset": 0.38, "scale_factor": 1.3},
    "motorcycle": {"rear_offset": 0.45, "side_offset": 0.25, "height_offset": 0.6, "scale_factor": 0.8},
    "bicycle": {"rear_offset": 0.45, "side_offset": 0.20, "height_offset": 0.6, "scale_factor": 0.7},
}

# Lane rendering settings
lane_material_color = (1.0, 1.0, 1.0, 1.0)  # White color for lane markings

# Set up Blender render settings
# def setup_render_settings():
#     """Configure Blender's render settings for the scene"""
#     scene = bpy.context.scene
    
#     # Set the render engine (using Cycles for better quality)
#     scene.render.engine = 'CYCLES'
    
#     # Set resolution
#     scene.render.resolution_x = render_width
#     scene.render.resolution_y = render_height
#     scene.render.resolution_percentage = 100
    
#     # Set output settings
#     scene.render.image_settings.file_format = 'JPEG'
#     scene.render.image_settings.quality = render_quality
    
#     # Set samples for Cycles
#     if hasattr(scene.cycles, 'samples'):
#         scene.cycles.samples = render_samples
#     elif hasattr(scene.cycles, 'preview_samples'):
#         scene.cycles.preview_samples = render_samples
    
#     # Set output path
#     os.makedirs(output_directory, exist_ok=True)
#     scene.render.filepath = os.path.join(output_directory, "frame_")
    
#     # Set up frame range (will be adjusted per render)
#     scene.frame_start = 1
#     scene.frame_end = 1  # We'll render one frame at a time
    
#     print(f"Render settings configured: {render_width}x{render_height} JPEG, Cycles with {render_samples} samples")


def setup_render_settings():
    """Configure Blender's render settings for optimized rendering"""
    scene = bpy.context.scene
    prefs = bpy.context.preferences

    # ===== Core Render Settings =====
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'  # Enable GPU rendering
    
    # ===== GPU Configuration ===== [4][7]
    # Enable CUDA/NVIDIA OptiX acceleration
    if prefs.addons['cycles'].preferences.has_active_device():
        cycles_prefs = prefs.addons['cycles'].preferences
        cycles_prefs.compute_device_type = 'OPTIX'  # For NVIDIA GPUs
        # cycles_prefs.compute_device_type = 'HIP'  # For AMD GPUs
        cycles_prefs.get_devices()
        
        # Enable first available GPU
        for device in cycles_prefs.devices:
            if device.type == 'CUDA' or device.type == 'OPTIX':
                device.use = True
                print(f"Activated GPU: {device.name}")

    # ===== Quality vs Speed Balance ===== [2][6]
    scene.cycles.samples = 32  # Reduced from 64 (balance quality/speed)
    scene.cycles.adaptive_threshold = 0.05  # Higher = faster, noisier
    scene.cycles.use_denoise = True  # Enable AI denoising
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    
    # ===== Performance Optimizations =====
    scene.cycles.use_adaptive_sampling = True  # Smart sample distribution
    # scene.render.tile_x = 256  # Optimal for GPU rendering [7]
    # scene.render.tile_y = 256
    scene.cycles.persistent_data = True  # Reuse data between frames
    
    # ===== Resolution & Output =====
    scene.render.resolution_x = render_width
    scene.render.resolution_y = render_height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'JPEG'
    scene.render.image_settings.quality = render_quality
    scene.render.filepath = os.path.join(output_directory, "frame_")
    
    # ===== Frame Settings =====
    scene.frame_start = 1
    scene.frame_end = 1
    
    print(f"Render settings configured for GPU: {render_width}x{render_height}")
    print(f"Cycles samples: {scene.cycles.samples}, Using device: {scene.cycles.device}")

def setup_camera():
    """Set up a camera for the scene if it doesn't already exist"""
    # Check if camera exists
    cam = None
    for obj in bpy.data.objects:
        if obj.type == 'CAMERA':
            cam = obj
            break
    
    # Create camera if it doesn't exist
    if cam is None:
        bpy.ops.object.camera_add(location=(-32.524, 0.56592, 7.339))
        cam = bpy.context.active_object
        cam.name = "RenderCamera"
    
    # Set camera parameters based on the transform panel values
    cam.rotation_euler = Euler((math.radians(84.759), math.radians(0.000052), math.radians(-91.308)), 'XYZ')
    
    # Make this the active camera
    bpy.context.scene.camera = cam
    
    return cam

def setup_camera_and_light(focal_length=35.0):  # Default 35mm focal length
    if "Camera" not in bpy.data.objects:
        bpy.ops.object.camera_add()
    cam = bpy.data.objects["Camera"]
    cam.location = (-14, 0, 5)
    cam.rotation_euler = (
        math.radians(84),
        math.radians(0),
        math.radians(270)
    )
    
    # Set the focal length
    cam.data.lens = focal_length  # This is measured in millimeters
    
    # Optional: You can also set the sensor size if needed
    # cam.data.sensor_width = 36.0  # 35mm full-frame sensor width
    
    bpy.context.scene.camera = cam

    # Rest of your function remains the same...
    if "TeslaSun" not in bpy.data.objects:
        bpy.ops.object.light_add(type='SUN')
        sun = bpy.context.object
        sun.name = "TeslaSun"
    else:
        sun = bpy.data.objects["TeslaSun"]
    sun.location = (0, 0, 100)
    sun.data.energy = 10.0
    sun.data.angle = math.radians(1.0)

    bpy.context.scene.eevee.use_gtao = True
    return cam
# === MAIN ===

def set_sky_and_ground():
    # === Add a large ground plane ===
    bpy.ops.mesh.primitive_plane_add(size=500, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground_Plane"

    # === Assign a grey material to the ground ===
    mat_ground = bpy.data.materials.new(name="GroundMaterial")
    mat_ground.use_nodes = True
    bsdf = mat_ground.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.001, 0.001, 0.001, 1.0)  # Grey
    ground.data.materials.append(mat_ground)

    # === Set up sky background using World Shader Nodes ===
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True

    # Clear existing nodes
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    # === Create new nodes ===
    tex_coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    gradient = nodes.new("ShaderNodeTexGradient")
    color_ramp = nodes.new("ShaderNodeValToRGB")
    background = nodes.new("ShaderNodeBackground")
    output = nodes.new("ShaderNodeOutputWorld")

    # Set node positions (optional, for visual clarity)
    tex_coord.location = (-800, 0)
    mapping.location = (-600, 0)
    gradient.location = (-400, 0)
    color_ramp.location = (-200, 0)
    background.location = (0, 0)
    output.location = (200, 0)

    # === Configure mapping: rotate on Y to make gradient vertical ===
    mapping.inputs['Rotation'].default_value = (0, math.radians(90), 0)

    # === Configure color ramp ===
    color_ramp.color_ramp.elements[0].position = 0.0
    color_ramp.color_ramp.elements[0].color = (1.0, 0.6, 0.3, 1.0)  # Orange
    color_ramp.color_ramp.elements[1].position = 1.0
    color_ramp.color_ramp.elements[1].color = (0.3, 0.5, 0.8, 1.0)  # Blue

    # === Connect nodes ===
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], gradient.inputs['Vector'])
    links.new(gradient.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], background.inputs['Color'])
    links.new(background.outputs['Background'], output.inputs['Surface'])

    print("🌇 Gradient sky background set up (Blender 4.x compatible)")



def setup_environment_image(image_path, strength=1.0):
    """
    Set up a world background using an environment image and add a ground plane.

    Parameters:
        image_path (str): Absolute path to the environment image (HDRI or JPG).
        strength (float): Background strength (brightness).
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    # Get or create the world
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links

    # Clear existing nodes
    nodes.clear()

    # Create nodes
    env_tex = nodes.new(type="ShaderNodeTexEnvironment")
    background = nodes.new(type="ShaderNodeBackground")
    output = nodes.new(type="ShaderNodeOutputWorld")

    # Position nodes (optional for better layout)
    env_tex.location = (-300, 300)
    background.location = (0, 300)
    output.location = (300, 300)

    # Load image
    env_tex.image = bpy.data.images.load(image_path)

    # Set strength
    background.inputs["Strength"].default_value = strength

    # Connect nodes
    links.new(env_tex.outputs["Color"], background.inputs["Color"])
    links.new(background.outputs["Background"], output.inputs["Surface"])

    # Adjust viewport shading
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.use_scene_world = True

    print(f"Environment image loaded from {image_path}")

    # Add a ground plane
    # bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
    # plane = bpy.context.object
    # plane.name = "GroundPlane"

    # # Assign simple gray material
    # mat = bpy.data.materials.new(name="GroundMaterial")
    # mat.use_nodes = True
    # bsdf = mat.node_tree.nodes.get("Principled BSDF")
    # if bsdf:
    #     bsdf.inputs["Base Color"].default_value = (0.8, 0.8, 0.8, 1)
    # plane.data.materials.append(mat)

    return world




def setup_sky():
    """
    Set up a sky environment with a grey ground and sky blue sky.
    """


    # Get the world or create one if it doesn't exist
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    # Enable nodes for the world
    world.use_nodes = True

    # Clear existing nodes
    world.node_tree.nodes.clear()

    # Create the Sky Texture node
    sky_texture = world.node_tree.nodes.new(type="ShaderNodeTexSky")
    sky_texture.location = (-300, 300)

    # Create the Background node
    background = world.node_tree.nodes.new(type="ShaderNodeBackground")
    background.location = (0, 300)

    # Create the World Output node
    output = world.node_tree.nodes.new(type="ShaderNodeOutputWorld")
    output.location = (300, 300)

    # Connect the nodes
    world.node_tree.links.new(sky_texture.outputs["Color"], background.inputs["Color"])
    world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])

    # Configure the Sky Texture node
    sky_texture.sky_type = 'NISHITA'  # Most realistic sky
    sky_texture.sun_elevation = math.radians(90.0)  # Midday sun
    sky_texture.sun_rotation = math.radians(0.0)  # Default rotation
    sky_texture.turbidity = 0.0  # Clear sky (lower values = bluer sky)
    sky_texture.ground_albedo = 0.8  # Set ground reflectivity to 0 for grey ground
    
    # Disable sun disc to avoid conflict with your Tesla sun
    if hasattr(sky_texture, "sun_disc"):
        sky_texture.sun_disc = False

    # Set background strength
    background.inputs["Strength"].default_value = 0.05

    # Adjust viewport shading to show the world
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.use_scene_world = True

    print("Sky environment with grey ground and sky blue sky set up successfully.")
    return world








# Function to create video from rendered frames
def create_video():
    """Create a video from the rendered frames using Blender's video sequencer"""
    # Get the scene
    scene = bpy.context.scene
    
    # Set up the video sequence editor
    if not scene.sequence_editor:
        scene.sequence_editor_create()
    
    # Clear existing sequences
    if scene.sequence_editor.sequences:
        for seq in scene.sequence_editor.sequences:
            scene.sequence_editor.sequences.remove(seq)
    
    # Create image sequence
    frame_pattern = os.path.join(output_directory, "frame_*.jpg")
    strip = scene.sequence_editor.sequences.new_image(
        name="RenderedFrames",
        filepath=os.path.join(output_directory, "frame_0001.jpg"),  # First frame will be named with 4 digits
        channel=1,
        frame_start=1
    )
    
    # Find all images in the directory
    frames = sorted(glob.glob(frame_pattern))
    for i, f in enumerate(frames[1:], start=1):  # Skip the first one as it's already added
        strip.elements.append(f)
    
    # Set the end frame
    scene.frame_end = len(frames)
    
    # Configure render settings for video
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    scene.render.filepath = final_video_path
    
    # Render the video
    print(f"Rendering video to {final_video_path}...")
    bpy.ops.render.render(animation=True)
    
    print(f"Video created at {final_video_path}")

# Load JSON data
with open(json_file_path, 'r') as file:
    road_signs_data = json.load(file)

with open(vehicle_json_file_path, 'r') as file:
    vehicle_data = json.load(file)

with open(traffic_light_json_file_path, 'r') as file:
    traffic_light_data = json.load(file)

with open(road_objects_json_file_path, 'r') as file:
    road_objects_data = json.load(file)

with open(lane_json_file_path, 'r') as file:
    lane_data = json.load(file)

# Function to convert JSON coordinates to Blender coordinates
def convert_coordinates(x, y, z):
    # Apply scale
    x *= 1
    y *= 1
    z *= 1
    return x, y, z

# Function to extract frame number from frame name
def extract_frame_number(frame_name):
    try:
        return int(frame_name.split('_')[-1])
    except:
        return 0

# Function to import stop sign asset from blend file
def import_stop_sign_asset():
    # Get absolute path to the blend file
    filepath = os.path.abspath(stop_sign_blend_file)
    
    # Import objects from the blend file without linking to scene
    with bpy.data.libraries.load(filepath) as (data_from, data_to):
        # Get list of all objects in the blend file
        data_to.objects = [name for name in data_from.objects]
    
    # Find a suitable stop sign object from the imported objects
    stop_sign_object = None
    for obj in data_to.objects:
        if obj is not None:
            # Use the first valid object as our stop sign model template
            if stop_sign_object is None:
                stop_sign_object = obj
                break
    
    if stop_sign_object is None:
        raise Exception(f"No stop sign object found in {stop_sign_blend_file}")
    
    return stop_sign_object




def import_speed_bump_asset():
    # Get absolute path to the blend file
    filepath = os.path.abspath(speed_breaker_blend_file)
    
    # Import objects from the blend file without linking to scene
    with bpy.data.libraries.load(filepath) as (data_from, data_to):
        # Get list of all objects in the blend file
        data_to.objects = [name for name in data_from.objects]
    
    # Find a suitable stop sign object from the imported objects
    speed_bump_object = None
    for obj in data_to.objects:
        if obj is not None:
            # Use the first valid object as our stop sign model template
            if speed_bump_object is None:
                speed_bump_object = obj
                break
    
    if speed_bump_object is None:
        raise Exception(f"No stop sign object found in {stop_sign_blend_file}")
    
    return speed_bump_object







# Function to import speed limit sign asset from blend file
def import_speed_limit_sign_asset():
    # Get absolute path to the blend file
    filepath = os.path.abspath(speed_limit_sign_blend_file)
    
    # Import objects from the blend file without linking to scene
    with bpy.data.libraries.load(filepath) as (data_from, data_to):
        # Get list of all objects in the blend file
        data_to.objects = [name for name in data_from.objects]
    
    # Find a suitable speed limit sign object from the imported objects
    speed_limit_sign_object = None
    for obj in data_to.objects:
        if obj is not None:
            # Use the first valid object as our speed limit sign model template
            if speed_limit_sign_object is None:
                speed_limit_sign_object = obj
                break
    
    if speed_limit_sign_object is None:
        raise Exception(f"No speed limit sign object found in {speed_limit_sign_blend_file}")
    
    return speed_limit_sign_object

# Function to add text to speed limit sign
def add_speed_limit_text_to_sign(sign_obj, speed_value, x, y, z, collections):
    """
    Adds speed limit text to a specific sign object
    """
    # Create text object
    bpy.ops.object.text_add()
    text = bpy.context.object
    text.name = f"SpeedLimitText_{sign_obj.name}_{speed_value}"
    
    # Add text to the speed_signs collection
    collections["speed_signs"].objects.link(text)
    
    # (Rest of your existing code remains the same...)
    text.data.body = f"SPEED\nLIMIT\n{speed_value}"
    text.data.align_x = 'CENTER'
    text.data.align_y = 'CENTER'
    text.data.size = 0.15
    text.data.extrude = 0.005
    text.location = Vector((x-0.1, y, 1.8))
    text.rotation_euler = Euler((math.radians(90), 0, math.radians(270)), 'XYZ')
    
    # Material setup (unchanged)
    if 'BlackText' not in bpy.data.materials:
        mat = bpy.data.materials.new(name='BlackText')
        mat.diffuse_color = (0, 0, 0, 1)
    else:
        mat = bpy.data.materials['BlackText']
    
    if len(text.data.materials) == 0:
        text.data.materials.append(mat)
    else:
        text.data.materials[0] = mat
    
    return text
 
# Create a 2D arrow mesh
def create_arrow_mesh(name="MotionArrow"):
    """Create a simple 2D arrow mesh for motion indication"""
    # Define vertices for a simple arrow shape
    verts = [
        (0, 0.5, 0),       # 0: arrow tip
        (-0.25, -0.1, 0),  # 1: right wing
        (0, 0, 0),         # 2: center
        (0.25, -0.1, 0),   # 3: left wing
        (0.1, -0.1, 0),    # 4: right shaft corner
        (0.1, -0.5, 0),    # 5: right shaft end
        (-0.1, -0.5, 0),   # 6: left shaft end
        (-0.1, -0.1, 0)    # 7: left shaft corner
    ]
    
    # Define faces
    faces = [(0, 1, 2), (0, 2, 3), (2, 7, 4), (2, 6, 7), (7, 6, 5, 4)]
    
    # Create mesh
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    
    # Add vertices and faces to mesh
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    # Set up initial material
    mat = bpy.data.materials.new(name=f"{name}_Material")
    mat.diffuse_color = (*arrow_color, 1.0)
    obj.active_material = mat
    
    return obj

# Function to create a light indicator mesh
def create_light_indicator(name, light_type="brake"):
    """Create a simple light indicator mesh"""
    # Create a simple disk shape
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    
    # Create circle vertices
    verts = []
    edges = []
    faces = []
    
    # Center vertex
    verts.append((0, 0, 0))
    
    # Circle vertices
    segments = 12
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = math.cos(angle) * 0.5
        y = math.sin(angle) * 0.5
        verts.append((x, y, 0))
    
    # Create faces - connect each segment to center
    for i in range(1, segments + 1):
        next_i = 1 if i == segments else i + 1
        faces.append((0, i, next_i))
    
    # Add vertices and faces to mesh
    mesh.from_pydata(verts, edges, faces)
    mesh.update()
    
    # Create material with emission for the light
    mat = bpy.data.materials.new(name=f"{name}_Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    for node in nodes:
        nodes.remove(node)
    
    # Create emission and output nodes
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    emission_node = nodes.new(type='ShaderNodeEmission')
    
    # Set light color based on type
    if light_type == "brake":
        emission_node.inputs[0].default_value = brake_light_color
    elif light_type == "left_indicator":
        emission_node.inputs[0].default_value = left_indicator_color
    elif light_type == "right_indicator":
        emission_node.inputs[0].default_value = right_indicator_color
    
    # Set emission strength
    emission_node.inputs[1].default_value = light_emission_strength
    
    # Connect nodes
    links.new(emission_node.outputs[0], output_node.inputs[0])
    
    # Assign material to object
    obj.active_material = mat
    
    return obj




def get_vehicle_type(class_name, vehicle_type):
    class_name = class_name.lower()
    vehicle_type = vehicle_type.lower()
    
    if "truck" in class_name and "pickup truck" in vehicle_type:
        return "pickup_truck"
    elif "truck" in class_name:
        return "truck"
    elif "convertible" in class_name or "sedan" in vehicle_type:
        return "sedan"
    elif "suv" in class_name or "suv" in vehicle_type:
        return "suv"
    elif "motorcycle" in class_name or "bike" in vehicle_type:
        return "motorcycle"
    elif "bicycle" in class_name or "cycle" in vehicle_type:
        return "bicycle"
    elif "bus" in class_name:
        return "truck"  # Use truck for buses
    else:
        return "sedan"  # Default to sedan


# Function to import vehicles from the blend files
def import_vehicle_assets():
    vehicle_models = {}
    
    for model_type, blend_file in vehicle_blend_files.items():
        try:
            # Import objects from the blend file
            filepath = os.path.join(os.path.dirname(bpy.data.filepath), blend_file)
            with bpy.data.libraries.load(filepath) as (data_from, data_to):
                data_to.objects = data_from.objects
            
            # Store imported objects
            models = []
            for obj in data_to.objects:
                if obj is not None:
                    models.append(obj)
            
            if models:
                vehicle_models[model_type] = models
        except Exception as e:
            print(f"Error importing {model_type} models: {e}")
    
    return vehicle_models

# Function to import traffic light assets from blend files
def import_traffic_light_assets():
    imported_models = {}
    
    for color, blend_file in traffic_light_blend_files.items():
        # Get absolute path to the blend file
        filepath = os.path.abspath(blend_file)
        
        # Import objects from the blend file without linking to scene
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects]
        
        # Find traffic light model and sphere in the imported objects
        traffic_light_model = None
        sphere_model = None
        
        for obj in data_to.objects:
            if obj is not None:
                # Determine if object is likely a traffic light or sphere based on name
                if "sphere" in obj.name.lower():
                    sphere_model = obj
                else:
                    traffic_light_model = obj
        
        # Store the models for later use
        imported_models[color] = {
            "traffic_light": traffic_light_model,
            "sphere": sphere_model
        }
    
    # Import arrow model
    arrow_filepath = os.path.abspath(arrow_blend_file)
    arrow_model = None
    
    try:
        with bpy.data.libraries.load(arrow_filepath) as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects]
        
        for obj in data_to.objects:
            if obj is not None:
                # Find the arrow object (the first object in the file)
                arrow_model = obj
                print(f"Arrow model imported: {obj.name}")
                break
        
        if arrow_model is None:
            print("Warning: No arrow model found in the blend file.")
    except Exception as e:
        print(f"Error importing arrow model: {e}")
    
    # Store the arrow model
    imported_models["arrow"] = arrow_model
    
    return imported_models

# Function to import asset from blend file (for road objects)
def import_asset(blend_file_path):
    # Get absolute path to the blend file
    filepath = os.path.abspath(blend_file_path)
    
    # Import objects from the blend file without linking to scene
    with bpy.data.libraries.load(filepath) as (data_from, data_to):
        # Get list of all objects in the blend file
        data_to.objects = [name for name in data_from.objects]
    
    # Find a suitable object from the imported objects
    asset_object = None
    for obj in data_to.objects:
        if obj is not None:
            # Use the first valid object as our model template
            if asset_object is None:
                asset_object = obj
                break
    
    if asset_object is None:
        raise Exception(f"No object found in {blend_file_path}")
    
    return asset_object

# Function to load pedestrian OBJ files
def load_pedestrians(frame_number, human_pose_folder,ped_veh, position_offset=None, use_collection=True):
    """
    Load pedestrian OBJ files for a specific frame number.
    """
    # Format frame number with leading zeros (6 digits)
    frame_str = f"{frame_number:06d}"
    pose_pattern = os.path.join(human_pose_folder, f"frame_{frame_str}_person_*.obj")
    pose_objs = sorted(glob.glob(pose_pattern))
    
    if not pose_objs:
        print(f"No pedestrian models found for frame {frame_number} in {human_pose_folder}")
        return []
    
    # Create a collection for the pedestrians if needed
    pedestrian_collection = None
    collection_name = f"Pedestrians_Frame_{frame_str}"
    
    if use_collection:
        # Fix: Properly check if collection exists
        if collection_name in [coll.name for coll in bpy.data.collections]:
            pedestrian_collection = bpy.data.collections[collection_name]
        else:
            pedestrian_collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(pedestrian_collection)
    
    imported_pedestrians = []
    
    for idx, obj_path in enumerate(pose_objs):
        # Extract person ID from filename (for better naming)
        person_id = os.path.basename(obj_path).split("_person_")[1].split(".")[0]
        
        # Store current selection
        prev_selected = set(bpy.context.selected_objects)
        
        # Import OBJ file - use the appropriate import function for your Blender version
        # For Blender 4.0+:
        try:
            bpy.ops.wm.obj_import(filepath=obj_path)
        except AttributeError:
            # For older Blender versions:
            bpy.ops.import_scene.obj(filepath=obj_path)
        
        # Find newly imported objects
        imported = [o for o in bpy.context.selected_objects if o not in prev_selected and o.type == 'MESH']
        
        if imported:
            person_obj = imported[0]
            person_obj.name = f"Pedestrian_{frame_str}_{person_id}"
            
            # Apply rotation to correct orientation
            person_obj.rotation_euler[0] = math.radians(-90)  # flip upright
            person_obj.rotation_euler[1] = math.radians(0)    # face +X instead of +Y
            person_obj.rotation_euler[2] = math.radians(-90)  # face +Z instead of +Y
            
            # Apply position offset if provided
            if position_offset:
                # Calculate offset based on pedestrian index for better spacing
                x_offset = position_offset[0] + (idx * 1.5)  # Space pedestrians 1.5 units apart
                y_offset = position_offset[1]
                z_offset = position_offset[2]
                print('****************************************************************')
                print('ped_veh',ped_veh)
                if ped_veh == "motorcycle":
                    person_obj.location = (x_offset+7.0, y_offset+1.85, z_offset+1.2)
                elif ped_veh == "bicycle":
                    person_obj.location = (x_offset-8.2, y_offset-8.0+6.2+0.5, z_offset+1.15)
                else:
                    person_obj.location = (x_offset, y_offset-8.0, z_offset+0.85)
                
                #person_obj.location = (x_offset, y_offset-8.0, z_offset)
            
            # Add to collection if enabled
            if use_collection and pedestrian_collection:
                # Remove from current collections
                for coll in list(person_obj.users_collection):
                    coll.objects.unlink(person_obj)
                # Add to pedestrian collection
                pedestrian_collection.objects.link(person_obj)
            
            imported_pedestrians.append(person_obj)
            print(f"Imported pedestrian: {person_obj.name}")
        else:
            print(f"Failed to import pedestrian from {obj_path}")
    
    print(f"Loaded {len(imported_pedestrians)} pedestrians for frame {frame_number}")
    return imported_pedestrians

# Blender Utils class for lane rendering
class Blender_Utils:
    def __init__(self, collections):
        self.collections = collections
        
    def create_bezier_curve_from_points(self, points, name="Bezier_Curve"):
        # Implementation as provided
        curve_data = bpy.data.curves.new(name=name, type='CURVE')
        curve_data.dimensions = '3D'
        polyline = curve_data.splines.new('BEZIER')
        polyline.bezier_points.add(len(points)-1)
        for i, (x, y, z) in enumerate(points):
            polyline.bezier_points[i].co = (z, -x, 0)
            polyline.bezier_points[i].handle_left = (z, -x, 0)
            polyline.bezier_points[i].handle_right = (z, -x, 0)
        
        curve_object = bpy.data.objects.new(name=f"{name}_Object", object_data=curve_data)
        
        # Add to lane collection instead of context collection
        self.collections["lanes"].objects.link(curve_object)
        return curve_object

    def create_lane_markings_by_curve_length(self, curve_object, lane_width=4, lane_length=10, gap_length=1, num_lanes=10):
        # Create a cube for lane markings
        bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        lane_marking = bpy.context.object
        lane_marking.scale[1] = 0.1 * lane_width
        lane_marking.scale[0] = 0.1 * lane_length
        lane_marking.scale[2] = 0.05
        
        # Create white material for lane markings
        mat = bpy.data.materials.new(name="Lane_Material")
        mat.diffuse_color = lane_material_color
        lane_marking.active_material = mat
        
        # Add modifiers
        bpy.ops.object.modifier_add(type='ARRAY')
        lane_marking.modifiers["Array"].fit_type = 'FIT_CURVE'
        lane_marking.modifiers["Array"].curve = curve_object
        
        lane_marking.modifiers["Array"].use_constant_offset = True
        lane_marking.modifiers["Array"].constant_offset_displace[0] = gap_length
        bpy.ops.object.modifier_add(type='CURVE')
        lane_marking.modifiers["Curve"].object = curve_object
        
        lane_marking.modifiers["Curve"].deform_axis = 'POS_X'
        
        # Move to lane collection
        for coll in list(lane_marking.users_collection):
            coll.objects.unlink(lane_marking)
        self.collections["lanes"].objects.link(lane_marking)
        
        return lane_marking

# Function to render lanes for a specific frame
def render_lanes(frame_number, lane_data, collections):
    """
    Render lane markings for a specific frame from the lane data.
    """
    # Find the frame data
    try:
        frame_data = lane_data['frames'][frame_number]
    except (KeyError, IndexError):
        print(f"Error: Frame {frame_number} not found in lane data")
        return []

    # Create Blender_Utils instance with collections
    blend_obj_gen = Blender_Utils(collections)
    
    created_lanes = []
    
    # Iterate through each lane
    for lane in frame_data['lanes']:
        # Extract world points
        points = [(1.5 * point['x'], point['y'], 2 * point['z']) for point in lane['world_points']]
        
        if len(points) < 2:
            print(f"Skipping lane {lane['lane_id']} - not enough points")
            continue
        
        # Create Bezier curve
        curve_obj = blend_obj_gen.create_bezier_curve_from_points(points, name=f"Lane_{lane['lane_id']}")
        
        # Create lane markings based on lane type
        if lane['type'] == "solid-line":
            lane_marking = blend_obj_gen.create_lane_markings_by_curve_length(
                curve_obj, lane_width=1, lane_length=20, gap_length=0, num_lanes=15
            )
        else:
            lane_marking = blend_obj_gen.create_lane_markings_by_curve_length(
                curve_obj, lane_width=1, lane_length=20, gap_length=1, num_lanes=8
            )
        
        created_lanes.append((curve_obj, lane_marking))
        print(f"Created lane {lane['lane_id']} of type {lane['type']}")
    
    return created_lanes


def clip_orientation(angle_in_degrees):
    """
    Clips the angle to one of the four cardinal directions based on specified ranges.
    Returns the clipped angle in degrees.
    """
    # Normalize angle to range 0-360
    angle_normalized = angle_in_degrees % 360
    
    # Clip based on ranges
    if 45 <= angle_normalized < 135:
        return 90  # facing forward
    elif 135 <= angle_normalized < 215:
        return 180  # facing left
    elif 215 <= angle_normalized < 305:
        return 270  # facing backward
    else:  # angle between 305-360 or 0-45 (wrapping around 0)
        return 0  # facing right






# Function to parse the color field and check for arrow information
def parse_color_field(color_str):
    if not color_str or not isinstance(color_str, str):
        return color_str, None  # Return original color if it's not a string
    
    color_str = color_str.lower()
    
    if color_str.startswith("arrow:"):
        # Extract the base color (default to red) and arrow direction
        base_color = "red"  # Default color for arrows
        arrow_direction = color_str.split(":")[1]
        return base_color, arrow_direction
    else:
        # Regular color without arrow
        return color_str, None

# Function to create collections or retrieve them if they exist
def get_or_create_collections():
    collections = {}
    
    # Road sign collections
    if "StopSign_Instances" not in bpy.data.collections:
        collections["stop_signs"] = bpy.data.collections.new("StopSign_Instances")
        bpy.context.scene.collection.children.link(collections["stop_signs"])
    else:
        collections["stop_signs"] = bpy.data.collections["StopSign_Instances"]

    if "SpeedLimitSign_Instances" not in bpy.data.collections:
        collections["speed_signs"] = bpy.data.collections.new("SpeedLimitSign_Instances")
        bpy.context.scene.collection.children.link(collections["speed_signs"])
    else:
        collections["speed_signs"] = bpy.data.collections["SpeedLimitSign_Instances"]

    if "SpeedBump_Instances" not in bpy.data.collections:
        collections["speed_bump"] = bpy.data.collections.new("SpeedBump_Instances")
        bpy.context.scene.collection.children.link(collections["speed_bump"])
    else:
        collections["speed_bump"] = bpy.data.collections["SpeedBump_Instances"]



    # Vehicle collections
    if "Vehicle_Instances" not in bpy.data.collections:
        collections["vehicles"] = bpy.data.collections.new("Vehicle_Instances")
        bpy.context.scene.collection.children.link(collections["vehicles"])
    else:
        collections["vehicles"] = bpy.data.collections["Vehicle_Instances"]

    if "Motion_Arrows" not in bpy.data.collections:
        collections["arrows"] = bpy.data.collections.new("Motion_Arrows")
        bpy.context.scene.collection.children.link(collections["arrows"])
    else:
        collections["arrows"] = bpy.data.collections["Motion_Arrows"]

    if "Vehicle_Lights" not in bpy.data.collections:
        collections["lights"] = bpy.data.collections.new("Vehicle_Lights")
        bpy.context.scene.collection.children.link(collections["lights"])
    else:
        collections["lights"] = bpy.data.collections["Vehicle_Lights"]

    # Traffic light collection
    if "TrafficLight_Instances" not in bpy.data.collections:
        collections["traffic_lights"] = bpy.data.collections.new("TrafficLight_Instances")
        bpy.context.scene.collection.children.link(collections["traffic_lights"])
    else:
        collections["traffic_lights"] = bpy.data.collections["TrafficLight_Instances"]

    # Road objects collections
    if "TrashCan_Instances" not in bpy.data.collections:
        collections["trash_cans"] = bpy.data.collections.new("TrashCan_Instances")
        bpy.context.scene.collection.children.link(collections["trash_cans"])
    else:
        collections["trash_cans"] = bpy.data.collections["TrashCan_Instances"]

    if "TrafficCone_Instances" not in bpy.data.collections:
        collections["traffic_cones"] = bpy.data.collections.new("TrafficCone_Instances")
        bpy.context.scene.collection.children.link(collections["traffic_cones"])
    else:
        collections["traffic_cones"] = bpy.data.collections["TrafficCone_Instances"]

    # Lane collection
    if "Lane_Instances" not in bpy.data.collections:
        collections["lanes"] = bpy.data.collections.new("Lane_Instances")
        bpy.context.scene.collection.children.link(collections["lanes"])
    else:
        collections["lanes"] = bpy.data.collections["Lane_Instances"]
    
    return collections

# Function to clear all objects from a collection
# def clear_collection(collection):
#     if collection:
#         for obj in list(collection.objects):
#             bpy.data.objects.remove(obj, do_unlink=True)
def clear_collection(collection):
    if collection:
        objects_to_clear = list(collection.objects)
        for obj in objects_to_clear:
            if obj.type == 'FONT' and obj.data:
                text_data = obj.data
                bpy.data.objects.remove(obj, do_unlink=True)
                bpy.data.curves.remove(text_data, do_unlink=True)
            else:
                bpy.data.objects.remove(obj, do_unlink=True)        

# Function to clear all collections for a fresh render
def clear_all_collections(collections):
    for col in collections.values():
        clear_collection(col)
    
    # Also clear any existing pedestrian collections
    for collection in list(bpy.data.collections):
        if collection.name.startswith("Pedestrians_Frame_"):
            clear_collection(collection)
            # Optionally remove the entire collection
            bpy.data.collections.remove(collection)

# Main rendering function for a single frame
def render_frame(frame_number, collections, models):
    """Render a single frame with all objects"""
    print(f"\n--- Rendering frame {frame_number} ---")
    
    # Set the current Blender frame (for animation)
    bpy.context.scene.frame_set(frame_number)
    
    # Update the render output path for this frame
    bpy.context.scene.render.filepath = os.path.join(output_directory, f"frame_{frame_number:04d}")
    
    # Find the appropriate frame names in each dataset
    road_signs_frame_name = None
    vehicle_frame_name = None
    traffic_light_frame_name = None
    road_objects_frame_name = None
    
    # Road signs
    try:
        road_signs_frame_name = f"frame_{frame_number:06d}"
        if road_signs_frame_name not in road_signs_data:
            # Try without leading zeros
            road_signs_frame_name = f"frame_{frame_number}"
            if road_signs_frame_name not in road_signs_data:
                road_signs_frame_name = None
                print(f"Warning: No road signs data found for frame {frame_number}")
    except Exception as e:
        print(f"Error finding road signs frame: {e}")
    
    # Vehicles
    try:
        vehicle_frame_name = f"frame_{frame_number:06d}"
        if vehicle_frame_name not in vehicle_data:
            # Try without leading zeros
            vehicle_frame_name = f"frame_{frame_number}"
            if vehicle_frame_name not in vehicle_data:
                vehicle_frame_name = None
                print(f"Warning: No vehicle data found for frame {frame_number}")
    except Exception as e:
        print(f"Error finding vehicle frame: {e}")
    
    # Traffic lights
    try:
        traffic_light_frame_name = f"frame_{frame_number:06d}"
        if traffic_light_frame_name not in traffic_light_data:
            # Try without leading zeros
            traffic_light_frame_name = f"frame_{frame_number}"
            if traffic_light_frame_name not in traffic_light_data:
                traffic_light_frame_name = None
                print(f"Warning: No traffic light data found for frame {frame_number}")
    except Exception as e:
        print(f"Error finding traffic light frame: {e}")
    
    # Road objects
    try:
        road_objects_frame_name = f"frame_{frame_number:06d}"
        if road_objects_frame_name not in road_objects_data:
            # Try without leading zeros
            road_objects_frame_name = f"frame_{frame_number}"
            if road_objects_frame_name not in road_objects_data:
                road_objects_frame_name = None
                print(f"Warning: No road objects data found for frame {frame_number}")
    except Exception as e:
        print(f"Error finding road objects frame: {e}")
    
    # If no data is available for any object type, skip this frame
    if not any([road_signs_frame_name, vehicle_frame_name, traffic_light_frame_name, road_objects_frame_name]):
        print(f"Warning: No data found for frame {frame_number} in any dataset, skipping...")
        return False
    
    # Render road signs
    if road_signs_frame_name and road_signs_frame_name in road_signs_data:
        road_signs_frame_data = road_signs_data[road_signs_frame_name]
        
        # Process stop signs
        for i, stop_sign in enumerate(road_signs_frame_data.get("stop_signs", [])):
            pos = stop_sign.get("position_3d", {})
            x_orig = pos.get("x", 0)
            y_orig = pos.get("y", 0)
            z_orig = pos.get("z", 0)
            
            scaled_depth = z_orig*6 
            x3d = (x_orig - cx) * scaled_depth / fx
            y3d = (y_orig - cy) * scaled_depth / fy
            
            # Apply coordinate transformation
            x, y, z = convert_coordinates(1.1*scaled_depth-10.0, -1.1 * x3d+2.0, 0)
            
            confidence = stop_sign.get("confidence", 0)
            class_name = stop_sign.get("class_name", "stop_sign")
            
            # Create a new instance for each stop sign
            stop_sign_instance = models["stop_sign"].copy()
            stop_sign_instance.data = models["stop_sign"].data  # Share the mesh data
            stop_sign_instance.name = f"StopSign_{i}_{class_name}_conf_{confidence:.2f}"
            collections["stop_signs"].objects.link(stop_sign_instance)
            
            # Position the stop sign
            stop_sign_instance.location = Vector((x, y, z))
        
        # Process speed limit signs
        speed_signs_with_limit = 0
        for i, speed_sign in enumerate(road_signs_frame_data.get("speed_limit_signs", [])):
            pos = speed_sign.get("position_3d", {})
            x_orig = pos.get("x", 0)
            y_orig = pos.get("y", 0)
            z_orig = pos.get("z", 0)
            
            scaled_depth = z_orig*5
            x3d = (x_orig - cx) * scaled_depth / fx
            y3d = (y_orig - cy) * scaled_depth / fy
            
            # Apply coordinate transformation
            x, y, z = convert_coordinates(1.1*scaled_depth-10.0, -1.1 * x3d-1.0, 0)
            
            confidence = speed_sign.get("confidence", 0)
            
            # Get the detected speed limit if available
            detected_speed_limit = speed_sign.get("detected_speed_limit", None)
            detected_hump = speed_sign.get("detected_hump_sign", None)
            # Create a new instance for each speed limit sign
            speed_sign_instance = models["speed_limit_sign"].copy()
            speed_sign_instance.data = models["speed_limit_sign"].data  # Share the mesh data
            
            # Include speed limit in name if available
            if detected_speed_limit:
                speed_sign_instance.name = f"SpeedLimitSign_{i}_speed_{detected_speed_limit}_conf_{confidence:.2f}"
                speed_signs_with_limit += 1
                speed_sign_instance.location = Vector((x, y, z))
            else:
                speed_sign_instance.name = f"SpeedLimitSign_{i}_conf_{confidence:.2f}"
                speed_sign_instance.location = Vector((x-100, y, z))

            if detected_hump:
                speed_bump_instance = models["speed_bump_model"].copy()
                speed_bump_instance.data = models["speed_bump_model"].data
                speed_bump_instance.name = f"SpeedBump_{i}_conf_{confidence:.2f}"
                collections["speed_bump"].objects.link(speed_bump_instance)
                speed_bump_instance.location = Vector((x+30, 0, 0))

                
            collections["speed_signs"].objects.link(speed_sign_instance)
            
            # Position the speed limit sign
            
            
            # Add text with the speed limit only if detected_speed_limit exists
            if detected_speed_limit is not None:
                add_speed_limit_text_to_sign(speed_sign_instance, detected_speed_limit, x, y, z, collections)
        
        print(f"Created {len(road_signs_frame_data.get('stop_signs', []))} stop sign instances for frame {frame_number}")
        print(f"Created {len(road_signs_frame_data.get('speed_limit_signs', []))} speed limit sign instances for frame {frame_number}")
    
    # Render vehicles
    if vehicle_frame_name and vehicle_frame_name in vehicle_data:
        vehicle_frame_data = vehicle_data[vehicle_frame_name]
        
        # Create egocentric car at (0,0,0)
        if "sedan" in models["vehicles"]:
            egocentric_car = models["vehicles"]["sedan"][0].copy()
            egocentric_car.name = "Egocentric_Car"
            collections["vehicles"].objects.link(egocentric_car)
            egocentric_car.location = Vector((0, 0, 0))
        ped_veh = None
        # Process each vehicle
        for i, vehicle in enumerate(vehicle_frame_data.get("vehicles", [])):
            pos = vehicle.get("position_3d", {})
            x_orig = pos.get("x", 0)
            y_orig = pos.get("y", 0)
            z_orig = pos.get("z", 0)
            scaled_depth = z_orig*6
            x3d = (x_orig - cx) * scaled_depth / fx 
            y3d = (y_orig - cy) * scaled_depth / fy
            
            # Apply coordinate transformation
            x, y, z = convert_coordinates(scaled_depth+10.0, -1.5 * x3d, 0)
            
            confidence = vehicle.get("confidence", 0)
            class_name = vehicle.get("class_name", "unknown")
            vehicle_type_str = vehicle.get("vehicle_type", "sedan")
            
            # Get orientation data
            orientation_3d = vehicle.get("orientation_3d", {})
            rotation_y = orientation_3d.get("rotation_y", 0)
            
            #rotation_y = orientation_3d.get("rotation_y", 0)
    

            rotation_y_degrees = math.degrees(rotation_y)
            
            # Clip orientation to cardinal directions
            clipped_rotation_degrees = clip_orientation(rotation_y_degrees)
            print(f"Clipped rotation: {clipped_rotation_degrees} degrees")
            # Convert back to radians for Blender
            rotation_y = math.radians(clipped_rotation_degrees)





            # Determine vehicle type
            veh_type = get_vehicle_type(class_name, vehicle_type_str)
            
            # Select appropriate vehicle model
            if veh_type in models["vehicles"] and models["vehicles"][veh_type]:
                vehicle_model = models["vehicles"][veh_type][0]
            else:
                # Fallback to any available model
                fallback_type = next(iter(models["vehicles"]))
                vehicle_model = models["vehicles"][fallback_type][0]
            
            # Create a new instance for each vehicle
            car_instance = vehicle_model.copy()
            car_instance.name = f"Car_{i}_{class_name}_conf_{confidence:.2f}"
            collections["vehicles"].objects.link(car_instance)
            
            # Position the car
            #car_instance.location = Vector((x, y, z))

            if veh_type == 'bicycle':
                if frame_number == 2040:
                    car_instance.location = Vector((x-6.0, y, z+0.35))
                elif frame_number == 2050:
                    car_instance.location = Vector((x-17.0, y-5.2, z+0.35))

            elif veh_type == 'motorcycle' and frame_number==1150:

                car_instance.location = Vector((x+7.7, y+2, z))

            elif veh_type == 'pickup_truck':
                car_instance.location = Vector((x, y, z+1.0))
            # Position the car
            else:
                car_instance.location = Vector((x, y, z))


            
            # Apply orientation - Z rotation in Blender matches rotation_y in data
            if veh_type =='truck':
                car_instance.rotation_euler = Euler((0, 0, rotation_y), 'XYZ')
                # Store the adjusted rotation for light placement
                adjusted_rotation_y = rotation_y + 1.57
            elif veh_type == 'suv' :
                car_instance.rotation_euler = Euler((0, 0, rotation_y), 'XYZ')
                adjusted_rotation_y = rotation_y + 3.14
            elif veh_type == 'pickup_truck':
                car_instance.rotation_euler = Euler((1.57, 0, rotation_y), 'XYZ')
                adjusted_rotation_y = rotation_y + 1.57
            elif veh_type =='motorcycle':
                car_instance.rotation_euler = Euler((1.57, 0, 0), 'XYZ')
                adjusted_rotation_y = rotation_y + 3.14
            elif veh_type == 'bicycle':
                car_instance.rotation_euler = Euler((1.57, math.radians(0), math.radians(210)), 'XYZ')
                adjusted_rotation_y = rotation_y + 3.14
            else:
                car_instance.rotation_euler = Euler((0, 0, rotation_y+3.14), 'XYZ')
                adjusted_rotation_y = rotation_y + 3.14
                    
            if veh_type == 'bicycle':
                ped_veh = 'bicycle'
                a=1
            elif veh_type == 'motorcycle':
                ped_veh = 'motorcycle'
                a=2


            # Check if vehicle has motion data and is moving
            motion_data = vehicle.get("motion", {})
            is_moving = motion_data.get("is_moving", False)
            
            if is_moving:
                # Create arrow for motion indication
                arrow = create_arrow_mesh(f"Arrow_{i}")
                collections["arrows"].objects.link(arrow)
                
                # Get motion direction
                flow_direction_angle = motion_data.get("flow_direction_angle", 0)
                # Convert from degrees to radians for Blender
                flow_direction_rad = math.radians(flow_direction_angle)
                
                # Position arrow above the vehicle
                # Get dimensions to properly place arrow on top
                dimensions = car_instance.dimensions
                max_dim = max(dimensions.x, dimensions.y)
                arrow.location = Vector((x, y, z + dimensions.z/2 + arrow_height))
                
                # Scale the arrow
                arrow.scale = Vector((arrow_size * max_dim, arrow_size * max_dim, arrow_size * max_dim))
                
                # Rotate arrow to match flow direction (rotate around Z axis in Blender)
                # The +90 degrees is to align arrow forward direction with the angle reference
                #arrow.rotation_euler = Euler((0, 0, flow_direction_rad - math.radians(90)), 'XYZ')
                if veh_type == 'suv':
                    arrow.rotation_euler = Euler((0, 0, rotation_y), 'XYZ')
                elif veh_type == 'sedan':
                    arrow.rotation_euler = Euler((0, 0, rotation_y), 'XYZ')
                elif veh_type == 'truck':
                    arrow.rotation_euler = Euler((0, 0, rotation_y), 'XYZ')
                elif veh_type == 'pickup_truck':
                    arrow.rotation_euler = Euler((0, 0, rotation_y+1.57), 'XYZ')
                elif veh_type == 'motorcycle':
                    arrow.rotation_euler = Euler((0, 0, rotation_y-1.57), 'XYZ')
                else:
                    arrow.rotation_euler = Euler((0, 0, rotation_y), 'XYZ')


            
            # Add vehicle lights based on the light status in JSON
            lights_data = vehicle.get("lights", {})
            
            # Get dimensions for light positioning
            dimensions = car_instance.dimensions
            max_dim = max(dimensions.x, dimensions.y)
            
            # Get vehicle-specific offsets or use default values
            offsets = light_offset_settings.get(veh_type, {
                "rear_offset": 0.45, 
                "side_offset": 0.4, 
                "height_offset": 0.3, 
                "scale_factor": 1.0
            })
            
            # 1. Add brake lights if active
            brake_light_status = lights_data.get("brake_light", {}).get("status", False)
            if brake_light_status:
                # Create left brake light
                left_brake_light = create_light_indicator(f"LeftBrakeLight_{i}", "brake")
                collections["lights"].objects.link(left_brake_light)
                
                # Create right brake light
                right_brake_light = create_light_indicator(f"RightBrakeLight_{i}", "brake")
                collections["lights"].objects.link(right_brake_light)
                top_brake_light = create_light_indicator(f"TopBrakeLight_{i}", "brake")
                collections["lights"].objects.link(top_brake_light)
                # Get offset parameters
                rear_offset = offsets["rear_offset"]
                side_offset = offsets["side_offset"] * 0.6  # Use a smaller side offset than for turn signals
                height_offset = offsets["height_offset"]
                
                # Position the left brake light at the left rear of the vehicle
                # left_brake_light.location = Vector((
                #     x - math.sin(adjusted_rotation_y) * dimensions.y * rear_offset+0.1,
                #     y - math.cos(adjusted_rotation_y) * dimensions.y * rear_offset+0.4,
                #     z + dimensions.z * height_offset
                # ))
                
                # # Position the right brake light at the right rear of the vehicle
                # right_brake_light.location = Vector((
                #     x - math.sin(adjusted_rotation_y) * dimensions.y * rear_offset+0.1,
                #     y - math.cos(adjusted_rotation_y) * dimensions.y * rear_offset-0.8,
                #     z + dimensions.z * height_offset
                # ))



                if veh_type == 'suv' and adjusted_rotation_y==7.85238898038469:
                # Position the left brake light at the left rear of the vehicle

                    left_brake_light.location = Vector((
                        x-2.35 ,
                        y +0.65,
                        z +0.9
                    ))
                    
                    # Position the right brake light at the right rear of the vehicle
                    right_brake_light.location = Vector((
                        x -2.35,
                        y -0.65,
                        z +0.9
                    ))

                    top_brake_light.location = Vector((
                        x -2.2,
                        y ,
                        z +1.7
                    ))
                elif veh_type == 'sedan' :   
                    
                    left_brake_light.location = Vector((
                        x -2.35,
                        y +0.65,
                        z +0.9
                    ))  
                    right_brake_light.location = Vector((   
                        x -2.35,
                        y -0.65,
                        z +0.9
                    ))
                    top_brake_light.location = Vector((     
                        x -2.2,
                        y ,
                        z +1.4
                    ))
                else:
                    left_brake_light.location = Vector((
                        -30 ,
                        y +0.65,
                        z +0.9
                    ))
                    
                    # Position the right brake light at the right rear of the vehicle
                    right_brake_light.location = Vector((
                        -30,
                        y -0.65,
                        z +0.9
                    ))

                    top_brake_light.location = Vector((
                        -30,
                        y ,
                        z +1.7
                    ))









                
                # Scale the lights based on vehicle dimensions
                light_factor = offsets["scale_factor"]
                
                # Apply scale and rotation to left brake light
                left_brake_light.scale = Vector((
                    light_scale * max_dim * light_factor,
                    light_scale * max_dim * light_factor,
                    light_scale * max_dim * light_factor
                ))
                left_brake_light.rotation_euler = Euler((math.pi/2, 0, adjusted_rotation_y + math.pi), 'XYZ')
                
                # Apply scale and rotation to right brake light
                right_brake_light.scale = Vector((
                    light_scale * max_dim * light_factor,
                    light_scale * max_dim * light_factor,
                    light_scale * max_dim * light_factor
                ))
                right_brake_light.rotation_euler = Euler((math.pi/2, 0, adjusted_rotation_y + math.pi), 'XYZ')

                top_brake_light.scale = Vector((
                light_scale * max_dim * light_factor,
                light_scale * max_dim * light_factor,
                light_scale * max_dim * light_factor
                ))
                top_brake_light.rotation_euler = Euler((math.pi/2, 0, adjusted_rotation_y + math.pi), 'XYZ')
            # 2. Add left indicator if active
            left_indicator_status = lights_data.get("left_indicator", {}).get("status", False)
            if left_indicator_status:
                left_indicator = create_light_indicator(f"LeftIndicator_{i}", "left_indicator")
                collections["lights"].objects.link(left_indicator)
                
                # Get offset parameters
                rear_offset = offsets["rear_offset"]
                side_offset = offsets["side_offset"]
                height_offset = offsets["height_offset"]
                
                # Position the left indicator at the left rear of the vehicle
                left_indicator.location = Vector((
                    x - math.sin(adjusted_rotation_y) * dimensions.y * rear_offset+0.1,
                    y - math.cos(adjusted_rotation_y) * dimensions.y * rear_offset+0.4,
                    z + dimensions.z * height_offset
                ))

                if veh_type == "suv":
                    left_indicator.location = Vector((
                        x - 2.35,
                        y + 0.65,
                        z + 0.8
                    ))
                elif veh_type == "sedan":
                    left_indicator.location = Vector((
                        x - 2.40,
                        y + 0.65,
                        z + 0.8
                    ))
                else:
                    left_indicator.location = Vector((
                        -30,
                        y - 0.65,
                        z + 0.8
                    ))

                
                # Scale the light based on vehicle dimensions
                light_factor = offsets["scale_factor"]
                left_indicator.scale = Vector((
                    light_scale * max_dim * light_factor,
                    light_scale * max_dim * light_factor,
                    light_scale * max_dim * light_factor
                ))
                
                # Orient the light
                left_indicator.rotation_euler = Euler((math.pi/2, 0, adjusted_rotation_y + math.pi), 'XYZ')
            
            # 3. Add right indicator if active
            right_indicator_status = lights_data.get("right_indicator", {}).get("status", False)
            if right_indicator_status:
                right_indicator = create_light_indicator(f"RightIndicator_{i}", "right_indicator")
                collections["lights"].objects.link(right_indicator)
                
                # Get offset parameters
                rear_offset = offsets["rear_offset"]
                side_offset = offsets["side_offset"]
                height_offset = offsets["height_offset"]
                
                # Position the right indicator at the right rear of the vehicle
                # right_indicator.location = Vector((
                #     x - math.sin(adjusted_rotation_y) * dimensions.y * rear_offset+0.1,
                #     y - math.cos(adjusted_rotation_y) * dimensions.y * rear_offset-0.8,
                #     z + dimensions.z * height_offset
                # ))

                if veh_type == "suv":
                    right_indicator.location = Vector((
                        x - 2.35,
                        y - 0.65,
                        z + 0.8
                    ))

                elif veh_type == "sedan":
                    right_indicator.location = Vector((
                        x - 2.4,
                        y - 0.65,
                        z + 0.8
                    ))

                else:
                    right_indicator.location = Vector((
                        -30,
                        y + 0.65,
                        z + 0.8
                    ))
                
                # Scale the light based on vehicle dimensions
                light_factor = offsets["scale_factor"]
                right_indicator.scale = Vector((
                    light_scale * max_dim * light_factor,
                    light_scale * max_dim * light_factor,
                    light_scale * max_dim * light_factor
                ))
                
                # Orient the light
                right_indicator.rotation_euler = Euler((math.pi/2, 0, adjusted_rotation_y + math.pi), 'XYZ')
        
        print(f"Created {len(vehicle_frame_data.get('vehicles', []))} vehicles for frame {frame_number}")
    
    # Render traffic lights
    if traffic_light_frame_name and traffic_light_frame_name in traffic_light_data:
        traffic_light_frame_data = traffic_light_data[traffic_light_frame_name]
        
        # Process each traffic light
        for i, traffic_light in enumerate(traffic_light_frame_data.get("traffic_lights", [])):
            pos = traffic_light.get("position_3d", {})
            x_orig = pos.get("x", 0)
            y_orig = pos.get("y", 0)
            z_orig = pos.get("z", 0)
            scaled_depth = z_orig*5 
            x3d = (x_orig - cx) * scaled_depth / fx 
            y3d = (y_orig - cy) * scaled_depth / fy
            
            # Apply coordinate transformation
            x, y, z = convert_coordinates(1.1*scaled_depth, 1.1 * x3d, 0)
            
            # Get traffic light color and check for arrow
            color_str = traffic_light.get("color", "green")
            base_color, arrow_direction = parse_color_field(color_str)
            confidence = traffic_light.get("confidence", 0)
            
            # Use default color if not found in imported models
            if base_color not in models["traffic_lights"]:
                print(f"Warning: Color '{base_color}' not found in imported models, using green")
                base_color = "green"
            
            # Get the models for this color
            traffic_light_model = models["traffic_lights"][base_color]["traffic_light"]
            sphere_model = models["traffic_lights"][base_color]["sphere"]
            
            # Create a unique traffic light instance
            instance_name = f"TrafficLight_{i}_{base_color}_{confidence:.2f}"
            
            # Create a traffic light instance
            if traffic_light_model:
                tl_instance = traffic_light_model.copy()
                tl_instance.data = traffic_light_model.data  # Share the mesh data
                tl_instance.name = instance_name
                collections["traffic_lights"].objects.link(tl_instance)
                
                # Position the traffic light (at 5m height)
                tl_instance.location = Vector((x, y, z + 5.0))
                # Rotate 180 degrees around z-axis to face the camera
                tl_instance.rotation_euler = Euler((math.radians(90), 0, math.radians(180)), 'XYZ')
            
            # Create a sphere instance
            if sphere_model:
                sphere_instance = sphere_model.copy()
                sphere_instance.data = sphere_model.data
                sphere_instance.name = f"Light_{instance_name}"
                collections["traffic_lights"].objects.link(sphere_instance)
                
                # Get height offset based on color
                height_offset = sphere_heights.get(base_color, 10)  # Default if color not found
                
                # Position the sphere at the correct height based on color
                sphere_instance.location = Vector((x-0.15, y+0.05, z + height_offset))
            
            # Add arrow if needed
            if arrow_direction and "arrow" in models["traffic_lights"]:
                arrow_model = models["traffic_lights"]["arrow"]
                if arrow_model and arrow_direction in arrow_rotations:
                    arrow_instance = arrow_model.copy()
                    arrow_instance.name = f"Arrow_{instance_name}_{arrow_direction}"
                    collections["traffic_lights"].objects.link(arrow_instance)
                    
                    # Position the arrow on top of the traffic light
                    arrow_instance.location = Vector((x, y, z + 5.0 + arrow_height_offset))
                    
                    # Apply the rotation based on arrow direction
                    direction_rotation = arrow_rotations[arrow_direction]
                    arrow_instance.rotation_euler = Euler(
                        (direction_rotation.x, direction_rotation.y, direction_rotation.z),
                        'XYZ'
                    )


                    mat_name = "GreenArrowMaterial"
                    if mat_name not in bpy.data.materials:
                        green_material = bpy.data.materials.new(name=mat_name)
                        
                        # Set basic diffuse color to green
                        green_material.diffuse_color = (0.0, 1.0, 0.0, 1.0)  # RGBA: Green with full opacity
                        
                        # Add emission for a glowing effect
                        green_material.use_nodes = True
                        nodes = green_material.node_tree.nodes
                        links = green_material.node_tree.links
                        
                        # Clear existing nodes
                        for node in nodes:
                            nodes.remove(node)
                        
                        # Create emission node for glow
                        emission = nodes.new(type='ShaderNodeEmission')
                        emission.inputs[0].default_value = (0.0, 1.0, 0.0, 1.0)  # Green
                        emission.inputs[1].default_value = 2.0  # Emission strength
                        
                        # Create output node
                        output = nodes.new(type='ShaderNodeOutputMaterial')
                        
                        # Connect nodes
                        links.new(emission.outputs[0], output.inputs[0])
                    else:
                        green_material = bpy.data.materials[mat_name]
                    
                    # Apply material to the arrow
                    if len(arrow_instance.data.materials) > 0:
                        # Replace existing material
                        arrow_instance.data.materials[0] = green_material
                    else:
                        # Add new material if none exists
                        arrow_instance.data.materials.append(green_material)






                    # Make sure arrow is visible
                    arrow_instance.hide_viewport = False
                    arrow_instance.hide_render = False
        
        print(f"Created {len(traffic_light_frame_data.get('traffic_lights', []))} traffic lights for frame {frame_number}")
    
    # Render road objects
    if road_objects_frame_name and road_objects_frame_name in road_objects_data:
        road_objects_frame_data = road_objects_data[road_objects_frame_name]
        
        # Process each trash can
        for i, trash_can in enumerate(road_objects_frame_data.get("dustbins", [])):
            pos = trash_can.get("position_3d", {})
            x_orig = pos.get("x", 0)
            y_orig = pos.get("y", 0)
            z_orig = pos.get("z", 0)
            
            # Apply camera transformation 
            scaled_depth = z_orig*5
            x3d = (x_orig - cx) * scaled_depth / fx
            y3d = (y_orig - cy) * scaled_depth / fy
            
            # Convert to Blender coordinates - similar to stop sign script, adding the offset
            x, y, z = convert_coordinates(1.1*scaled_depth+10.0, -1.5 * x3d, 0)
            
            confidence = trash_can.get("confidence", 0)
            class_name = trash_can.get("class_name", "trash_can")
            
            # Create a new instance for each trash can
            trash_can_instance = models["trash_can"].copy()
            trash_can_instance.data = models["trash_can"].data  # Share the mesh data
            trash_can_instance.name = f"TrashCan_{i}_{class_name}_conf_{confidence:.2f}"
            collections["trash_cans"].objects.link(trash_can_instance)
            
            # Position the trash can
            trash_can_instance.location = Vector((x, y, z))
        
        # Process each traffic cone
        for i, traffic_cone in enumerate(road_objects_frame_data.get("traffic_cones", [])):
            pos = traffic_cone.get("position_3d", {})
            x_orig = pos.get("x", 0)
            y_orig = pos.get("y", 0)
            z_orig = pos.get("z", 0)
            
            # Apply camera transformation
            scaled_depth = z_orig*5
            x3d = (x_orig - cx) * scaled_depth / fx
            y3d = (y_orig - cy) * scaled_depth / fy
            
            # Convert to Blender coordinates
            x, y, z = convert_coordinates(1.1*scaled_depth+5.0, -0.2 * x3d+4, 0)
            
            confidence = traffic_cone.get("confidence", 0)
            class_name = traffic_cone.get("class_name", "traffic_cone")
            
            # Create a new instance for each traffic cone
            traffic_cone_instance = models["traffic_cone"].copy()
            traffic_cone_instance.data = models["traffic_cone"].data  # Share the mesh data
            traffic_cone_instance.name = f"TrafficCone_{i}_{class_name}_conf_{confidence:.2f}"
            collections["traffic_cones"].objects.link(traffic_cone_instance)
            
            # Position the traffic cone
            traffic_cone_instance.location = Vector((x, y, z))
        
        # Process each traffic cylinder
        for i, traffic_cylinder in enumerate(road_objects_frame_data.get("traffic_cylinders", [])):
            pos = traffic_cylinder.get("position_3d", {})
            x_orig = pos.get("x", 0)
            y_orig = pos.get("y", 0)
            z_orig = pos.get("z", 0)
            
            # Apply camera transformation
            scaled_depth = z_orig*5
            x3d = (x_orig - cx) * scaled_depth / fx
            y3d = (y_orig - cy) * scaled_depth / fy
            
            # Convert to Blender coordinates
            x, y, z = convert_coordinates(1.1*scaled_depth+10.0, -1.5 * x3d, 0)
            
            confidence = traffic_cylinder.get("confidence", 0)
            class_name = traffic_cylinder.get("class_name", "traffic_cylinder")
            
            # Create a new instance for each traffic cylinder (using traffic cone model)
            traffic_cone_instance = models["traffic_cone"].copy()
            traffic_cone_instance.data = models["traffic_cone"].data  # Share the mesh data
            traffic_cone_instance.name = f"TrafficCylinder_{i}_{class_name}_conf_{confidence:.2f}"
            collections["traffic_cones"].objects.link(traffic_cone_instance)
            
            # Position the traffic cylinder/cone
            traffic_cone_instance.location = Vector((x, y, z))
        
        print(f"Created road objects for frame {frame_number}")

    # Render pedestrians
    pedestrians = load_pedestrians(
        frame_number=frame_number,
        human_pose_folder=human_pose_folder,ped_veh=ped_veh,
        position_offset=pedestrian_position_offset
    )
    
    print(f"Loaded {len(pedestrians)} pedestrians for frame {frame_number}")
    
    # Render lanes
    created_lanes = render_lanes(
        frame_number=frame_number,
        lane_data=lane_data,
        collections=collections  # Pass collections to render_lanes
    )
    
    print(f"Created {len(created_lanes)} lane instances for frame {frame_number}")
    
    # Render the frame
    print(f"Rendering frame {frame_number}...")
    bpy.ops.render.render(write_still=True)
    
    return True

# Main function to run the entire rendering process
def main():
    """Run the complete rendering process with setup and cleanup"""
    # Set up render settings
    setup_render_settings()
    
    # Set up camera for the scene
    camera = setup_camera_and_light()
    setup_sky()

    set_sky_and_ground()
    # setup_realistic_background()
    image_path = "/home/neel/Desktop/cv_1/Einstein Vision/blender_assets/day1.png"
    setup_environment_image(image_path, strength=0.9)
    # Get or create collections for organization
    collections = get_or_create_collections()
    
    # Import all model assets
    models = {}
    
    # Road sign models
    models["stop_sign"] = import_stop_sign_asset()
    print(f"Imported stop sign model: {models['stop_sign'].name}")
    models["speed_bump_model"] = import_speed_bump_asset()
    #print(f"Imported stop sign model: {models["speed_bump_model"].name}")
    try:
        models["speed_limit_sign"] = import_speed_limit_sign_asset()
        print(f"Imported speed limit sign model: {models['speed_limit_sign'].name}")
    except Exception as e:
        print(f"Warning: {e}")
        print("Creating a placeholder for speed limit sign")
        
        # Create a placeholder speed limit sign (simple cube)
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        models["speed_limit_sign"] = bpy.context.active_object
        models["speed_limit_sign"].name = "SpeedLimitSign_Placeholder"
        models["speed_limit_sign"].scale = (0.5, 0.05, 0.7)  # Make it sign-shaped
        
        # Create a material for the sign
        mat = bpy.data.materials.new(name="SpeedLimitMaterial")
        mat.diffuse_color = (1, 1, 1, 1)  # White
        
        if models["speed_limit_sign"].data.materials:
            models["speed_limit_sign"].data.materials[0] = mat
        else:
            models["speed_limit_sign"].data.materials.append(mat)
        
        # Hide it from the scene (will be used as template)
        models["speed_limit_sign"].hide_viewport = True
        models["speed_limit_sign"].hide_render = True
    
    # Vehicle models
    models["vehicles"] = import_vehicle_assets()
    if not models["vehicles"]:
        print(f"Warning: No vehicle models found in the blend files")
    
    # Traffic light models
    models["traffic_lights"] = import_traffic_light_assets()
    print(f"Imported traffic light models for colors: {', '.join([k for k in models['traffic_lights'].keys() if k != 'arrow'])}")
    
    # Road object models
    try:
        models["trash_can"] = import_asset(trash_can_blend_file)
        print(f"Imported trash can model: {models['trash_can'].name}")
        
        models["traffic_cone"] = import_asset(traffic_cone_blend_file)
        print(f"Imported traffic cone model: {models['traffic_cone'].name}")
    except Exception as e:
        print(f"Error importing road object models: {e}")
        # If traffic cone model fails, create a placeholder
        if 'traffic_cone' not in models:
            bpy.ops.mesh.primitive_cone_add(radius1=0.5, radius2=0, depth=1)
            models["traffic_cone"] = bpy.context.active_object
            models["traffic_cone"].name = "PlaceholderTrafficCone"
            print(f"Created placeholder traffic cone model: {models['traffic_cone'].name}")
    
    # Determine range of frames to render
    end_frame = min(max_frames, 2140)  # Cap at 2150 as per requirements
    
    # Calculate frames to render (every 10th frame starting at 10)
    frames_to_render = list(range(start_frame, end_frame + 1, frame_interval))
    
    # Track successfully rendered frames
    successful_frames = []
    
    # Render each frame
    for frame_num in frames_to_render:
        # Clear all collections before rendering a new frame
        clear_all_collections(collections)
        
        # Render the frame
        success = render_frame(frame_num, collections, models)
        if success:
            successful_frames.append(frame_num)
    
    print(f"\nRendering complete! Rendered {len(successful_frames)} frames out of {len(frames_to_render)} requested.")
    
    # If frames were successfully rendered, create a video
    # if successful_frames:
    #     create_video()
    # else:
    #     print("No frames were successfully rendered. Cannot create video.")

# Run the main function when the script is executed
if __name__ == "__main__" or not bpy.context.window:  # Check for headless mode
    main()

# Instructions for headless execution
"""
To run this script in headless mode, use the following command:

blender -b -P render_scenes.py

where "render_scenes.py" is the filename of this script.

Additional options:
- To set a custom output directory: 
  blender -b -P render_scenes.py -- --output-dir /path/to/output
  
- To run with GPU acceleration (if available):
  blender -b -P render_scenes.py --enable-gpu-acceleration
  
- For full background processing (no status updates):
  blender -b -P render_scenes.py --background

For complete documentation, see https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html
"""
