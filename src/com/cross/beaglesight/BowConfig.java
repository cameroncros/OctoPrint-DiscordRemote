package com.cross.beaglesight;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import org.xmlpull.v1.XmlSerializer;

public class BowConfig {
	private String bowname;
	private String bowdescription;
	private Map<String, String> positionArray;
	private String method;


	public BowConfig() {
		positionArray = new HashMap<String, String>();
		bowname="";
		bowdescription="";
		method="";
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

	public void save(XmlSerializer serializer) throws IllegalArgumentException, IllegalStateException, IOException {
		serializer.startTag(null, "bow");
		serializer.startTag(null, "name");
		serializer.text(bowname);
		serializer.endTag(null, "name");
		serializer.startTag(null, "description");
		serializer.text(bowdescription);
		serializer.endTag(null, "description");
		for (String distance : positionArray.keySet()) {
			serializer.startTag(null, "position");
			serializer.text(distance+","+positionArray.get(distance));
			serializer.endTag(null, "position");
		}
		serializer.endTag(null, "bow");
		
		
		// TODO Auto-generated method stub
		
	}

	public void setMethod(String methodType) {
		// TODO Auto-generated method stub
		method = methodType;
	}

	public String getMethod() {
		// TODO Auto-generated method stub
		return method;
	}
}