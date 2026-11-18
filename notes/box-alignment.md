# Box alignment (United vs Arsenal, 8s at 10:00)

This game has no SoccerNet tracking/GSR ground truth. What I could pull for this match: event labels, Mask R-CNN player boxes at 2 fps, and field calibration. I lined Roboflow YOLO up against those Mask R-CNN boxes on the same 8 seconds.

Hit = overlap of 0.5 IoU or more. The OpenCV 8s trim is about 10 frames behind the label clock, so I shifted by that before scoring.

On 16 label frames (10:00–10:07.5):

- 157 hits, 65 misses, 120 extras
- hit rate on SoccerNet boxes: **71%**
- mean overlap on hits: 0.69
- mean centre gap on hits: **6.5 pixels**
- using SoccerNet's pitch homography on the feet of those hits: **median 0.34 m, mean 0.42 m, 90th percentile 0.80 m**

YOLO finds extra boxes (crowd, staff, a second box on the same person). Misses are mostly far/small players. When the two boxes are on the same person they sit almost on top of each other.

6.5 px is not one metre value: near the camera a pixel is smaller than far up the pitch, and vertical pixels cost more than horizontal ones. That is why I mapped each pair through the homography instead of multiplying 6.5 by a single scale.

This is YOLO vs Mask R-CNN, not vs a human tracking file. The calibration also drifts at the far end of this tight zoom (a few feet land slightly off the pitch). The number is still good enough to sit next to the 0.3 m fps ceiling.
