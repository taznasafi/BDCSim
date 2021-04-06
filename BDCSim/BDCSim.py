
import arcpy
import os
import my_paths
from collections import defaultdict
import BDCSim.__init__ as int_paths
from BDCSim import logger, get_path
import pandas as pd
from functools import reduce


class Simulator:
    base_input_folder, base_output_folder = int_paths.input_path, int_paths.output_path
    gdb_output_dic = defaultdict(list)
    arcpy.env.overwriteOutput = True
    def __init__(self, in_gdb_path=None, in_gdb_2_path=None, in_path=None,
                 output_folder=None, generic_out_path=None,
                 out_gdb_name=None, out_gdb=None):
        self.in_gdb_path = in_gdb_path
        self.in_gdb_2_path = in_gdb_2_path
        self.in_path = in_path
        self.output_folder = output_folder
        self.generic_out_path = generic_out_path
        self.out_gdb_name = out_gdb_name
        self.out_gdb = out_gdb

    def create_gdb(self):
        """
        creates ESRI GDB, given that you have provided Class properties correctly.
        """

        if not arcpy.Exists(self.out_gdb):

            arcpy.CreateFileGDB_management(out_folder_path=self.output_folder, out_name=self.out_gdb_name)
            # print(arcpy.GetMessages(0))
        else:
            print("GDB Exists: {}.gdb".format(self.out_gdb_name))


    def create_data_frames_using_points(self):


        fc_list = get_path.pathFinder(env=self.in_gdb_path).get_file_path_with_wildcard_from_gdb(wildcard="XY*Data", type="Point")

        arcpy.MakeFeatureLayer_management(in_features=my_paths.block_groups, out_layer="block_groups")

        for fc in fc_list:
            print(fc)

            fc_df = get_path.pathFinder.fc_2_df(fc)
            fc_df_grouped = fc_df.groupby(['provider_id','test_route']).count().reset_index()


            selected_df_list = []

            for pid, route in zip(list(fc_df_grouped['provider_id']), list(fc_df_grouped['test_route'])):


                # select provider and route
                # select the block groups and output csv

                print(pid, route)


                arcpy.MakeFeatureLayer_management(in_features=fc, out_layer="in_memory/temp_points_selections", where_clause=""" "provider_id" = {} and "test_route" = '{}'  """.format(pid, route))


                arcpy.SelectLayerByLocation_management(in_layer='block_groups',
                                                       overlap_type="INTERSECT",
                                                       select_features="in_memory/temp_points_selections")

                temp_frames = get_path.pathFinder.fc_2_df('block_groups')
                temp_frames['pid'] = pid
                temp_frames['route'] = route
                selected_df_list.append(temp_frames)


                arcpy.Delete_management("in_memory/temp_points_selections")

            if len(selected_df_list)>0:
                master_df = pd.concat(selected_df_list)

                csv_output = os.path.join(self.output_folder,"csv", "Frames_selected_cbg_by_base_speed_tests.csv")

                arcpy.Delete_management("block_groups")

                master_df.to_csv(csv_output)


    def create_data_frames_using_bbox(self, bounding_box):


        fc_list = get_path.pathFinder(env=self.in_gdb_path).get_file_path_with_wildcard_from_gdb(wildcard="XY*Data", type="Point")

        arcpy.MakeFeatureLayer_management(in_features=my_paths.block_groups, out_layer="block_groups")

        for fc in fc_list:
            print(fc)

            fc_df = get_path.pathFinder.fc_2_df(fc)
            fc_df_grouped = fc_df.groupby(['provider_id','test_route']).count().reset_index()


            selected_df_list = []

            for pid, route in zip(list(fc_df_grouped['provider_id']), list(fc_df_grouped['test_route'])):


                # select provider and route
                # create bounding box in memory
                # use the bounding box from memory to select by locaiton (interset method) block groups

                print(pid, route)
                bb_output = os.path.join(self.out_gdb, "pid_{}_route_{}_{}_bounding_box".format(pid, route, bounding_box))




                arcpy.MakeFeatureLayer_management(in_features=fc, out_layer="in_memory/temp_points_selections", where_clause=""" "provider_id" = {} and "test_route" = '{}'  """.format(pid, route))



                arcpy.MinimumBoundingGeometry_management(in_features='in_memory/temp_points_selections', out_feature_class="in_memory/{}_bounding_box".format(bounding_box), geometry_type=bounding_box)

                arcpy.SelectLayerByLocation_management(in_layer='block_groups',
                                                       overlap_type="INTERSECT",
                                                       select_features="in_memory/{}_bounding_box".format(bounding_box))

                temp_frames = get_path.pathFinder.fc_2_df('block_groups')
                temp_frames['pid'] = pid
                temp_frames['route'] = route
                selected_df_list.append(temp_frames)
                if not arcpy.Exists(bb_output):

                    arcpy.CopyFeatures_management(in_features="in_memory/{}_bounding_box".format(bounding_box),
                                                  out_feature_class=os.path.join(self.out_gdb,
                                                  "pid_{}_route_{}_{}_bounding_box".format(pid, route, bounding_box)))
                try:
                    arcpy.FeaturesToJSON_conversion(
                        "in_memory/{}_bounding_box".format(bounding_box),
                        os.path.join(self.output_folder,'csv',"{}_bounding_box".format(bounding_box)), geoJSON=True)


                except Exception as e:
                    print(e)
                    arcpy.Delete_management(os.path.join(self.output_folder,'csv',"{}_bounding_box.geojson".format(bounding_box)))

                arcpy.Delete_management('in_memory/{}_bounding_box'.format(bounding_box))
                arcpy.Delete_management("in_memory/temp_points_selections")

            if len(selected_df_list)>0:
                master_df = pd.concat(selected_df_list)

                csv_output = os.path.join(self.output_folder,"csv", "Frames_selected_cbg_by_{}.csv".format(bounding_box))

                arcpy.Delete_management("block_groups")

                master_df.to_csv(csv_output)

    def report(self):
        print("Create Final Report")
        csv_list = get_path.pathFinder(env=self.output_folder).path_grabber(wildcard="Frames*.csv")
        
        csv_df_list = []

        for csv in csv_list:
            print(csv)
            
            df = pd.read_csv(csv, dtype={"STATEFP10": object,
                                         "COUNTYFP10": object,
                                         "TRACTCE10": object,
                                         "GEOID10": object})

            column_name = "GEOID10_{}".format(os.path.basename(csv).strip(".csv"))

            df.rename(columns={"GEOID10": column_name}, inplace=True)

            csv_df_list.append(df.groupby(['pid', 'route'])[column_name].count().reset_index())

        master_df =  reduce(lambda left,right: pd.merge(left,right, on=['pid', 'route'],
                                            how='outer'), csv_df_list)

        master_df.to_csv(os.path.join(self.output_folder, "final_report.csv"))
