package com.cross.beaglesight;

import java.util.Map;

public abstract class PositionCalculator
{
	Map<Double,Double> positionArray = null;
	
	void setPositions(Map<String,String> pos) {
		positionArray.clear();
		for (String key : pos.keySet()) {
			double x = Double.valueOf(key);
			double y = Double.valueOf(pos.get(key));
			positionArray.put(x, y);
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
}
