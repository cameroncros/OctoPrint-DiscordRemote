package com.cross.beaglesightlibs;

import android.content.Context;
import android.util.Log;

import java.io.File;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;



public class BowManager
{
	private static volatile BowManager instance = null;
	Context cont = null;
	Map<String, BowConfig> bowList = null;
	File folder = null;
	
	Set<String> getBowNames() {
		return bowList.keySet();
	}

	BowManager() {
		bowList = new HashMap<String, BowConfig>();
	}

	private void loadBows() {
		bowList.clear();
		File[] listOfFiles = folder.listFiles();
		for (File fl : listOfFiles) {
            importBow(fl);
		}		
	}

    public void importBow(File fl) {
        BowConfig bc = new BowConfig();
        bc.load(fl, cont);
        bowList.put(bc.getName(), bc);
    }

	void saveBows() {
		File[] listOfFiles = folder.listFiles();
		for (File fl : listOfFiles) {
			fl.delete();
		}
		for (BowConfig bc : bowList.values()) {
			bc.save(folder.getAbsolutePath(), cont);
		}
	}

	public PositionCalculator getPositionCalculator(String bowName) {
		if (bowName == null) {
			return null;
		}
        BowConfig bc = bowList.get(bowName);
        if (bc == null) {
            return null;
        }
		PositionCalculator pc = null;
		switch (bc.getMethod()) {

		case 0:
			pc = new PolynomialCalculator();
			break;
		case 1:
			pc = new LineOfBestFitCalculator(3);
			break;
		case 2:
			pc = new LineOfBestFitCalculator(4);
			break;
		}
		pc.setPositions(bc.getPositions());
		return pc;
	}

	public static BowManager getInstance(Context cont) {
		if (instance == null) {
			synchronized (BowManager.class) {
				if (instance == null) {
					instance = new BowManager();
                    if (cont != null) {
                        instance.setContext(cont);
                        instance.loadBows();
                    }
				}
			}
		}

		return instance;
	}

	public Set<String> getBowList() {
		return bowList.keySet();
	}

	public void saveNewBowConfig(BowConfig bc) {
		bowList.put(bc.getName(), bc);
		this.saveBows();
	}

	public void setContext(Context cont) {
		this.cont = cont;
        folder = new File(cont.getFilesDir()+File.separator+"bows"+File.separator);
        if (!folder.exists() && folder.mkdir()) {
            Log.e("BeagleSight", "Cant create the bow folder or the folder wasnt found");
            folder=null;
        }
	}

	public void deleteBow(String bowname) {
		bowList.remove(bowname);
		saveBows();
		loadBows();
		// TODO Auto-generated method stub

	}

	public BowConfig getBow(String bowname) throws NullPointerException {
		if (bowname == null) {
			throw new NullPointerException();
		}
		return bowList.get(bowname);
	}

}