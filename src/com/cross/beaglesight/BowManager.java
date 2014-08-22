package com.cross.beaglesight;

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

	Set<String> getBowNames() {
		return bowList.keySet();
	}

	BowManager() {
		bowList = new HashMap<String, BowConfig>();
//		BowConfig bc = new BowConfig();
//		bc.setName("G5-Midas");
//		bc.setDescription("This is my G5 bow with the cheap midas sight and vegas optic");
//		bc.addPosition("18", "95");
//		bc.addPosition("20", "95");
//		bc.addPosition("30", "91");
//		bc.addPosition("40", "83");
//		bc.addPosition("50", "73");
//		bowList.put(bc.getName(), bc);
	}

	public void loadBows() {
		bowList.clear();
		FileInputStream fileIS;
		try {
			fileIS = cont.openFileInput("bows.xml");
			DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
			DocumentBuilder db = factory.newDocumentBuilder();
			InputSource inputSource = new InputSource(fileIS);
            Document document = db.parse(inputSource);
            
            NodeList nodelist = document.getElementsByTagName("bow");
            for (int i = 0; i < nodelist.getLength(); i++) {
            	BowConfig bc = new BowConfig();
            	Node e = nodelist.item(i);
            	NodeList children = e.getChildNodes();
            	for (int j = 0; j < children.getLength(); j++) {
            		Node nd = children.item(j);
            		switch (nd.getNodeName()) {
            		case "name":
            			bc.setName(nd.getTextContent());
            			break;
            		case "description":
            			bc.setDescription(nd.getTextContent());
            			break;
            		case "position":
            			String values = nd.getTextContent();
            			String parts[] = values.split(",");
            			bc.addPosition(parts[0], parts[1]);
            			break;
            		}
            	}
            	bowList.put(bc.getName(), bc);
            }
            
		}
		catch (FileNotFoundException f) {
			saveBows();
			loadBows();
		}
		catch (Exception e) {
			Log.e("BeagleSight", e.getMessage());
		}

	}

	void saveBows() {
		FileOutputStream fileOS;
		try {
			fileOS = cont.openFileOutput("bows.xml", Context.MODE_PRIVATE);
			XmlSerializer serializer = Xml.newSerializer();
			serializer.setOutput(fileOS, "UTF-8");
			serializer.startDocument(null, Boolean.valueOf(true));
			serializer.setFeature("http://xmlpull.org/v1/doc/features.html#indent-output", true);
			serializer.startTag(null, "root");
			for (BowConfig bc : bowList.values()) {
				bc.save(serializer);
			}
			serializer.endTag(null,"root");
			serializer.endDocument();
			serializer.flush();
			fileOS.close();


		} catch (Exception e) {
			// TODO Auto-generated catch block
			Log.e("Exception",e.toString());
		}
	}

	public PositionCalculator getPositionCalculator(String bowName) {
		if (bowName == null) {
			return null;
		}
		PositionCalculator pc = new PositionCalculator();
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