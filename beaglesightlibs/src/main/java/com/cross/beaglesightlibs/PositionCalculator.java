package com.cross.beaglesightlibs;

import java.text.DecimalFormat;
import java.util.List;

public abstract class PositionCalculator
{
    List<PositionPair> positions;
    private static DecimalFormat hn = new DecimalFormat("#");
    private static DecimalFormat df = new DecimalFormat("#.##");

	void setPositions(List<PositionPair> pos) {
		positions = pos;
	}

	public abstract float calcPosition(float distance);

	public int precision() {
		switch (positions.size()) {
		case 0:
		case 1:
		case 2:
			return 0;
		default:
			return positions.size()-2;
		}
	}

    public List<PositionPair> getPositions() {
        return positions;
    }
    public static String getDisplayValue(float val, int numPlaces) {
        switch (numPlaces) {
            default:
            case 0:
                return hn.format(val);
            case 2:
                return df.format(val);

        }
    }

    //TODO: Horrifically slow and inaccurate. Replace with optimised version?
    public float getMaxPosition(float distStart, float distEnd)
    {
        float max = Float.MIN_VALUE;
        for (float i = distStart; i < distEnd; i++)
        {
            float val = this.calcPosition(i);
            if (val > max)
            {
                max = val;
            }
        }
        return max;
    }

    //TODO: Horrifically slow and inaccurate. Replace with optimised version?
    public float getMinPosition(float distStart, float distEnd)
    {
        float min = Float.MAX_VALUE;
        for (float i = distStart; i < distEnd; i++)
        {
            float val = this.calcPosition(i);
            if (val < min)
            {
                min = val;
            }
        }
        return min;
    }
}
