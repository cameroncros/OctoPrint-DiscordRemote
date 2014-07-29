package com.cross.beaglesight;

public class BowManager
{
	
	
	class KnownPosition {
		double Distance;
		double Position;
		KnownPosition(double d, double p) {
			Distance=d;
			Position=p;
		}
	}

	
	
	class BowConfig {
		String bowname;
		String bowdescription;
		Map<Double,KnownPosition> positionArray = null;	
	}

	String currentBow = null;	
	Map<String, BowConfig> bowList = null;
	
	Vector<String> getBowNames() {
		return bowList.
	}
	
}