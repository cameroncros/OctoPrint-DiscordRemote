package com.cross.beaglesightlibs;

import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public abstract class PositionCalculator
{
	Map<Double,Double> positionArray = null;
    static DecimalFormat hn = new DecimalFormat("#");
    static DecimalFormat df = new DecimalFormat("#.##");
	
	void setPositions(Map<String,String> pos) {
		positionArray.clear();
		for (String key : pos.keySet()) {
			try {
				double x = Double.valueOf(key);
				double y = Double.valueOf(pos.get(key));

				positionArray.put(x, y);
			}
			catch (NumberFormatException e) {
				//Invalid numbers in save file, dont need to do anything but ignore them
			}
		}
	}
	public abstract double calcPosition(double distance);
	public int precision() {
		switch (positionArray.size()) {
		case 0:
		case 1:
		case 2:
			return 0;
		default:
			return positionArray.size()-2;
		}
	}

    public List<Double> getKnownPositions() {
        return new ArrayList<Double>(positionArray.values());
    }

    public List<Double> getKnownDistances() {
        return new ArrayList<Double>(positionArray.keySet());
    }

    public static String getDisplayValue(double val, int numPlaces) {
        switch (numPlaces) {
            default:
            case 0:
                return hn.format(val);
            case 2:
                return df.format(val);

        }
    }
}
