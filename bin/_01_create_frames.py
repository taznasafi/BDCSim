from BDCSim import BDCSim, os
import my_paths

def create_frame(run=False, base_frames= False, bbox_type=False):

    framer = BDCSim.Simulator()
    framer.in_gdb_path = my_paths.XY_tests
    framer.output_folder = framer.base_output_folder
    framer.out_gdb_name = "_01_frame_bbox"
    framer.out_gdb = os.path.join(framer.output_folder, framer.out_gdb_name+".gdb")
    framer.create_gdb()

    if run:
        if base_frames:
            framer.create_data_frames_using_points()
        if bbox_type:
            framer.create_data_frames_using_bbox(bounding_box=bbox_type)
