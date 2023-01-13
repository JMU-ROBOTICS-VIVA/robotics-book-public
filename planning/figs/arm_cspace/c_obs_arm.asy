

real l1 = 100.0;
real l2 = 100.0;
real segWidth = 10;

path obs1 = box((100, 100), (150, 170));
path obs2 = box((-100, 100), (-80, 120));

// point is a point on segment on of the arm, this returns
// the location of that point in world coords.
pair segOneToWorld(real theta1,  pair point) {
  return rotate(theta1) * point;
}

pair segTwoToWorld(real theta1, real theta2, pair point) {
  return rotate(theta1) * shift(l1, 0) * rotate(theta2) * point;
}

path segOnePath(real theta1) {
  pair ll_seg1 = (-segWidth, -segWidth);
  pair ul_seg1 = (-segWidth, segWidth);
  pair ur_seg1 = (l1 + segWidth, segWidth);
  pair lr_seg1 = (l1 + segWidth, -segWidth);
  return segOneToWorld(theta1, ll_seg1) --
    segOneToWorld(theta1, ul_seg1) --
    segOneToWorld(theta1, ur_seg1) --
    segOneToWorld(theta1, lr_seg1)-- cycle;
  
}

path segTwoPath(real theta1, real theta2) {
  pair ll_seg2 = (-segWidth, -segWidth);
  pair ul_seg2 = (-segWidth, segWidth);
  pair ur_seg2 = (l2 - segWidth, segWidth);
  pair lr_seg2 = (l2 - segWidth, -segWidth);
  return segTwoToWorld(theta1, theta2, ll_seg2) --
    segTwoToWorld(theta1, theta2, ul_seg2) --
    segTwoToWorld(theta1, theta2, ur_seg2) --
    segTwoToWorld(theta1, theta2, lr_seg2)-- cycle;

}

pair[] collisionPoints(path obstacle) {
  pair[] result;
  for (real theta1 = 0; theta1 < 360.0; theta1 += 2) {
    for (real theta2 = 0; theta2 < 360.0; theta2 += 2) {
      path segOnePath = segOnePath(theta1);
      path segTwoPath = segTwoPath(theta1, theta2);
      if ((intersect(segOnePath, obstacle).length > 0) ||
	  (intersect(segTwoPath, obstacle).length > 0))
	result.push((theta1, theta2));
    }
  }
  return result;
}


picture armPic(real theta1, real theta2) {
  picture pic;

  filldraw(pic, obs1, mediumgray);
  filldraw(pic, obs2, mediumgray);
  
  path segOnePath = segOnePath(theta1);

  path segTwoPath = segTwoPath(theta2, theta2);

  filldraw(pic, segOnePath, mediumgray);
  filldraw(pic, segTwoPath, mediumgray);

  dot(pic, (0,0));

  dot(pic, segTwoToWorld(theta1, theta2, (0,0)));
  return pic;
}

void COBSFigure() {

  pair[] obs1Hits = collisionPoints(obs1);
  pair[] obs2Hits = collisionPoints(obs2);
  draw(obs1Hits, mediumgray);
  draw(obs2Hits, red);
  dot((0,0), invisible);
  dot((360, 360), invisible);
}

add(armPic(45, 45));
shipout("arm_world", format="pdf");

erase();
COBSFigure();
shipout("arm_cobs", format="pdf");
