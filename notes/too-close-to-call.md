# Too close to call

Broadcast footage is 25 frames a second. That is one frame every 0.04 s.

SAOT (the Premier League limb system) can split players by about 3 cm. I cannot match that from a TV clip.

How far a player moves in one frame:

- walking (~1.5 m/s) → about 6 cm
- jogging (~4 m/s) → about 16 cm
- sprinting (~8 m/s) → about 32 cm
- a full sprint (~10 m/s) → about 40 cm

Even if the boxes and the pitch map were perfect, a sprinter has already moved ~30 cm between two frames. If I am off by one frame on the kick, that is another 30 cm. Two frames is more like 60–80 cm. 3 cm is not on the table.

On the United–Arsenal 8s clip I now have a detector figure as well. When YOLO and SoccerNet's Mask R-CNN both found the same person, their feet were about **0.3–0.4 m** apart on the pitch (median 0.34 m, mean 0.42 m). That is already the size of one sprint-frame. It is not human ground truth, and the pitch map is messy at the far end of a tight zoom, but it is no longer a guess.

I will treat it as too close to call when the gap is under about **0.4 m** (detector), or about **0.7 m** if I am also not sure which frame the ball was played (detector + one sprint-frame). Misses and extras are outside that number: a dropped far player is worse than 0.4 m.
