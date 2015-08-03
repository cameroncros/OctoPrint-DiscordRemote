package com.cross.beaglesightlibs;

import android.content.Context;
import android.content.pm.PackageManager;
import android.util.Log;

import com.mariux.teleport.lib.TeleportClient;

import java.io.File;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.Vector;


public class BowManager
{
	private static volatile BowManager instance = null;
	Context cont = null;
	Map<String, BowConfig> bowList = null;
	File folder = null;
	private TeleportClient mTeleportClient;



	Set<String> getBowNames() {
		return bowList.keySet();
	}

	BowManager(Context cont) {
		bowList = new HashMap<String, BowConfig>();
		setContext(cont);
	}

	private void loadBows() {
		bowList.clear();
		if (folder != null) {
			File[] listOfFiles = folder.listFiles();
			for (File fl : listOfFiles) {
				BowConfig bc = importBow(fl);
				if (bc != null) {
					bowList.put(bc.getName(), bc);
				}
			}
		}
	}

    public BowConfig importBow(File fl) {
		try {
			BowConfig bc = new BowConfig();
			bc.load(fl);
			return bc;
		} catch (Exception e) {
			Log.e("BeagleSight", e.getMessage());
		}
		return null;
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
			synchronized (BowManager.class) {
				if (instance == null && cont != null) {
					instance = new BowManager(cont);
					instance.loadBows();
				}
			}

		return instance;
	}

	public Vector<String> getBowList() {
		return new Vector<String>(bowList.keySet());
	}

	public void saveBowConfig(BowConfig bc) {
		bowList.put(bc.getName(), bc);
		bc.save(folder.getAbsolutePath(), cont);
		Log.w("BowManager","saved "+bc.getFileName());
		if (!cont.getPackageManager().hasSystemFeature(PackageManager.FEATURE_WATCH))
		{
			mTeleportClient.syncByteArray(bc.getFileName(), bc.toByteArray());
		};
	}

	private void setContext(Context cont) {
		this.cont = cont;
        folder = new File(cont.getFilesDir()+File.separator+"bows"+File.separator);
        if (!folder.exists() && !folder.mkdir()) {
            Log.e("BeagleSight", "Cant create the bow folder or the folder wasnt found");
            folder=null;
        }
		mTeleportClient = new TeleportClient(cont);
		mTeleportClient.connect();
	}

	public void deleteBow(String bowname) {
		File file = new File(getBow(bowname).getPathToFile());
		file.delete();
		Log.w("BowManager", "deleted "+file.getAbsolutePath());
		bowList.remove(bowname);
		// TODO Auto-generated method stub

	}

	public BowConfig getBow(String bowname) throws NullPointerException {
		if (bowname == null) {
			throw new NullPointerException();
		}
		return bowList.get(bowname);
	}

}