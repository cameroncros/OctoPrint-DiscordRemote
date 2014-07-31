package com.cross.beaglesight;

import java.util.HashMap;
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
		positionArray = new HashMap<Double, KnownPosition>();
		bowname="";
		bowdescription="";
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
		positionArray.clear();
	}
	
	void addPosition(double distance, double position) 
	{
		positionArray.put(distance, new KnownPosition(distance, position));
	}
	
	Map<Double,KnownPosition> getPositions() {
		return positionArray;
	}

	public void save() {
		// TODO Auto-generated method stub
		
	}
}