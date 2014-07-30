package com.cross.beaglesight;

import java.util.Map;

public class BowConfig {
	public String bowname;
	public String bowdescription;
	public Map<Double, KnownPosition> positionArray;
	
	class KnownPosition {
		double Distance;
		double Position;
		KnownPosition(double d, double p) {
			Distance=d;
			Position=p;
		}
	}

	BowConfig() {
		
	}
	
	void setName(String name) {
		bowname = name;
	}
	
	void setDescription(String description) {
		bowdescription = description;
	}
	
	String getName() {
		return bowname;
	}
	String getDescription() {
		return bowdescription;
	}
	
	void clearPositions() {
		positionArray = null;
	}
	
	void addPosition(double distance, double position) 
	{
		positionArray.put(distance, new KnownPosition(distance, position));
	}
	
	Map<Double,KnownPosition> getPositions() {
		return positionArray;
	}
}