package com.cross.beaglesight;

import android.content.Context;
import android.util.Log;
import android.util.Xml;

import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;
import org.xmlpull.v1.XmlSerializer;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.util.HashMap;
import java.util.Map;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

public class BowConfig {
	private String bowname;
    private String bowfilepath;
	private String bowdescription;
	private Map<String, String> positionArray;
	private int method;


	public BowConfig() {
		positionArray = new HashMap<String, String>();
		bowname="";
		bowdescription="";
		method=0;
	}

	public void setName(String name) {
		bowname = name;
	}

	public void setDescription(String description) {
		bowdescription = description;
	}

	public String getName() {
		return bowname;
	}
	public String getDescription() {
		return bowdescription;
	}
    public String getPathToFile() {
        return bowfilepath;
    }

	void clearPositions() {
		positionArray.clear();
	}

	public void addPosition(String distance, String position) 
	{
		positionArray.put(distance, position);
	}

	public Map<String,String> getPositions() {
		return positionArray;
	}

	public void save(String path, Context cont) {
		FileOutputStream fileOS;
		try {
			String filename = path+File.separator+getFileName();
			fileOS = new FileOutputStream(filename,true);
			XmlSerializer serializer = Xml.newSerializer();
			serializer.setOutput(fileOS, "UTF-8");
			serializer.startDocument(null, Boolean.valueOf(true));
			serializer.setFeature("http://xmlpull.org/v1/doc/features.html#indent-output", true);

			serializer.startTag(null, "bow");
			serializer.startTag(null, "name");
			serializer.text(bowname);
			serializer.endTag(null, "name");
			serializer.startTag(null, "description");
			serializer.text(bowdescription);
			serializer.endTag(null, "description");
            serializer.startTag(null, "method");
            serializer.text(Integer.toString(method));
            serializer.endTag(null, "method");

            for (String distance : positionArray.keySet()) {
				serializer.startTag(null, "position");
				serializer.text(distance+","+positionArray.get(distance));
				serializer.endTag(null, "position");
			}
			serializer.endTag(null, "bow");
			serializer.endDocument();
			serializer.flush();
			fileOS.close();


		} catch (Exception e) {
			// TODO Auto-generated catch block
			Log.e("Exception",e.toString());
		}

	}
	
	public void load(String filename, Context cont) {
        bowfilepath = filename;
		FileInputStream fileIS;
		try {
			fileIS = new FileInputStream(filename);
			DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
			DocumentBuilder db = factory.newDocumentBuilder();
			InputSource inputSource = new InputSource(fileIS);
			Document document = db.parse(inputSource);

			NodeList nodelist = document.getElementsByTagName("bow");
			for (int i = 0; i < nodelist.getLength(); i++) {
				Node e = nodelist.item(i);
				NodeList children = e.getChildNodes();
				for (int j = 0; j < children.getLength(); j++) {
					Node nd = children.item(j);
					switch (nd.getNodeName()) {
					case "name":
						setName(nd.getTextContent());
						break;
					case "description":
						setDescription(nd.getTextContent());
						break;
					case "position":
						String values = nd.getTextContent();
						String parts[] = values.split(",");
						addPosition(parts[0], parts[1]);
						break;
					case "method":
						setMethod(Integer.parseInt(nd.getTextContent()));
						break;
					}
				}
			}

		}
		catch (FileNotFoundException f) {
			Log.e("BeagleSight", f.getMessage());
		}
		catch (Exception e) {
			Log.e("BeagleSight", e.getMessage());
		}
	}
	
	public String getFileName() {
		return bowname.replaceAll(" ", "_").concat(".xml");
	}

	public void setMethod(int methodType) {
		// TODO Auto-generated method stub
		method = methodType;
	}

	public int getMethod() {
		// TODO Auto-generated method stub
		return method;
	}
}