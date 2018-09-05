package com.cross.beaglesight;

import android.content.Intent;
import android.util.Log;
import android.widget.Toast;

import com.cross.beaglesightlibs.BowConfig;
import com.cross.beaglesightlibs.BowManager;
import com.google.android.gms.wearable.DataEvent;
import com.google.android.gms.wearable.DataEventBuffer;
import com.google.android.gms.wearable.DataItem;
import com.google.android.gms.wearable.DataMap;
import com.google.android.gms.wearable.DataMapItem;
import com.google.android.gms.wearable.WearableListenerService;

import org.xml.sax.SAXException;

import java.io.ByteArrayInputStream;
import java.io.IOException;

import javax.xml.parsers.ParserConfigurationException;

import static com.cross.beaglesightlibs.BowManager.BOWCONFIGS;

public class ListenerService extends WearableListenerService {
    static final String REFRESH_DATA = "REFRESH_DATA";
    BowManager bowManager;
    public ListenerService() {
        bowManager = BowManager.getInstance(getBaseContext());
        Log.i("BeagleSightWear","Started listener service");
    }

    @Override
    public void onDataChanged(DataEventBuffer dataEvents) {
        for (DataEvent event : dataEvents) {
            if (event.getType() == DataEvent.TYPE_CHANGED) {
                // Remove all bow configs
                for (BowConfig bowConfig : bowManager.getBowList())
                {
                    bowManager.deleteBowConfig(bowConfig.getId());
                }
                // Add back bow configs
                DataItem item = event.getDataItem();
                if (item.getUri().getPath().compareTo(BOWCONFIGS) == 0) {
                    DataMap dataMap = DataMapItem.fromDataItem(item).getDataMap();
                    for (String key : dataMap.keySet())
                    {
                        byte[] bytes = dataMap.getByteArray(key);
                        ByteArrayInputStream bais = new ByteArrayInputStream(bytes);
                        try {
                            BowConfig bc = new BowConfig(bais);
                            bowManager.addBowConfig(bc);
                        } catch (IOException | ParserConfigurationException | SAXException e) {
                            e.printStackTrace();
                        }
                    }
                }
            }
        }

        // Start the sight list activity.

        Intent intent = new Intent(REFRESH_DATA);
        sendBroadcast(intent);
    }
}
