from bin import _01_create_frames, _02_create_report




if __name__=="__main__":
    #Create Frames based on Bounding Box Types
    _01_create_frames.create_frame(run=True, base_frames=True)
    _01_create_frames.create_frame(run=True, bbox_type="CONVEX_HULL")
    _01_create_frames.create_frame(run=True, bbox_type="CIRCLE")
    _01_create_frames.create_frame(run=True, bbox_type="ENVELOPE")
    _01_create_frames.create_frame(run=True, bbox_type="RECTANGLE_BY_AREA")
    _01_create_frames.create_frame(run=True, bbox_type="RECTANGLE_BY_WIDTH")

    _02_create_report.create_report(run=True)