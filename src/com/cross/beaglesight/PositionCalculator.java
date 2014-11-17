package com.cross.beaglesight;

import java.util.Map;

public abstract class PositionCalculator
{
	Map<String,String> positionArray = null;
	
	abstract void setPositions(Map<String,String> pos);
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
