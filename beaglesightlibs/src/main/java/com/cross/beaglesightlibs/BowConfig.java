package com.cross.beaglesightlibs;

import android.util.Log;
import android.util.Xml;

import com.cross.beaglesightlibs.exceptions.InvalidNumberFormatException;

import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;
import org.xmlpull.v1.XmlSerializer;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

public class BowConfig {
    private String id = "";
    private String name = "";
    private String description = "";
    private List<PositionPair> positionArray = new ArrayList<>();
    private PositionCalculator positionCalculator = new LineOfBestFitCalculator();

    public BowConfig(String name, String description) {
        this.id = UUID.randomUUID().toString();
        this.name = name;
        this.description = description;
    }

    public BowConfig(InputStream stream) throws IOException, ParserConfigurationException, SAXException {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        DocumentBuilder db = factory.newDocumentBuilder();
        InputSource inputSource = new InputSource(stream);
        Document document = db.parse(inputSource);

        NodeList nodelist = document.getElementsByTagName("bow");
        for (int i = 0; i < nodelist.getLength(); i++) {
            Node e = nodelist.item(i);
            NodeList children = e.getChildNodes();
            for (int j = 0; j < children.getLength(); j++) {
                Node nd = children.item(j);
                switch (nd.getNodeName()) {
                    case "id":
                        id = nd.getTextContent();
                        break;
                    case "name":
                        name = nd.getTextContent();
                        break;
                    case "description":
                        description = nd.getTextContent();
                        break;
                    case "position":
                        String values = nd.getTextContent();
                        String parts[] = values.split(",");
                        try {
                            PositionPair pair = new PositionPair(parts[0], parts[1]);
                            addPosition(pair);
                        }
                        catch (InvalidNumberFormatException f)
                        {
                            // Do nothing, should never happen
                        }
                        break;
                }
            }
        }
    }

    public void save(OutputStream fileOS) {
        try {
            XmlSerializer serializer = Xml.newSerializer();
            serializer.setOutput(fileOS, "UTF-8");
            serializer.startDocument(null, Boolean.TRUE);
            serializer.setFeature("http://xmlpull.org/v1/doc/features.html#indent-output", true);

            serializer.startTag(null, "bow");
            serializer.startTag(null, "id");
            serializer.text(id);
            serializer.endTag(null, "id");
            serializer.startTag(null, "name");
            serializer.text(name);
            serializer.endTag(null, "name");
            serializer.startTag(null, "description");
            serializer.text(description);
            serializer.endTag(null, "description");

            for (PositionPair pair : positionArray) {
                serializer.startTag(null, "position");
                serializer.text(pair.toString());
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

    public String getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getDescription() {
        return description;
    }

    public void addPosition(PositionPair pair)
    {
        positionArray.add(pair);
        positionCalculator.setPositions(positionArray);
    }

    public PositionCalculator getPositionCalculator() {
        return positionCalculator;
    }

    public List<PositionPair> getPositions() {
        return positionArray;
    }

    public void deletePosition(PositionPair selectedPair) {
        positionArray.remove(selectedPair);
    }
}