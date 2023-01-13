//https://tex.stackexchange.com/questions/249659/how-to-center-a-label-inside-a-closed-path-in-asymptote


pair[] pairsFromPath(path pairs)
{
  pair[] all;
  for (int i = 0; i < size(pairs); ++i) {
    all.push(point(pairs, i));
    write(i);
  }
  return all;
}

pair[] a = pairsFromPath((10, 11) -- (12, 13) -- cycle);
write(a);



path convexHull(pair[] in_pset)
{
    pair[] pset = copy(in_pset);

    if (pset.length == 0) { path hull; return hull; }

    { // remove duplicate points
        int indexDelete = 1;
        while (indexDelete > 0)
        {
            indexDelete = -1;
            for (int i = 1; i < pset.length; ++i)
            {
                for (int j = 0; j < i; ++j)
                {
                    if (pset[i] == pset[j])
                    {
                        indexDelete = i;
                        break;
                    }
                }
                if (indexDelete > 0) { break; }
            }
            if (indexDelete > 0) { pset.delete(indexDelete); }
        }
    }

    path hull;

    { // add point at min y (and min x if tie) to hull, delete point from pset
        int minIndex = 0;

        for (int i = 1; i < pset.length; ++i)
        {
            if (pset[i].y < pset[minIndex].y ||
                    (pset[i].y == pset[minIndex].y && pset[i].x < pset[minIndex].x))
            {
                minIndex = i;
            }
        }
        hull = pset[minIndex];
        pset.delete(minIndex);
    }

    while (pset.length > 0)
    {
        { // add next point to hull
            real minAngle = 361.0;
            int minAngleIndex = 0;
            for (int i = 0; i < pset.length; ++i)
            {
                real angle = degrees(pset[i] - relpoint(hull, 1.0), false);
                if (angle < minAngle)
                {
                    minAngle = angle;
                    minAngleIndex = i;
                }
            }
            hull = hull--pset[minAngleIndex];
            pset.delete(minAngleIndex);
        }

        { // remove points interior to current hull from pset
            path tempHull = hull--cycle;
            int[] deleteIndeces;
            for (int i = pset.length - 1; i > -1; --i)
            {
                if (inside(tempHull, pset[i])) { deleteIndeces.push(i); }
            }
            for (int i = 0; i < deleteIndeces.length; ++i)
            {
                pset.delete(deleteIndeces[i]);
            }
        }
    }
    return hull--cycle;
}

path convexHull(path all_pairs)
{
  return convexHull(pairsFromPath(all_pairs));
}
