package com.cross.beaglesight;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import org.xmlpull.v1.XmlSerializer;

public class BowConfig {
	public String bowname;
	public String bowdescription;
	public Map<String, KnownPosition> positionArray;
	
	class KnownPosition {
		String Distance;
		String Position;
		KnownPosition(String d, String p) {
			Distance=d;
			Position=p;
		}
	}

	BowConfig() {
		positionArray = new HashMap<String, KnownPosition>();
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
	
	void addPosition(String distance, String position) 
	{
		positionArray.put(distance, new KnownPosition(distance, position));
	}
	
	Map<String,KnownPosition> getPositions() {
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
		for (KnownPosition kp : positionArray.values()) {
			serializer.startTag(null, "position");
			serializer.text(kp.Distance+","+kp.Position);
			serializer.endTag(null, "position");
		}
		serializer.endTag(null, "bow");
		
		
		// TODO Auto-generated method stub
		
	}
}