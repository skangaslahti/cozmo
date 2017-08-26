#!/usr/bin/env python3

# Copyright (c) 2016 Anki, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''Display a GUI window showing an annotated camera view.

Note:
    This example requires Python to have Tkinter installed to display the GUI.
    It also requires the Pillow and numpy python packages to be pip installed.

The :class:`cozmo.world.World` object collects raw images from Cozmo's camera
and makes them available as a property (:attr:`~cozmo.world.World.latest_image`)
and by generating :class:`cozmo.world.EvtNewCamerImages` events as they come in.

Each image is an instance of :class:`cozmo.world.CameraImage` which provides
access both to the raw camera image, and to a scalable annotated image which
can show where Cozmo sees faces and objects, along with any other information
your program may wish to display.

This example uses the tkviewer to display the annotated camera on the screen
and adds a couple of custom annotations of its own using two different methods.
'''


import sys
import time


try:
    from PIL import ImageDraw, ImageFont
except ImportError:
    sys.exit('run `pip3 install --user Pillow numpy` to run this example')

import cozmo
from cozmo.objects import LightCube1Id, LightCube2Id, LightCube3Id


# Define an annotator using the annotator decorator
@cozmo.annotate.annotator
def clock(image, scale, annotator=None, world=None, **kw):
    d = ImageDraw.Draw(image)
    bounds = (0, 0, image.width, image.height)
    text = cozmo.annotate.ImageText(time.strftime("%H:%m:%S"),
            position=cozmo.annotate.TOP_LEFT)
    text.render(d, bounds)

# Define another decorator as a subclass of Annotator
class Battery(cozmo.annotate.Annotator):
    def apply(self, image, scale):
        d = ImageDraw.Draw(image)
        bounds = (0, 0, image.width, image.height)
        batt = self.world.robot.battery_voltage
        text = cozmo.annotate.ImageText('BATT %.1fv' % batt, color='green')
        text.render(d, bounds)


def cozmo_program(robot: cozmo.robot.Robot):
    robot.world.image_annotator.add_static_text('text', 'Coz-Cam', position=cozmo.annotate.TOP_RIGHT)
    robot.world.image_annotator.add_annotator('clock', clock)
    robot.world.image_annotator.add_annotator('battery', Battery)
    
    
    lookaround = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)

    cubes = robot.world.wait_until_observe_num_objects(num=3, object_type=cozmo.objects.LightCube, timeout=None)
    
    cube1 = robot.world.get_light_cube(LightCube1Id)  # looks like a paperclip
    cube2 = robot.world.get_light_cube(LightCube2Id)  # looks like a lamp / heart
    cube3 = robot.world.get_light_cube(LightCube3Id)
  
    lookaround.stop()
    
    robot.pickup_object(cube3).wait_for_completed()
    d = cozmo.util.Distance(distance_mm = 40)
    robot.place_on_object(cube1).wait_for_completed()
    robot.set_lift_height(height = 0.0, max_speed = 5).wait_for_completed()

    robot.go_to_object(cube1,d).wait_for_completed()
    
    robot.set_lift_height(height = 1.0, max_speed = 5).wait_for_completed()
    
    d2 = cozmo.util.Distance(distance_inches=-2.0)
    d3= cozmo.util.Distance(distance_inches=2.0)
    d4 = cozmo.util.Distance(distance_inches = 3.0)
    s = cozmo.util.Speed(speed_mmps = 10.0)
    robot.drive_straight(d2,s, False).wait_for_completed()
    robot.drive_wheels(10.0, -10.0, duration = 5.0)
    robot.drive_straight(d4,s,False).wait_for_completed()
    robot.drive_wheels(-10.0, 10.0, duration = 5.0)
    robot.drive_straight(d3,s,False).wait_for_completed()
    robot.set_lift_height (height = 0.0).wait_for_completed()
    
    
    # Shutdown the program after 200 seconds
    time.sleep(200)
    


cozmo.run_program(cozmo_program, use_viewer=True, force_viewer_on_top=True)
