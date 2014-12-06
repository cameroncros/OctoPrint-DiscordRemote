package com.cross.beaglesight;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;
import org.xmlpull.v1.XmlSerializer;

import android.content.Context;
import android.util.Log;
import android.util.Xml;






import com.cross.beaglesight.PositionCalculator;
import com.cross.beaglesight.gui.MainActivity;



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

	public void loadBows() {
		bowList.clear();
		File[] listOfFiles = folder.listFiles();
		for (File fl : listOfFiles) {
			BowConfig bc = new BowConfig();
			bc.load(fl.getAbsolutePath(), cont);
			bowList.put(bc.getName(), bc);
		}		
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
		PositionCalculator pc = null;
		switch (bowList.get(bowName).getMethod()) {

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
		pc.setPositions(bowList.get(bowName).getPositions());
		return pc;
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

	public Set<String> getBowList() {
		return bowList.keySet();
	}

	public void saveNewBowConfig(BowConfig bc) {
		bowList.put(bc.getName(), bc);
		this.saveBows();
	}

	public void setContext(MainActivity mainActivity) {
		cont = mainActivity;
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