package com.cross.beaglesight;

import java.util.Map;
import java.util.Set;
import com.cross.beaglesight.PositionCalculator;



public class BowManager
{
	String currentBow = null;	
	Map<String, BowConfig> bowList = null;
	
	Set<String> getBowNames() {
		return bowList.keySet();
	}
	
	BowManager() {
		
	}
	
	void loadBows() {
		
	}
	
	void saveBows() {
		
	}

	public PositionCalculator getPositionCalculator(String bowName) {
		PositionCalculator pc = new PositionCalculator();
//		pc.addPosition(18, 95);
//		pc.addPosition(20, 95);
//		pc.addPosition(30, 91);
//		pc.addPosition(40, 83);
//		pc.addPosition(50, 73);
		bowList.get(bowName);
		pc.setPositions(bowList.get(bowName).getPositions());
		return pc;
	}

	public String getCurrentPostion() {
		//TODO:
		return "G5-Midas";
	}

	public static BowManager getInstance() {
		// TODO Auto-generated method stub
		return null;
	}
	
}