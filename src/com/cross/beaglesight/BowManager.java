package com.cross.beaglesight;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import com.cross.beaglesight.PositionCalculator;



public class BowManager
{
	private static volatile BowManager instance = null;
	String currentBow = null;	
	Map<String, BowConfig> bowList = null;
	
	Set<String> getBowNames() {
		return bowList.keySet();
	}
	
	BowManager() {
		bowList = new HashMap<String, BowConfig>();
		BowConfig bc = new BowConfig();
		bc.setName("G5-Midas");
		bc.setDescription("This is my G5 bow with the cheap midas sight and vegas optic");
		bc.addPosition(18, 95);
		bc.addPosition(20, 95);
		bc.addPosition(30, 91);
		bc.addPosition(40, 83);
		bc.addPosition(50, 73);
		bowList.put(bc.getName(), bc);
	}
	
	void loadBows() {
		bowList.clear();
		
	}
	
	void saveBows() {
		for (BowConfig bc : bowList) {
			bc.save();
		}
	}

	public PositionCalculator getPositionCalculator(String bowName) {
		PositionCalculator pc = new PositionCalculator();
//		pc.addPosition(18, 95);
//		pc.addPosition(20, 95);
//		pc.addPosition(30, 91);
//		pc.addPosition(40, 83);
//		pc.addPosition(50, 73);
		pc.setPositions(bowList.get(bowName).getPositions());
		return pc;
	}

	public String getCurrentPostion() {
		//TODO:
		return "G5-Midas";
	}

	public static BowManager getInstance() {
	        if (instance == null) {
	            synchronized (BowManager.class) {
	                if (instance == null) {
	                    instance = new BowManager();
	                }
	            }
	        }
	        return instance;
	}
	
}